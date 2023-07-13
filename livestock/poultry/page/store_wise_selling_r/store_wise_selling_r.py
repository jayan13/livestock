import frappe
from frappe.utils import getdate,add_days,get_first_day,get_last_day,nowdate,flt,date_diff
@frappe.whitelist()

@frappe.whitelist()
def get_report(company,store):
    html=''
    items=frappe.db.get_all("Item",filters={'item_group':'EGGS','item_code':['NOT in',['ORG EGG','ORG EGG BROWN']]},fields=['item_code'],order_by='item_code',pluck='item_code')
    items_str="','".join(items)
    
    posted_on=getdate(nowdate())
    sl_entrys= frappe.db.sql("""
            SELECT
                sum(actual_qty) as qty,item_code
            FROM
                `tabStock Ledger Entry` 
            WHERE
                company = '{0}' 
                and actual_qty > 0 
                and voucher_type='Stock Entry'
                AND is_cancelled = 0 
                AND posting_date < '{1}'
                AND item_code in ('{2}')
                and warehouse = '{3}'
            GROUP BY
                item_code
            """.format(company,posted_on,items_str,store),as_dict=1,debug=0)
    
    custsql=frappe.db.sql("""
            SELECT
                DISTINCT customer
            FROM
                `tabSales Invoice` s
                left join `tabSales Invoice Item` si on si.parent=s.name
            WHERE
                s.company = '{0}'
                and s.is_return!=1                
                AND si.item_code in ('{2}')
                and si.warehouse = '{3}' order by customer
            """.format(company,posted_on,items_str,store),as_dict=1,debug=0)
            #AND YEAR(s.posting_date) = YEAR('{1}') 
    customer=[]
    if custsql:
        for cu in custsql:
            customer.append(cu.customer.replace("'", "\\'"))
        
    customersal="','".join(customer)

    html+='<div class="rephd">Stock in Hand: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Store : '+str(store)+' </div>' 
    html+='<table class="table table-bordered" id="prod">'
    html+='<tr class="table-secondary"><th style="width: 300px;">Items </th><th class="text-right">Qty In Ctn</th></tr>'
    total_ctn=0
    for ent in sl_entrys:
        qty=flt(ent.qty/360,3)
        total_ctn+=qty
        html+='<tr><td>'+str(getitem_name(ent.item_code))+'</td><td class="text-right">'+str(frappe.utils.fmt_money(flt(qty,3)))+'</td></tr>'

    html+='<tr><td>Total</td><td class="text-right"><b>'+str(frappe.utils.fmt_money(flt(total_ctn,3)))+'</b></td></tr>'
    html+='</table>'

    html+='<div class="rephd">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; </div>' 
    html+='<table class="table table-bordered" >'
    html+='<tr class="table-secondary"><th style="width: 300px;"></th><th class="text-right">Today</th><th class="text-right">MTD</th><th class="text-right">Prev Month</th><th class="text-right">YTD</th></tr>'
    
    today_qty=0
    this_qty=0
    year_qty=0

    today_amt=0
    this_amt=0
    year_amt=0

    today_qty_org=0
    this_qty_org=0
    year_qty_org=0

    today_amt_org=0
    this_amt_org=0
    year_amt_org=0

    today_sale=0
    this_sale=0
    year_sale=0

    avgtoday_sale=0
    avgthis_sale=0
    avgyear_sale=0

    sl_today= frappe.db.sql("""
            SELECT
                IFNULL(sum(si.base_amount),0) as amount,IFNULL(sum(si.stock_qty),0) as qty,si.item_code
            FROM
                `tabSales Invoice` s
                left join `tabSales Invoice Item` si on si.parent=s.name
            WHERE
                s.company = '{0}'
                and s.status not in ('Draft','Return','Cancelled')                
                AND s.docstatus = 1
                and s.is_return!=1  
                AND s.posting_date = '{1}'
                AND si.item_code in ('{2}')
                and si.warehouse = '{3}' 
                GROUP BY si.item_code
            """.format(company,posted_on,items_str,store),as_dict=1,debug=0)

    if sl_today:
        for sl in sl_today:
            if sl.item_code not in ['ORG1115','ORG1130']:
                today_qty+=sl.qty
                today_amt+=sl.amount
            else:
                today_qty_org+=sl.qty
                today_amt_org+=sl.amount

        if today_amt:
            avgtoday_sale=today_amt/today_qty

        today_sale=today_amt

    sl_curmonth= frappe.db.sql("""
            SELECT
                IFNULL(sum(si.base_amount),0) as amount,IFNULL(sum(si.stock_qty),0) as qty,si.item_code
            FROM
                `tabSales Invoice` s
                left join `tabSales Invoice Item` si on si.parent=s.name
            WHERE
                s.company = '{0}'
                and s.status not in ('Draft','Return','Cancelled')                
                AND s.docstatus = 1 
                and s.is_return!=1 
                AND MONTH(s.posting_date) = MONTH('{1}') and YEAR(s.posting_date) = YEAR('{1}') 
                AND si.item_code in ('{2}')
                and si.warehouse = '{3}'
                GROUP BY si.item_code
            """.format(company,posted_on,items_str,store),as_dict=1,debug=0)
    if sl_curmonth:
        for sl in sl_curmonth:
            if sl.item_code not in ['ORG1115','ORG1130']:
                this_qty+=sl.qty
                this_amt+=sl.amount
            else:
                this_qty_org+=sl.qty
                this_amt_org+=sl.amount

        this_sale=this_amt
        if this_amt:
            avgthis_sale=this_amt/this_qty
        

    sl_curyear= frappe.db.sql("""
            SELECT
                IFNULL(sum(si.base_amount),0) as amount,IFNULL(sum(si.stock_qty),0) as qty,si.item_code
            FROM
                `tabSales Invoice` s
                left join `tabSales Invoice Item` si on si.parent=s.name
            WHERE
                s.company = '{0}'
                and s.status not in ('Draft','Return','Cancelled')                
                AND s.docstatus = 1
                and s.is_return!=1 
                AND YEAR(s.posting_date) = YEAR('{1}') 
                AND si.item_code in ('{2}')
                and si.warehouse = '{3}'
                GROUP BY si.item_code
            """.format(company,posted_on,items_str,store),as_dict=1,debug=0)
    if sl_curyear:
        for sl in sl_curyear:
            if sl.item_code not in ['ORG1115','ORG1130']:
                year_qty+=sl.qty
                year_amt+=sl.amount
            else:
                year_qty_org+=sl.qty
                year_amt_org+=sl.amount

        year_sale=year_amt

        if year_amt:
            avgyear_sale=year_amt/year_qty
        
    #------------------------------------------------
    befthis_qty=0
    befyear_qty=0
    prev_mth_sale=0
    prev_mth_avg_sale=0
    sl_curmonth_bf= frappe.db.sql("""
            SELECT
                IFNULL(sum(si.base_amount),0) as amount,IFNULL(sum(si.stock_qty),0) as qty
            FROM
                `tabSales Invoice` s
                left join `tabSales Invoice Item` si on si.parent=s.name
            WHERE
                s.company = '{0}'
                and s.status not in ('Draft','Return','Cancelled')                
                AND s.docstatus = 1 
                and s.is_return!=1 
                AND MONTH(s.posting_date) = MONTH(DATE_SUB('{1}', INTERVAL -1 MONTH)) and YEAR(s.posting_date) = YEAR('{1}') 
                AND si.item_code in ('{2}')
                and si.warehouse = '{3}'
            """.format(company,posted_on,items_str,store),as_dict=1,debug=0)
    if sl_curmonth_bf:        
        befthis_qty=sl_curmonth_bf[0].qty
        prev_mth_sale=sl_curmonth_bf[0].amount
        if prev_mth_sale:
            prev_mth_avg_sale=prev_mth_sale/befthis_qty
            prev_mth_avg_sale=f"{prev_mth_avg_sale:.12f}"

    sl_curyear_bf= frappe.db.sql("""
            SELECT
                IFNULL(sum(si.stock_qty),0) as qty
            FROM
                `tabSales Invoice` s
                left join `tabSales Invoice Item` si on si.parent=s.name
            WHERE
                s.company = '{0}'
                and s.status not in ('Draft','Return','Cancelled')                
                AND s.docstatus = 1
                and s.is_return!=1 
                AND MONTH(s.posting_date) < MONTH('{1}') and YEAR(s.posting_date) = YEAR('{1}') 
                AND si.item_code in ('{2}')
                and si.warehouse = '{3}'
            """.format(company,posted_on,items_str,store),as_dict=1,debug=0)

    
    if sl_curyear_bf:
        befyear_qty=sl_curyear_bf[0].qty

#-------------------------------------------------
    sl_curmonth_dis= frappe.db.sql("""
            SELECT
                IFNULL(sum(total),0) as amt
            FROM
                `tabSales Invoice` s
            WHERE
                s.company = '{0}'
                and s.status not in ('Draft','Return','Cancelled')                
                AND s.docstatus = 1 
                and s.is_return=1
                and s.customer in ('{2}') 
                and s.naming_series in ('DISCOUNT-.####','BUSINESS-PROMO-.####')
                AND MONTH(s.posting_date) = MONTH(DATE_SUB('{1}', INTERVAL -1 MONTH)) and YEAR(s.posting_date) = YEAR('{1}') 
                
            """.format(company,posted_on,customersal),as_dict=1,debug=0)
    avg_dis_last=0   
    avg_dis_sale=0     
    if sl_curmonth_dis:
        if sl_curmonth_dis[0].amt:
            avg_dis_last=sl_curmonth_dis[0].amt/befthis_qty
            avg_dis_last=f"{avg_dis_last:.12f}"  
            avg_dis_sale=(this_amt+sl_curmonth_dis[0].amt)/befthis_qty

    sl_curyear_dis= frappe.db.sql("""
            SELECT
                IFNULL(sum(total),0) as amt
            FROM
                `tabSales Invoice` s
            WHERE
                s.company = '{0}'
                and s.status not in ('Draft','Return','Cancelled')                
                AND s.docstatus = 1
                and s.is_return=1
                and s.customer in ('{2}')
                and s.naming_series in ('DISCOUNT-.####','BUSINESS-PROMO-.####') 
                AND MONTH(s.posting_date) < MONTH('{1}') and YEAR(s.posting_date) = YEAR('{1}') 
            """.format(company,posted_on,customersal),as_dict=1,debug=0)

    avg_dis_year=0
    avg_disy_sale=0
    if sl_curyear_dis:
        if sl_curyear_dis[0].amt:            
            avg_dis_year=float(sl_curyear_dis[0].amt)/float(befyear_qty)
            avg_dis_year=f"{avg_dis_year:.12f}"            
            avg_disy_sale=(year_amt+sl_curyear_dis[0].amt)/befyear_qty

    html+='<tr><td>Sales</td><td class="text-right">'+str(frappe.utils.fmt_money(flt(today_sale,4)))+'</td><td  class="text-right">'+str(frappe.utils.fmt_money(flt(this_sale,4)))+'</td><td class="text-right">'+str(frappe.utils.fmt_money(flt(prev_mth_sale,4)))+'</td><td  class="text-right">'+str(frappe.utils.fmt_money(flt(year_sale,4)))+'</td></tr>'
    html+='<tr><td>Average Selling Price</td><td class="text-right">'+str(avgtoday_sale)+'</td><td  class="text-right">'+str(avgthis_sale)+'</td><td class="text-right">'+str(frappe.utils.fmt_money(flt(prev_mth_avg_sale,4)))+'</td><td  class="text-right">'+str(avgyear_sale)+'</td></tr>'
    
    html+='<tr><td>Average Discount till Prev month</td><td class="text-right"></td><td></td><td  class="text-right">'+str(avg_dis_last)+'</td><td  class="text-right">'+str(avg_dis_year)+'</td></tr>'
    html+='<tr><td>Avg SP after discount</td><td class="text-right"></td><td></td><td  class="text-right">'+str(avg_dis_sale)+'</td><td  class="text-right">'+str(avg_disy_sale)+'</td></tr>'

    html+='</table>'

    

    out_standing= frappe.db.sql("""
            SELECT sum(ot.outstanding_amount) as outstanding_amount,ot.customer from (
            SELECT
                s.outstanding_amount as outstanding_amount,s.customer as customer
            FROM
                `tabSales Invoice` s
                left join `tabSales Invoice Item` si on si.parent=s.name
            WHERE
                s.company = '{0}'
                and s.status not in ('Draft','Paid','Cancelled')                
                AND s.docstatus = 1
                and s.is_return!=1 
                AND si.item_code in ('{2}')
                and si.warehouse = '{3}' 
                GROUP BY s.name ) as ot group by ot.customer
            """.format(company,posted_on,items_str,store),as_dict=1,debug=0)
            # AND YEAR(s.posting_date) = YEAR('{1}')
    
    out_standing_ret=frappe.db.sql("""
            SELECT
                sum(outstanding_amount) as outstanding_amount,customer
            FROM
                `tabSales Invoice` where
                company = '{0}'                              
                AND docstatus = 1
                and is_return=1
                and outstanding_amount < 0  
                and customer in ('{2}')
                group by customer
                """.format(company,posted_on,customersal),as_dict=1,debug=0)
                #and naming_series not in ('DISCOUNT-.####','BUSINESS-PROMO-.####')  AND YEAR(posting_date) = YEAR('{1}')
    
    outstand=0
    retn=0
    cus_rows=[]
    for cus in customer:
        flg=0
        row=[cus,0,0,0]
        if out_standing:
            for ot in out_standing:
                if cus==ot.customer:
                    outstand+=ot.outstanding_amount
                    row[1]=ot.outstanding_amount
                    flg=1

        if out_standing_ret:
            for re in out_standing_ret:
                if cus==re.customer:
                    retn+=re.outstanding_amount
                    row[2]=re.outstanding_amount
                    flg=1

        if flg==1:
            row[3]=row[1]+row[2]
            cus_rows.append(row)
    cus_rows=Sort(cus_rows)
    html+='<div class="rephd">Outstanding Amount &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; </div>' 
    html+='<table class="table table-bordered" >'
    html+='<tr class="table-secondary"><th style="width: 300px;">Customer</th><th class="text-right">Outstanding</th><th class="text-right">Credit Note</th><th class="text-right">Balance Outstanding</th></tr>'
    html+='<tr><td>Total Outstanding</td><td class="text-right"><b>'+str(frappe.utils.fmt_money(flt(outstand,4)))+'</b></td><td  class="text-right"><b>'+str(frappe.utils.fmt_money(flt(retn,4)))+'</b></td><td  class="text-right"><b>'+str(frappe.utils.fmt_money(flt(outstand+retn,4)))+'</b></td></tr>'
    html+='</table>'

    html+='<div class="rephd">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; </div>' 
    html+='<table class="table table-bordered" >'
    html+='<tr class="table-secondary"><th style="width: 300px;">Average Selling Price - Breakup</th><th class="text-right">Today</th><th class="text-right">MTD</th><th class="text-right">YTD</th></tr>'
    
    avg_selling_d=0
    avg_selling_m=0
    avg_selling_y=0
    item_cnt_d=0
    item_cnt_m=0
    item_cnt_y=0

    for itm in items:
        davg=0
        mavg=0
        yavg=0

        if itm in ['ORG1115','ORG1130']:
            continue

        for sl1 in sl_today:
            if sl1.amount:
                if itm==sl1.item_code:
                    davg=sl1.amount/sl1.qty
                    item_cnt_d+=1
                    avg_selling_d+=davg

        for sl2 in sl_curmonth:
            if sl2.amount:
                if itm==sl2.item_code:
                    mavg=sl2.amount/sl2.qty
                    item_cnt_m+=1
                    avg_selling_m+=mavg

        for sl3 in sl_curyear:
            if sl3.amount:
                if itm==sl3.item_code:
                    yavg=sl3.amount/sl3.qty
                    item_cnt_y+=1
                    avg_selling_y+=yavg

        if davg or mavg or yavg:            
            html+='<tr><td>'+str(getitem_name(itm))+'</td><td class="text-right">'+str(flt(davg,4))+'</td><td  class="text-right">'+str(flt(mavg,4))+'</td><td  class="text-right">'+str(flt(yavg,4))+'</td></tr>'

    avg_d=0
    if avg_selling_d:
        avg_d=avg_selling_d/item_cnt_d

    avg_m=0
    if avg_selling_m:
        avg_m=avg_selling_m/item_cnt_m

    avg_y=0
    if avg_selling_y:
        avg_y=avg_selling_y/item_cnt_y


    html+='<tr><td>Accumulated AVG</td><td class="text-right"><b>'+str(flt(avg_d,4))+'</b></td><td  class="text-right"><b>'+str(flt(avg_m,4))+'</b></td><td  class="text-right"><b>'+str(flt(avg_y,4))+'</b></td></tr>'
            
    html+='</table>'

    html+='<div class="rephd">Organic &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; </div>' 
    html+='<table class="table table-bordered" >'
    html+='<tr class="table-secondary"><th style="width: 300px;"></th><th class="text-right">Today</th><th class="text-right">MTD</th><th class="text-right">YTD</th></tr>'
    html+='<tr><td>Sales</td><td class="text-right">'+str(frappe.utils.fmt_money(flt(today_amt_org,4)))+'</td><td  class="text-right">'+str(frappe.utils.fmt_money(flt(this_amt_org,4)))+'</td><td  class="text-right">'+str(frappe.utils.fmt_money(flt(year_amt_org,4)))+'</td></tr>'
    avgtoday_sale_org=0
    if today_amt_org:
        avgtoday_sale_org=today_amt_org/today_qty_org

    avgthis_sale_org=0
    if this_amt_org:
        avgthis_sale_org=this_amt_org/this_qty_org

    avgyear_sale_org=0
    if year_amt_org:
        avgyear_sale_org=year_amt_org/year_qty_org

    html+='<tr><td>Average Selling Price</td><td class="text-right">'+str(avgtoday_sale_org)+'</td><td  class="text-right">'+str(avgthis_sale_org)+'</td><td  class="text-right">'+str(avgyear_sale_org)+'</td></tr>'
    html+='</table>'

    html+='<div class="rephd">Organic &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; </div>' 
    html+='<table class="table table-bordered" >'
    html+='<tr class="table-secondary"><th style="width: 300px;">Average Selling Price - Breakup</th><th class="text-right">Today</th><th class="text-right">MTD</th><th class="text-right">YTD</th></tr>'
    
    avg_selling_d=0
    avg_selling_m=0
    avg_selling_y=0
    item_cnt_d=0
    item_cnt_m=0
    item_cnt_y=0

    for itm in items:
        davg=0
        mavg=0
        yavg=0

        if itm not in ['ORG1115','ORG1130']:
            continue

        for sl1 in sl_today:
            if sl1.amount:
                if itm==sl1.item_code:
                    davg=sl1.amount/sl1.qty
                    item_cnt_d+=1
                    avg_selling_d+=davg

        for sl2 in sl_curmonth:
            if sl2.amount:
                if itm==sl2.item_code:
                    mavg=sl2.amount/sl2.qty
                    item_cnt_m+=1
                    avg_selling_m+=mavg

        for sl3 in sl_curyear:
            if sl3.amount:
                if itm==sl3.item_code:
                    yavg=sl3.amount/sl3.qty
                    item_cnt_y+=1
                    avg_selling_y+=yavg

        if davg or mavg or yavg:    
            html+='<tr><td>'+str(getitem_name(itm))+'</td><td class="text-right">'+str(flt(davg,4))+'</td><td  class="text-right">'+str(flt(mavg,4))+'</td><td  class="text-right">'+str(flt(yavg,4))+'</td></tr>'

    avg_d=0
    if avg_selling_d:
        avg_d=avg_selling_d/item_cnt_d

    avg_m=0
    if avg_selling_m:
        avg_m=avg_selling_m/item_cnt_m

    avg_y=0
    if avg_selling_y:
        avg_y=avg_selling_y/item_cnt_y        

    html+='<tr><td>Accumulated AVG</td><td class="text-right"><b>'+str(flt(avg_d,4))+'</b></td><td  class="text-right"><b>'+str(flt(avg_m,4))+'</b></td><td  class="text-right"><b>'+str(flt(avg_y,4))+'</b></td></tr>'
    html+='</table>'

    html+='<div class="rephd">Customer Outstanding Amount &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; </div>' 
    html+='<table class="table table-bordered" >'
    html+='<tr class="table-secondary"><th style="width: 600px;">Customer</th><th class="text-right">Outstanding</th><th class="text-right">Credit Note</th><th class="text-right">Balance Outstanding</th></tr>'
    for cs in cus_rows:
        html+='<tr><td>'+str(cs[0])+'</td><td class="text-right">'+str(frappe.utils.fmt_money(flt(cs[1],4)))+'</td><td  class="text-right">'+str(frappe.utils.fmt_money(flt(cs[2],4)))+'</td><td  class="text-right">'+str(frappe.utils.fmt_money(flt(cs[3],4)))+'</td></tr>'
    
    html+='<tr><td>Total</td><td class="text-right"><b>'+str(frappe.utils.fmt_money(flt(outstand,4)))+'</b></td><td  class="text-right"><b>'+str(frappe.utils.fmt_money(flt(retn,4)))+'</b></td><td  class="text-right"><b>'+str(frappe.utils.fmt_money(flt(outstand+retn,4)))+'</b></td></tr>'
    html+='</table>'
    
    return html

def getitem_name(item_code):
    return frappe.db.get_value('Item',item_code,'item_name')

def Sort(sub_li):
 
    # reverse = None (Sorts in Ascending order)
    # key is set to sort using second element of
    # sublist lambda has been used
    sub_li.sort(key = lambda x: x[1],reverse=1)
    return sub_li

