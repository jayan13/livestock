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
    date_range=[] #['ORG1115','ORG1130'] ['ORG EGG','ORG EGG BROWN']
    items=frappe.db.get_all("Item",filters={'item_group':'EGGS','item_code':['NOT in',['ORG EGG','ORG EGG BROWN']]},fields=['item_code'],order_by='item_code',pluck='item_code')
    items_str="','".join(items)
    itemss=items
    itemss_str=items_str

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
    html+='<div class="rephd">Production: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;From Date: '+str(frappe.utils.formatdate(date_from))+' To Date : '+str(frappe.utils.formatdate(date_to))+'</div>' 
    html+='<div class="scrl" ><table class="table table-bordered" id="prod">'
    proddatetot=[]
    range_res=[]
    if date_range:
        html+='<tr class="table-secondary"><th style="width: 225px;">Items </th>'
        for dr in date_range:
            html+='<th style="text-align:center;font-weight:bold">'+str(frappe.utils.formatdate(dr.get('from'), "MMM yy"))+'(Qty in Ctn)</th>'
            proddatetot.append(0)
            resprd=frappe.db.sql(""" SELECT sum(qty*conversion_factor) as qty,`tabStock Entry Detail`.item_code 
                    FROM `tabStock Entry Detail`
                    JOIN `tabStock Entry` on `tabStock Entry Detail`.parent = `tabStock Entry`.name
                    WHERE
                    `tabStock Entry`.docstatus=1
                    AND  `tabStock Entry Detail`.item_code in ('{0}')
                    AND ((`tabStock Entry Detail`.is_finished_item = 1
                    AND `tabStock Entry`.stock_entry_type = 'Manufacture'
                    AND `tabStock Entry`.manufacturing_type in ('Egg','Egg Packing') ) or (`tabStock Entry`.stock_entry_type = 'Material Receipt' AND `tabStock Entry`.stock_entry_type_option='Production') )
                    AND `tabStock Entry`.company = '{1}'
                    AND `tabStock Entry`.posting_date between '{2}' 
                    AND '{3}'
                    GROUP BY `tabStock Entry Detail`.item_code """.format(items_str,company,dr.get('from'),dr.get('to')),as_dict=1,debug=0)
            range_res.append(resprd)
        html+='</tr>'
        if items:
            for itm in items:
                html+='<tr>'
                html+='<td>'+str(getitem_name(itm))+'</td>'
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

                    html+='<td class="text-right">'+str(frappe.utils.fmt_money(flt(qtyinctn,3)))+'</td>'

                    tot=proddatetot[i]
                    proddatetot[i]=float(tot)+float(qtyinctn)    
                    i+=1
                html+='</tr>'

            html+='<tr class="table-secondary"><th>Total</th>'
            for total in proddatetot:
                 html+='<th class="text-right"><b>'+str(frappe.utils.fmt_money(flt(total,3)))+'</b></th>'
            html+='</tr>'
    html+='</table></div>'
    #================== sales ===========
    
    html+='<div class="rephd">Sales: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;From Date: '+str(frappe.utils.formatdate(date_from))+' To Date : '+str(frappe.utils.formatdate(date_to))+'</div>' 
    html+='<div class="scrl" ><table class="table table-bordered" >'
    saleqtytot=[]
    saleamttot=[]
    salerqtytot=[]
    saleramttot=[]
    range_ress=[]
    range_ressr=[]
    netqty_tot=[]
    netsale_tot=[]
    if date_range:
        html+='<tr class="table-secondary"><th rowspan="2" style="width: 225px;">Items </th>'
        for dr in date_range:
            html+='<th colspan="6" style="text-align:center;font-weight:bold">'+str(frappe.utils.formatdate(dr.get('from'), "MMM yy"))+'</th>'
            saleqtytot.append(0)
            saleamttot.append(0)
            salerqtytot.append(0)
            saleramttot.append(0)
            netqty_tot.append(0)
            netsale_tot.append(0)
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
            ressaler=frappe.db.sql(""" SELECT `tabSales Invoice Item`.item_code,ROUND(sum(`tabSales Invoice Item`.base_net_amount),2) as amt,sum(qty*conversion_factor) as qty
                    FROM `tabSales Invoice`
                    JOIN `tabSales Invoice Item` on `tabSales Invoice Item`.parent = `tabSales Invoice`.name
                    WHERE `tabSales Invoice`.docstatus=1
                    AND `tabSales Invoice`.is_return=1
                    AND `tabSales Invoice Item`.item_code in ('{0}')
                    AND `tabSales Invoice`.company = '{1}'
                    AND `tabSales Invoice`.posting_date between '{2}' AND '{3}'
                    GROUP BY `tabSales Invoice Item`.item_code """.format(itemss_str,company,dr.get('from'),dr.get('to')),as_dict=1,debug=0)
            range_ressr.append(ressaler)
        html+='</tr>'

        html+='<tr class="table-secondary">'
        for dr in date_range:
            html+='<th style="position: unset;font-weight:normal;">Qty</th><th>Amount</th><th>Rtn Qty</th><th>Rtn Amount</th><th>Net Qty</th><th>Net Amt</th>'            
        html+='</tr>'

        if itemss:
            for itm in itemss:
                html+='<tr>'
                html+='<td>'+str(getitem_name(itm))+'</td>'
                d=0
                i=0
                for dr in date_range:
                    #if itm.item_code=='CG11111':
                     #   d=1
                    if ((i+1) % 2) == 0:                        
                        sty=' style="background-color: #f3faff; border: 1px solid #ccc;" '
                        
                        
                    else:                        
                        sty=' style=" border: 1px solid #ccc;" '

                    qtyinctn=0
                    amount=0
                    itmqty=range_ress[i]
                    if itmqty:
                        for it in itmqty:
                            if itm==it.item_code:
                                if it.qty:
                                    qtyinctn=float(it.qty)/360
                                amount=it.amt
                    html+='<td class="text-right" '+str(sty)+'>'+str(frappe.utils.fmt_money(flt(qtyinctn,3)))+'</td>'
                    html+='<td class="text-right" '+str(sty)+'>'+str(frappe.utils.fmt_money(amount))+'</td>'

                    srqty=0
                    srval=0  
                    salret=range_ressr[i]
                    if salret:
                        for ret in salret:
                            if itm==ret.item_code:
                                if ret.qty:
                                    srqty=float(ret.qty)/360
                                srval=ret.amt

                    html+='<td class="text-right" '+str(sty)+'>'+str(frappe.utils.fmt_money(flt(srqty,3)))+'</td>'
                    html+='<td class="text-right" '+str(sty)+' >'+str(frappe.utils.fmt_money(srval))+'</td>'
                    
                    net=qtyinctn+srqty
                    snet=amount+srval
                    html+='<td class="text-right" '+str(sty)+' ><b>'+str(frappe.utils.fmt_money(net))+'</b></td>'
                    html+='<td class="text-right" '+str(sty)+' ><b>'+str(frappe.utils.fmt_money(snet))+'</b></td>'

                    ntot=netqty_tot[i]
                    netqty_tot[i]=float(net)+float(ntot)

                    stot=netsale_tot[i]
                    netsale_tot[i]=float(snet)+float(stot)

                    tot=saleqtytot[i]
                    saleqtytot[i]=float(tot)+float(qtyinctn)
                    tots=saleamttot[i]
                    saleamttot[i]=float(tots)+float(amount)

                    totr=salerqtytot[i]
                    salerqtytot[i]=float(totr)+float(srqty)
                    totsr=saleramttot[i]
                    saleramttot[i]=float(totsr)+float(srval) 

                    i+=1
                html+='</tr>'
            html+='<tr class="table-secondary"><th>Total</th>'
            j=0
            for total in saleqtytot:
                 html+='<th class="text-right"><b>'+str(frappe.utils.fmt_money(flt(total,3)))+'</b></th>'
                 html+='<th class="text-right"><b>'+str(frappe.utils.fmt_money(flt(saleamttot[j],3)))+'</b></th>'
                 html+='<th class="text-right"><b>'+str(frappe.utils.fmt_money(flt(salerqtytot[j],3)))+'</b></th>'
                 html+='<th class="text-right"><b>'+str(frappe.utils.fmt_money(flt(saleramttot[j],3)))+'</b></th>'
                 html+='<th class="text-right"><b>'+str(frappe.utils.fmt_money(flt(netqty_tot[j],3)))+'</b></th>'
                 html+='<th class="text-right"><b>'+str(frappe.utils.fmt_money(flt(netsale_tot[j],3)))+'</b></th>'
                
                 
                 j+=1
            html+='</tr>'
        
    html+='</table></div>'

    #================== sales return ===========
    html+='<div class="rephd">Sales Return: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;From Date: '+str(frappe.utils.formatdate(date_from))+' To Date : '+str(frappe.utils.formatdate(date_to))+'</div>' 
    html+='<div class="scrl" ><table class="table table-bordered" >'
    saleqtytot=[]
    saleamttot=[]
    
    if date_range:
        html+='<tr class="table-secondary"><th rowspan="2" style="width: 225px;">Items </th>'
        for dr in date_range:
            html+='<th colspan="2" style="text-align:center;font-weight:bold">'+str(frappe.utils.formatdate(dr.get('from'), "MMM yy"))+'</th>'
            saleqtytot.append(0)
            saleamttot.append(0)
            
        html+='</tr>'

        html+='<tr class="table-secondary">'
        for dr in date_range:
            html+='<th>Qty</th><th>Amount</th>'            
        html+='</tr>'

        if itemss:
            for itm in itemss:
                html+='<tr>'
                html+='<td>'+str(getitem_name(itm))+'</td>'
                d=0
                i=0
                for dr in date_range:
                    #if itm.item_code=='CG11111':
                     #   d=1
                    if ((i+1) % 2) == 0:                        
                        sty=' style="background-color: #f3faff; border: 1px solid #ccc;" '
                        
                        
                    else:                        
                        sty=' style=" border: 1px solid #ccc;" '
                        

                    qtyinctn=0
                    amount=0
                    itmqty=range_ressr[i]
                    if itmqty:
                        for it in itmqty:
                            if itm==it.item_code:
                                if it.qty:
                                    qtyinctn=float(it.qty)/360
                                amount=it.amt
                    html+='<td class="text-right" '+str(sty)+' >'+str(frappe.utils.fmt_money(flt(qtyinctn,3)))+'</td>'
                    html+='<td class="text-right" '+str(sty)+' >'+str(frappe.utils.fmt_money(amount))+'</td>'

                    tot=saleqtytot[i]
                    saleqtytot[i]=float(tot)+float(qtyinctn)
                    tots=saleamttot[i]
                    saleamttot[i]=float(tots)+float(amount)    
                    i+=1
                html+='</tr>'
            html+='<tr class="table-secondary"><th>Total</th>'
            j=0
            for total in saleqtytot:
                 html+='<th class="text-right"><b>'+str(frappe.utils.fmt_money(flt(total,3)))+'</b></th>'
                 html+='<th class="text-right"><b>'+str(frappe.utils.fmt_money(flt(saleamttot[j],3)))+'</b></th>'
                 j+=1
            html+='</tr>'
        
    html+='</table></div>'

    return html

def getitem_name(item_code):
    return frappe.db.get_value('Item',item_code,'item_name')


