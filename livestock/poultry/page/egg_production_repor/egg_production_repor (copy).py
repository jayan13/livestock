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

    items=frappe.db.get_all("Item",filters={'item_group':'EGGS','item_code':['NOT in',['ORG1115','ORG1130']]},fields=['item_code','item_name'],order_by='item_code')
    html=''
    html+='<div id="rephd">Production: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;From Date: '+str(frappe.utils.formatdate(date_from))+' To Date : '+str(frappe.utils.formatdate(date_to))+'</div>' 
    html+='<table class="table table-bordered" id="prod">'
    proddatetot=[]
    if date_range:
        html+='<tr class="table-secondary"><th>Items </th>'
        for dr in date_range:
            html+='<th>'+str(frappe.utils.formatdate(dr.get('from'), "MMM yy"))+'(Qty in Ctn)</th>'
            proddatetot.append(0)
        html+='</tr>'
        if items:
            for itm in items:
                html+='<tr>'
                html+='<td>'+str(itm.item_code)+'</td>'
                d=0
                i=0
                for dr in date_range:
                    #if itm.item_code=='CG11111':
                     #   d=1
                    itmqty=frappe.db.sql(""" SELECT sum(qty*conversion_factor) as qty
                    FROM `tabStock Entry Detail`
                    JOIN `tabStock Entry` on `tabStock Entry Detail`.parent = `tabStock Entry`.name
                    WHERE
                    `tabStock Entry`.docstatus=1
                    AND  `tabStock Entry Detail`.item_code='{0}'
                    AND `tabStock Entry Detail`.is_finished_item = 1
                    AND `tabStock Entry`.stock_entry_type = 'Manufacture'
                    AND `tabStock Entry`.manufacturing_type = 'Egg'
                    AND `tabStock Entry`.company = '{1}'
                    AND `tabStock Entry`.posting_date between '{2}' 
                    AND '{3}'
                    GROUP BY `tabStock Entry Detail`.item_code """.format(itm.item_code,company,dr.get('from'),dr.get('to')),as_dict=1,debug=d)
                    qtyinctn=0
                    if itmqty:                        
                        if itmqty[0].qty:
                            qtyinctn=float(itmqty[0].qty)/360
                        html+='<td class="text-right">'+str(flt(qtyinctn,3))+'</td>'
                    else:
                        html+='<td class="text-right">0</td>'

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
    items=frappe.db.get_all("Item",filters={'item_group':'EGGS','item_code':['NOT in',['ORG EGG','ORG EGG BROWN']]},fields=['item_code','item_name'],order_by='item_code')
    html+='<div id="rephd">Sales: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;From Date: '+str(frappe.utils.formatdate(date_from))+' To Date : '+str(frappe.utils.formatdate(date_to))+'</div>' 
    html+='<table class="table table-bordered" >'
    saleqtytot=[]
    saleamttot=[]
    if date_range:
        html+='<tr class="table-secondary"><th rowspan="2">Items </th>'
        for dr in date_range:
            html+='<th colspan="2">'+str(frappe.utils.formatdate(dr.get('from'), "MMM yy"))+'</th>'
            saleqtytot.append(0)
            saleamttot.append(0)
        html+='</tr>'

        html+='<tr class="table-secondary">'
        for dr in date_range:
            html+='<th>Qty</th><th>Amount</th>'            
        html+='</tr>'

        if items:
            for itm in items:
                html+='<tr>'
                html+='<td>'+str(itm.item_code)+'</td>'
                d=0
                i=0
                for dr in date_range:
                    #if itm.item_code=='CG11111':
                     #   d=1
                    itmqty=frappe.db.sql(""" SELECT ROUND(sum(`tabSales Invoice Item`.base_net_amount),2) as amt,sum(qty*conversion_factor) as qty
                    FROM `tabSales Invoice`
                    JOIN `tabSales Invoice Item` on `tabSales Invoice Item`.parent = `tabSales Invoice`.name
                    WHERE `tabSales Invoice`.docstatus=1
                    AND `tabSales Invoice`.is_return!=1
                    AND `tabSales Invoice Item`.item_code ='{0}'
                    AND `tabSales Invoice`.company = '{1}'
                    AND `tabSales Invoice`.posting_date between '{2}' AND '{3}'
                    GROUP BY `tabSales Invoice Item`.item_code """.format(itm.item_code,company,dr.get('from'),dr.get('to')),as_dict=1,debug=d)
                    qtyinctn=0
                    sval=0
                    if itmqty:                        
                        if itmqty[0].qty:
                            qtyinctn=float(itmqty[0].qty)/360
                        html+='<td class="text-right">'+str(flt(qtyinctn,3))+'</td>'
                        if itmqty[0].amt:
                            sval=itmqty[0].amt
                        html+='<td class="text-right">'+str(sval)+'</td>'
                    else:
                        html+='<td class="text-right">0</td><td class="text-right">0</td>'

                    tot=saleqtytot[i]
                    saleqtytot[i]=float(tot)+float(qtyinctn)
                    tots=saleamttot[i]
                    saleamttot[i]=float(tots)+float(sval)    
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

    #================== sales ===========
    html+='<div id="rephd">Sales Return: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;From Date: '+str(frappe.utils.formatdate(date_from))+' To Date : '+str(frappe.utils.formatdate(date_to))+'</div>' 
    html+='<table class="table table-bordered" >'
    saleqtytot=[]
    saleamttot=[]
    if date_range:
        html+='<tr class="table-secondary"><th rowspan="2">Items </th>'
        for dr in date_range:
            html+='<th colspan="2">'+str(frappe.utils.formatdate(dr.get('from'), "MMM yy"))+'</th>'
            saleqtytot.append(0)
            saleamttot.append(0)
        html+='</tr>'

        html+='<tr class="table-secondary">'
        for dr in date_range:
            html+='<th>Qty</th><th>Amount</th>'            
        html+='</tr>'

        if items:
            for itm in items:
                html+='<tr>'
                html+='<td>'+str(itm.item_code)+'</td>'
                d=0
                i=0
                for dr in date_range:
                    #if itm.item_code=='CG11111':
                     #   d=1
                    itmqty=frappe.db.sql(""" SELECT ROUND(sum(`tabSales Invoice Item`.base_net_amount),2) as amt,sum(qty*conversion_factor) as qty
                    FROM `tabSales Invoice`
                    JOIN `tabSales Invoice Item` on `tabSales Invoice Item`.parent = `tabSales Invoice`.name
                    WHERE `tabSales Invoice`.docstatus=1
                    AND `tabSales Invoice`.is_return=1
                    AND `tabSales Invoice Item`.item_code ='{0}'
                    AND `tabSales Invoice`.company = '{1}'
                    AND `tabSales Invoice`.posting_date between '{2}' AND '{3}'
                    GROUP BY `tabSales Invoice Item`.item_code """.format(itm.item_code,company,dr.get('from'),dr.get('to')),as_dict=1,debug=d)
                    qtyinctn=0
                    sval=0
                    if itmqty:                        
                        if itmqty[0].qty:
                            qtyinctn=float(itmqty[0].qty)/360
                        html+='<td class="text-right">'+str(flt(qtyinctn,3))+'</td>'
                        if itmqty[0].amt:
                            sval=itmqty[0].amt
                        html+='<td class="text-right">'+str(sval)+'</td>'
                    else:
                        html+='<td class="text-right">0</td><td class="text-right">0</td>'

                    tot=saleqtytot[i]
                    saleqtytot[i]=float(tot)+float(qtyinctn)
                    tots=saleamttot[i]
                    saleamttot[i]=float(tots)+float(sval)    
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


