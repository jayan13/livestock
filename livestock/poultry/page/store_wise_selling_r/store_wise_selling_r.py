import frappe
from frappe.utils import getdate,add_days,get_first_day,get_last_day,nowdate,flt,date_diff

@frappe.whitelist()
def get_report(company,store):
    html=''
    items=frappe.db.get_all("Item",filters={'item_group':'EGGS','item_code':['NOT in',['ORG EGG','ORG EGG BROWN']]},fields=['item_code'],order_by='item_code',pluck='item_code')
    items_str="','".join(items)
    
    posted_on=getdate(nowdate())
    sl_entrys=frappe.db.get_all('Bin',filters={'warehouse':store,'item_code':['in',items]},fields=['actual_qty as qty','item_code'])
    
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
        if not qty:
            continue
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
                AND MONTH(s.posting_date) = MONTH(DATE_SUB('{1}', INTERVAL 1 MONTH)) and YEAR(s.posting_date) = YEAR('{1}') 
                AND si.item_code in ('{2}')
                AND si.item_code not in ('ORG1115','ORG1130')
                and si.warehouse = '{3}'
            """.format(company,posted_on,items_str,store),as_dict=1,debug=0)
    if sl_curmonth_bf:        
        befthis_qty=sl_curmonth_bf[0].qty
        prev_mth_sale=sl_curmonth_bf[0].amount
        if prev_mth_sale:
            prev_mth_avg_sale=prev_mth_sale/befthis_qty
            prev_mth_avg_sale=f"{prev_mth_avg_sale:.12f}"

    

#-------------------------------------------------
    sl_curmonth_dis= frappe.db.sql("""
            SELECT
                IFNULL(sum(total),0) as amt
            FROM
                `tabSales Invoice` s
            WHERE
                s.company = '{0}'
                and s.status not in ('Draft','Cancelled')                
                AND s.docstatus = 1 
                and s.is_return=1
                and s.customer in ('{2}') 
                and s.naming_series in ('DISCOUNT-.####','BUSINESS-PROMO-.####')
                AND MONTH(s.posting_date) = MONTH(DATE_SUB('{1}', INTERVAL 1 MONTH)) and YEAR(s.posting_date) = YEAR('{1}') 
                
            """.format(company,posted_on,customersal),as_dict=1,debug=0)
    avg_dis_last=0   
    avg_dis_sale=0     
    if sl_curmonth_dis:
        if sl_curmonth_dis[0].amt:
            avg_dis_last=sl_curmonth_dis[0].amt/befthis_qty
            avg_dis_last=f"{avg_dis_last:.12f}"  
            avg_dis_sale=(prev_mth_sale+sl_curmonth_dis[0].amt)/befthis_qty

    sl_curyear_bf= frappe.db.sql("""
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
                AND MONTH(s.posting_date) < MONTH('{1}') and YEAR(s.posting_date) = YEAR('{1}') 
                AND si.item_code in ('{2}')
                AND si.item_code not in ('ORG1115','ORG1130')
                and si.warehouse = '{3}'
            """.format(company,posted_on,items_str,store),as_dict=1,debug=0)

    
    if sl_curyear_bf:
        befyear_qty=sl_curyear_bf[0].qty
        befyear_amt=sl_curyear_bf[0].amount

    sl_curyear_dis= frappe.db.sql("""
            SELECT
                IFNULL(sum(total),0) as amt
            FROM
                `tabSales Invoice` s
            WHERE
                s.company = '{0}'
                and s.status not in ('Draft','Cancelled')                
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
            avg_disy_sale=(befyear_amt+sl_curyear_dis[0].amt)/befyear_qty

    html+='<tr><td>Sales</td><td class="text-right">'+str(frappe.utils.fmt_money(flt(today_sale,4)))+'</td><td  class="text-right">'+str(frappe.utils.fmt_money(flt(this_sale,4)))+'</td><td class="text-right">'+str(frappe.utils.fmt_money(flt(prev_mth_sale,4)))+'</td><td  class="text-right">'+str(frappe.utils.fmt_money(flt(year_sale,4)))+'</td></tr>'
    html+='<tr><td>Average Selling Price</td><td class="text-right">'+str(avgtoday_sale)+'</td><td  class="text-right">'+str(avgthis_sale)+'</td><td class="text-right">'+str(frappe.utils.fmt_money(flt(prev_mth_avg_sale,4)))+'</td><td  class="text-right">'+str(avgyear_sale)+'</td></tr>'
    
    html+='<tr><td>Average Discount till Prev month</td><td class="text-right"></td><td></td><td  class="text-right">'+str(avg_dis_last)+'</td><td  class="text-right">'+str(avg_dis_year)+'</td></tr>'
    html+='<tr><td>Avg SP after discount</td><td class="text-right"></td><td></td><td  class="text-right">'+str(avg_dis_sale)+'</td><td  class="text-right">'+str(avg_disy_sale)+'</td></tr>'

    html+='</table>'

    out_standing=frappe.db.sql(""" select party,sum(debit) as debit,sum(credit) as credit,(sum(debit)-sum(credit)) as balance from `tabGL Entry`
                where company='{0}' 
                and party_type='Customer'
                and (posting_date <='{1}' or is_opening = 'Yes') 
                and is_cancelled = 0
                and party in ('{2}')
                group by party order by balance desc """.format(company,posted_on,customersal),as_dict=1,debug=0)
    
    
    outstand=0
    retn=0
    balout=0
    
    for cus in out_standing:
        outstand+=cus.debit
        retn+=cus.credit
        balout+=cus.balance
        
    html+='<div class="rephd">Outstanding Amount &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; </div>' 
    html+='<table class="table table-bordered" >'
    html+='<tr class="table-secondary"><th style="width: 300px;">Customer</th><th class="text-right">Debit</th><th class="text-right">Credit</th><th class="text-right">Balance Outstanding</th></tr>'
    html+='<tr><td>Total Outstanding</td><td class="text-right"><b>'+str(frappe.utils.fmt_money(flt(outstand,4)))+'</b></td><td  class="text-right"><b>'+str(frappe.utils.fmt_money(flt(retn,4)))+'</b></td><td  class="text-right"><b>'+str(frappe.utils.fmt_money(flt(outstand-retn,4)))+'</b></td></tr>'
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
    html+='<tr class="table-secondary"><th style="width: 600px;">Customer</th><th class="text-right">Debit</th><th class="text-right">Credit</th><th class="text-right">Balance Outstanding</th></tr>'
    for cs in out_standing:
        html+='<tr><td>'+str(cs.party)+'</td><td class="text-right">'+str(frappe.utils.fmt_money(flt(cs.debit,4)))+'</td><td  class="text-right">'+str(frappe.utils.fmt_money(flt(cs.credit,4)))+'</td><td  class="text-right">'+str(frappe.utils.fmt_money(flt(cs.balance,4)))+'</td></tr>'
    
    html+='<tr><td>Total</td><td class="text-right"><b>'+str(frappe.utils.fmt_money(flt(outstand,4)))+'</b></td><td  class="text-right"><b>'+str(frappe.utils.fmt_money(flt(retn,4)))+'</b></td><td  class="text-right"><b>'+str(frappe.utils.fmt_money(flt(balout,4)))+'</b></td></tr>'
    html+='</table>'
    #----------------------------------------------------------
    setting=frappe.db.get_value("Store Performance Report Setting",{'company':company,'store':store},['cost_center','name'], as_dict=1)
    if setting:
        exptot=0
        html+='<div class="rephd">Expenses &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; </div>' 
        html+='<table class="table table-bordered" >'
        html+='<tr class="table-secondary"><th style="width: 600px;">Expense</th><th class="text-right">Today</th><th class="text-right">MTD</th><th class="text-right">YTD</th></tr>'
        
        cost_center=setting.cost_center.replace("'", "\\'")
        vehicle_maintenance=get_accounts(setting.name,'vehicle_maintenance')
        petty_cash_expenses=get_accounts(setting.name,'petty_cash_expenses')
        vehicle_str="','".join(vehicle_maintenance)
        petty_str="','".join(petty_cash_expenses)
        
        vehsql=frappe.db.sql(""" select account, sum(debit) as debit,sum(credit) as credit,sum(debit-credit) as exp
            from `tabGL Entry`
            where company='{0}' 
            and account in ('{3}') 
            and cost_center ='{2}' 
            and posting_date ='{1}'  
            and is_cancelled = 0 group by account
            """.format(company,posted_on,cost_center,vehicle_str),as_dict=1,debug=0)

        vehsqlm=frappe.db.sql(""" select account, sum(debit) as debit,sum(credit) as credit,sum(debit-credit) as exp
            from `tabGL Entry`
            where company='{0}' 
            and account in ('{3}') 
            and cost_center ='{2}' 
            AND MONTH(posting_date) = MONTH('{1}') and YEAR(posting_date) = YEAR('{1}') 
            and is_cancelled = 0 group by account
            """.format(company,posted_on,cost_center,vehicle_str),as_dict=1,debug=0)

        vehsqly=frappe.db.sql(""" select account, sum(debit) as debit,sum(credit) as credit,sum(debit-credit) as exp
            from `tabGL Entry`
            where company='{0}' 
            and account in ('{3}') 
            and cost_center ='{2}' 
            AND YEAR(posting_date) = YEAR('{1}')
            and is_cancelled = 0 group by account
            """.format(company,posted_on,cost_center,vehicle_str),as_dict=1,debug=0)
        if vehicle_maintenance:
            for vm in vehicle_maintenance:
                flg=1
                html2='<tr><td>'+str(vm)+'</td>'

                if vehsql:
                    v=0
                    for vv in vehsql:
                        if vm==vv.account:
                            v=vv.exp
                            if vv.exp != 0:
                                flg=1
                    html2+='<td class="text-right">'+str(frappe.utils.fmt_money(v))+'</td>'
                else:
                    html2+='<td class="text-right">0</td>'

                if vehsqlm:
                    v=0
                    for vv in vehsqlm:
                        if vm==vv.account:
                            v=vv.exp
                            if vv.exp != 0:
                                flg=1
                    html2+='<td class="text-right">'+str(frappe.utils.fmt_money(v))+'</td>'
                else:
                    html2+='<td class="text-right">0</td>'

                if vehsqly:
                    v=0
                    for vv in vehsqly:
                        if vm==vv.account:
                            v=vv.exp
                            if vv.exp != 0:
                                flg=1
                    html2+='<td class="text-right">'+str(frappe.utils.fmt_money(v))+'</td>'
                else:
                    html2+='<td class="text-right">0</td>'

                html2+='</tr>'
                if flg==1:
                    html+=html2

        #----------------------------------------------------------
        petsql=frappe.db.sql(""" select account, sum(debit) as debit,sum(credit) as credit,sum(debit-credit) as exp
            from `tabGL Entry`
            where company='{0}' 
            and account in ('{3}') 
            and cost_center ='{2}' 
            and posting_date ='{1}'  
            and is_cancelled = 0 group by account
            """.format(company,posted_on,cost_center,petty_str),as_dict=1,debug=0)

        petsqlm=frappe.db.sql(""" select account, sum(debit) as debit,sum(credit) as credit,sum(debit-credit) as exp
            from `tabGL Entry`
            where company='{0}' 
            and account in ('{3}') 
            and cost_center ='{2}' 
            AND MONTH(posting_date) = MONTH('{1}') and YEAR(posting_date) = YEAR('{1}') 
            and is_cancelled = 0 group by account
            """.format(company,posted_on,cost_center,petty_str),as_dict=1,debug=0)

        petsqly=frappe.db.sql(""" select account, sum(debit) as debit,sum(credit) as credit,sum(debit-credit) as exp
            from `tabGL Entry`
            where company='{0}' 
            and account in ('{3}') 
            and cost_center ='{2}' 
            AND YEAR(posting_date) = YEAR('{1}')
            and is_cancelled = 0 group by account
            """.format(company,posted_on,cost_center,petty_str),as_dict=1,debug=1)
        #frappe.msgprint(str(petsqly))
        if petty_cash_expenses:
            for ptty in petty_cash_expenses:
                flg=0
                html2='<tr><td>'+str(ptty)+'-hh</td>'

                if petsql:
                    v=0
                    for vv in petsql:
                        if ptty==vv.account:
                            v=vv.exp
                            if vv.exp != 0:
                                flg=1
                    html2+='<td class="text-right">'+str(frappe.utils.fmt_money(v))+'</td>'
                else:
                    html2+='<td class="text-right">0</td>'

                if petsqlm:
                    v=0
                    for vv in petsqlm:
                        if ptty==vv.account:
                            v=vv.exp
                            if vv.exp != 0:
                                flg=1
                    html2+='<td class="text-right">'+str(frappe.utils.fmt_money(v))+'</td>'
                else:
                    html2+='<td class="text-right">0</td>'

                if petsqly:
                    v=0
                    for vv in petsqly:
                        if ptty==vv.account:
                            v=vv.exp
                            if vv.exp != 0:
                                flg=1
                    html2+='<td class="text-right">'+str(frappe.utils.fmt_money(v))+'</td>'
                else:
                    html2+='<td class="text-right">0</td>'

                html2+='</tr>'
                
                if flg==1:
                    html+=html2

        html+='</table>'    
    return html
def get_accounts(parent,parentfield):
    acc=[]
    acsql=frappe.db.sql(""" select ex.account,a.is_group from `tabExpense Accounts` ex 
        left join `tabAccount` a on a.name=ex.account 
                where ex.parent='{0}' and ex.parentfield='{1}' """.format(parent,parentfield),as_dict=1,debug=0)
    if acsql:
        for ac in acsql:
            if ac.is_group:
                acc=acc+get_child_acc(ac.account)
            else:
                acc.append(ac.account.replace("'", "\\'"))
    return acc

def get_child_acc(account):
    accc=[]
    acsql=frappe.db.sql(""" select name,is_group from  `tabAccount` where parent_account='{0}' """.format(account),as_dict=1,debug=0)
    if acsql:
        for ac in acsql:
            if ac.is_group:
                accc=accc+get_child_acc(ac.name)
            else:
                accc.append(ac.name.replace("'", "\\'"))
    return accc


def getitem_name(item_code):
    return frappe.db.get_value('Item',item_code,'item_name')

def Sort(sub_li):
 
    # reverse = None (Sorts in Ascending order)
    # key is set to sort using second element of
    # sublist lambda has been used
    sub_li.sort(key = lambda x: x[1],reverse=1)
    return sub_li

def get_item_ctn_qty(item_code,stock_qty):
    ctnqty=0   
    cv=frappe.db.get_value('UOM Conversion Detail', {'parent': item_code,'uom':'Ctn'}, 'conversion_factor', as_dict=1,debug=0)
    if stock_qty>0:
        ctnqty=round(stock_qty/cv.conversion_factor,2)
        
    return ctnqty