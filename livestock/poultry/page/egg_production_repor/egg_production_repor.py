import frappe
from frappe.utils import getdate,add_days,get_first_day,get_last_day,nowdate,flt,date_diff
@frappe.whitelist()
def get_company_list():
    data = {}
    data["companys"] = frappe.get_list("Company", fields=['name'],limit_page_length=0, order_by="name",debug=0)
    return data

@frappe.whitelist()
def get_report(company,date_from,date_to):
    date_from=getdate(date_from)
    date_to=getdate(date_to)
    date_range=[]
    items=frappe.db.get_all("Item",filters={'item_group':'EGGS','item_code':['NOT in',['ORG1115','ORG1130']]},fields=['item_code'],order_by='item_code',pluck='item_code')
    items_str="','".join(items)
    itemss=frappe.db.get_all("Item",filters={'item_group':'EGGS','item_code':['NOT in',['ORG EGG','ORG EGG BROWN']]},fields=['item_code'],order_by='item_code',pluck='item_code')
    itemss_str="','".join(itemss)

    cnt=0
    day = date_from
    while day < date_to:
        if cnt > 60:
            break

        if frappe.utils.formatdate(day, "MMM yy")!=frappe.utils.formatdate(date_to, "MMM yy"):
            to=get_last_day(getdate(day))
            date_range.append({'from':day,'to':to})
            day=add_days(to,1)
        else:
            date_range.append({'from':day,'to':date_to})
            day=date_to
        cnt+=1

    
    html=''
    html+='<div id="rephd">Production: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;From Date: '+str(frappe.utils.formatdate(date_from))+' To Date : '+str(frappe.utils.formatdate(date_to))+'</div>' 
    html+='<table class="table table-bordered" id="prod">'
    proddatetot=[]
    range_res=[]
    if date_range:
        html+='<tr class="table-secondary"><th>Items </th>'
        for dr in date_range:
            html+='<th>'+str(frappe.utils.formatdate(dr.get('from'), "MMM yy"))+'(Qty in Ctn)</th>'
            proddatetot.append(0)
            resprd=frappe.db.sql(""" SELECT sum(qty*conversion_factor) as qty,`tabStock Entry Detail`.item_code 
                    FROM `tabStock Entry Detail`
                    JOIN `tabStock Entry` on `tabStock Entry Detail`.parent = `tabStock Entry`.name
                    WHERE
                    `tabStock Entry`.docstatus=1
                    AND  `tabStock Entry Detail`.item_code in ('{0}')
                    AND `tabStock Entry Detail`.is_finished_item = 1
                    AND `tabStock Entry`.stock_entry_type = 'Manufacture'
                    AND `tabStock Entry`.manufacturing_type = 'Egg'
                    AND `tabStock Entry`.company = '{1}'
                    AND `tabStock Entry`.posting_date between '{2}' 
                    AND '{3}'
                    GROUP BY `tabStock Entry Detail`.item_code """.format(items_str,company,dr.get('from'),dr.get('to')),as_dict=1,debug=0)
            range_res.append(resprd)
        html+='</tr>'
        if items:
            for itm in items:
                html+='<tr>'
                html+='<td>'+str(itm)+'</td>'
                d=0
                i=0
                for dr in date_range:
                    #if itm.item_code=='CG11111':
                     #   d=1
                    qtyinctn=0
                    itmqty=range_res[i]
                    if itmqty:
                        for it in itmqty:
                            if itm==it.item_code:
                                if it.qty:
                                    qtyinctn=float(it.qty)/360

                    html+='<td class="text-right">'+str(flt(qtyinctn,3))+'</td>'

                    tot=proddatetot[i]
                    proddatetot[i]=float(tot)+float(qtyinctn)    
                    i+=1
                html+='</tr>'
            html+='<tr class="table-secondary"><th>Total</th>'
            for total in proddatetot:
                 html+='<th class="text-right"><b>'+str(flt(total,3))+'</b></th>'
            html+='</tr>'
    html+='</table>'
    #================== sales ===========
    
    html+='<div id="rephd">Sales: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;From Date: '+str(frappe.utils.formatdate(date_from))+' To Date : '+str(frappe.utils.formatdate(date_to))+'</div>' 
    html+='<table class="table table-bordered" >'
    saleqtytot=[]
    saleamttot=[]
    range_ress=[]
    if date_range:
        html+='<tr class="table-secondary"><th rowspan="2">Items </th>'
        for dr in date_range:
            html+='<th colspan="2">'+str(frappe.utils.formatdate(dr.get('from'), "MMM yy"))+'</th>'
            saleqtytot.append(0)
            saleamttot.append(0)
            ressale=frappe.db.sql(""" SELECT `tabSales Invoice Item`.item_code,ROUND(sum(`tabSales Invoice Item`.base_net_amount),2) as amt,sum(qty*conversion_factor) as qty
                    FROM `tabSales Invoice`
                    JOIN `tabSales Invoice Item` on `tabSales Invoice Item`.parent = `tabSales Invoice`.name
                    WHERE `tabSales Invoice`.docstatus=1
                    AND `tabSales Invoice`.is_return!=1
                    AND `tabSales Invoice Item`.item_code in('{0}')
                    AND `tabSales Invoice`.company = '{1}'
                    AND `tabSales Invoice`.posting_date between '{2}' AND '{3}'
                    GROUP BY `tabSales Invoice Item`.item_code """.format(itemss_str,company,dr.get('from'),dr.get('to')),as_dict=1,debug=0)
            range_ress.append(ressale)
        html+='</tr>'

        html+='<tr class="table-secondary">'
        for dr in date_range:
            html+='<th>Qty</th><th>Amount</th>'            
        html+='</tr>'

        if itemss:
            for itm in itemss:
                html+='<tr>'
                html+='<td>'+str(itm)+'</td>'
                d=0
                i=0
                for dr in date_range:
                    #if itm.item_code=='CG11111':
                     #   d=1
                    
                    qtyinctn=0
                    amount=0
                    itmqty=range_ress[i]
                    if itmqty:
                        for it in itmqty:
                            if itm==it.item_code:
                                if it.qty:
                                    qtyinctn=float(it.qty)/360
                                amount=it.amt
                    html+='<td class="text-right">'+str(flt(qtyinctn,3))+'</td>'
                    html+='<td class="text-right">'+str(amount)+'</td>'
                    

                    tot=saleqtytot[i]
                    saleqtytot[i]=float(tot)+float(qtyinctn)
                    tots=saleamttot[i]
                    saleamttot[i]=float(tots)+float(amount)    
                    i+=1
                html+='</tr>'
            html+='<tr class="table-secondary"><th>Total</th>'
            j=0
            for total in saleqtytot:
                 html+='<th class="text-right"><b>'+str(flt(total,3))+'</b></th>'
                 html+='<th class="text-right"><b>'+str(flt(saleamttot[j],3))+'</b></th>'
                 j+=1
            html+='</tr>'
        
    html+='</table>'

    #================== sales return ===========
    html+='<div id="rephd">Sales Return: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;From Date: '+str(frappe.utils.formatdate(date_from))+' To Date : '+str(frappe.utils.formatdate(date_to))+'</div>' 
    html+='<table class="table table-bordered" >'
    saleqtytot=[]
    saleamttot=[]
    range_ressr=[]
    if date_range:
        html+='<tr class="table-secondary"><th rowspan="2">Items </th>'
        for dr in date_range:
            html+='<th colspan="2">'+str(frappe.utils.formatdate(dr.get('from'), "MMM yy"))+'</th>'
            ressaler=frappe.db.sql(""" SELECT `tabSales Invoice Item`.item_code,ROUND(sum(`tabSales Invoice Item`.base_net_amount),2) as amt,sum(qty*conversion_factor) as qty
                    FROM `tabSales Invoice`
                    JOIN `tabSales Invoice Item` on `tabSales Invoice Item`.parent = `tabSales Invoice`.name
                    WHERE `tabSales Invoice`.docstatus=1
                    AND `tabSales Invoice`.is_return=1
                    AND `tabSales Invoice Item`.item_code in ('{0}')
                    AND `tabSales Invoice`.company = '{1}'
                    AND `tabSales Invoice`.posting_date between '{2}' AND '{3}'
                    GROUP BY `tabSales Invoice Item`.item_code """.format(itemss_str,company,dr.get('from'),dr.get('to')),as_dict=1,debug=0)
            saleqtytot.append(0)
            saleamttot.append(0)
            range_ressr.append(ressaler)
        html+='</tr>'

        html+='<tr class="table-secondary">'
        for dr in date_range:
            html+='<th>Qty</th><th>Amount</th>'            
        html+='</tr>'

        if itemss:
            for itm in itemss:
                html+='<tr>'
                html+='<td>'+str(itm)+'</td>'
                d=0
                i=0
                for dr in date_range:
                    #if itm.item_code=='CG11111':
                     #   d=1
                    
                    qtyinctn=0
                    amount=0
                    itmqty=range_ressr[i]
                    if itmqty:
                        for it in itmqty:
                            if itm==it.item_code:
                                if it.qty:
                                    qtyinctn=float(it.qty)/360
                                amount=it.amt
                    html+='<td class="text-right">'+str(flt(qtyinctn,3))+'</td>'
                    html+='<td class="text-right">'+str(amount)+'</td>'

                    tot=saleqtytot[i]
                    saleqtytot[i]=float(tot)+float(qtyinctn)
                    tots=saleamttot[i]
                    saleamttot[i]=float(tots)+float(amount)    
                    i+=1
                html+='</tr>'
            html+='<tr class="table-secondary"><th>Total</th>'
            j=0
            for total in saleqtytot:
                 html+='<th class="text-right"><b>'+str(flt(total,3))+'</b></th>'
                 html+='<th class="text-right"><b>'+str(flt(saleamttot[j],3))+'</b></th>'
                 j+=1
            html+='</tr>'
        
    html+='</table>'

    return html

def getitem_name(item_code):
    return frappe.db.get_value('Item',item_code,'item_name')


