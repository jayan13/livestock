from distutils.log import debug
from itertools import product
import frappe
import erpnext
from frappe import _
from frappe.utils import cint, comma_or, cstr, flt, format_time, formatdate, getdate, nowdate
from erpnext.stock.get_item_details import (
	get_conversion_factor,
	get_default_cost_center,
)
from erpnext.stock.utils import (get_incoming_rate)
from erpnext.stock.doctype.item.item import get_item_defaults 
#from erpnext.stock.doctype.stock_entry.stock_entry import get_uom_details

@frappe.whitelist()
def stock_entry_rec(batch,transfer_qty):
    udoc = frappe.get_doc('Broiler Batch', batch)
    sett = frappe.get_doc('Broiler Shed',udoc.broiler_shed)
    #----------------  exess production material recipt entry-------------
    exess=int(transfer_qty)
    stock_entry_recp = frappe.new_doc("Stock Entry")    
    stock_entry_recp.company = sett.company
    stock_entry_recp.purpose = "Manufacture"
    stock_entry_recp.stock_entry_type = "Material Receipt"
    stock_entry_recp.manufacturing_type = "Broiler Chicken"
    stock_entry_recp.project = udoc.project
    stock_entry_recp.posting_date=nowdate()        
    item_account_details = get_item_defaults(sett.base_row_material, sett.company)
    stock_uom = item_account_details.stock_uom
    conversion_factor = get_conversion_factor(sett.base_row_material, stock_uom).get("conversion_factor")
    cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
    stock_adjustment_account=frappe.db.get_value('Company',sett.company,'stock_adjustment_account')
    expense_account=sett.difference_account or stock_adjustment_account or item_account_details.get("expense_account")
    base_row_rate = get_incoming_rate({
						"item_code": sett.base_row_material,
						"warehouse": sett.row_material_target_warehouse,
						"posting_date": stock_entry_recp.posting_date,
						"posting_time": stock_entry_recp.posting_time,
						"qty": -1 * exess,
                        'company':sett.company
					})

    precision = cint(frappe.db.get_default("float_precision")) or 3    
    amount=flt(exess * flt(base_row_rate), precision)
    stock_entry_recp.append('items', {
                        't_warehouse': sett.row_material_target_warehouse,
                        'item_code': sett.base_row_material,
                        'qty': exess,
                        'actual_qty':exess,
                        'uom': stock_uom,
                        'cost_center':cost_center,					
                        'ste_detail': item_account_details.name,
                        'stock_uom': stock_uom,
                        'expense_account':expense_account,
                        'valuation_rate': base_row_rate,
                        "basic_rate":base_row_rate, 	
                        "basic_amount":amount,  
                        "amount":amount,  
                        "transfer_qty":exess,
                        'conversion_factor': flt(conversion_factor),
                                  
        })
    stock_entry_recp.insert(ignore_permissions=True)
    stock_entry_recp.submit()

    #udoc.excess_production = udoc.excess_production+int(exess)
    #udoc.save()
    excess_production,current_alive_chicks=frappe.db.get_value('Broiler Batch', batch, ['excess_production','current_alive_chicks'])
    current_alive_chicks=current_alive_chicks+exess
    excess_production=excess_production+exess
    frappe.db.set_value('Broiler Batch', batch, 'excess_production', excess_production)
    frappe.db.set_value('Broiler Batch', batch, 'current_alive_chicks', current_alive_chicks)

    frappe.msgprint(" Material receipt created "+str(stock_entry_recp.name))
    return exess
    #----------------  exess production  material recipt entry-------------

@frappe.whitelist()
def stock_entry(batch,transfer_qty,transfer_date,transfer_warehouse=''):
    
    udoc = frappe.get_doc('Broiler Batch', batch)
    sett = frappe.get_doc('Broiler Shed',udoc.broiler_shed)
    
    broiler_item_transfer=frappe.db.get_list('Broiler Item Transfer',filters={'processed': '1','broiler_bach':batch},
    fields=['sum(transfer_qty) as transfer_qty,sum(scrap) as scrap'],group_by='broiler_bach')
    pv_qty={}
    #pv_transfer_qty = 0
    pv_scrap = 0
    for trn in broiler_item_transfer:
        #pv_transfer_qty = trn.transfer_qty
        pv_scrap = trn.scrap

    cur_live=udoc.current_alive_chicks
    materials=frappe.db.get_list('Broiler Transfer Consumable',filters={'processed': '1','batch':batch},
    fields=['sum(ROUND(used_quantity, 2)) as used_quantity,materal'],group_by='materal',debug=0)
    for mat in materials:
        pv_qty.update({mat.materal:mat.used_quantity})

    if not sett:
        frappe.throw(_("Please add Broiler settings for {0} ").format(sett.company))

    broiler_item = frappe.new_doc("Broiler Item Transfer")
    broiler_item.transfer_date=transfer_date
    broiler_item.transfer_qty=transfer_qty
    broiler_item.transfer_warehouse=transfer_warehouse
    broiler_item.broiler_bach=batch
    
    stock_entry = frappe.new_doc("Stock Entry")    
    stock_entry.company = sett.company
    stock_entry.purpose = "Manufacture"
    stock_entry.stock_entry_type = "Manufacture"
    stock_entry.manufacturing_type = "Broiler Chicken"
    stock_entry.project = udoc.project
    stock_entry.posting_date=transfer_date
	#stock_entry.set_stock_entry_type()
    base_row_rate=0
    total_add_cost=0
    tot_scrap=sum(c.total for c in udoc.daily_mortality)+udoc.mortality-pv_scrap or 0
    if tot_scrap < 0:
        tot_scrap=0

    if sett.base_row_material:
        #base_row_rate = frappe.db.get_value('Item Price', {'price_list': 'Standard Buying','item_code':sett.base_row_material}, 'price_list_rate')
        pv_item_qty=pv_qty.get(sett.base_row_material) or 0
        itmqty=int(tot_scrap)+int(transfer_qty)
        broiler_item.append('materials', {
        'materal':sett.base_row_material,
        'used_quantity':itmqty,
        'batch':batch
        })

        item_account_details = get_item_defaults(sett.base_row_material, sett.company)
        stock_uom = item_account_details.stock_uom
        conversion_factor = get_conversion_factor(sett.base_row_material, stock_uom).get("conversion_factor")
        cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
        stock_adjustment_account=frappe.db.get_value('Company',sett.company,'stock_adjustment_account')
        expense_account=stock_adjustment_account or item_account_details.get("expense_account")
        base_row_rate = get_incoming_rate({
						"item_code": sett.base_row_material,
						"warehouse": sett.row_material_target_warehouse,
						"posting_date": stock_entry.posting_date,
						"posting_time": stock_entry.posting_time,
						"qty": -1 * itmqty,
                        'company':sett.company
					})
        if sett.row_material_target_warehouse:
            validate_stock_qty(sett.base_row_material,itmqty,sett.row_material_target_warehouse,stock_uom,stock_uom)

        precision = cint(frappe.db.get_default("float_precision")) or 3    
        amount=flt(itmqty * flt(base_row_rate), precision)
        stock_entry.append('items', {
                        's_warehouse': sett.row_material_target_warehouse,
                        'item_code': sett.base_row_material,
                        'qty': itmqty,
                        'actual_qty':itmqty,
                        'uom': stock_uom,
                        'cost_center':cost_center,					
                        'ste_detail': item_account_details.name,
                        'stock_uom': stock_uom,
                        'expense_account':expense_account,
                        'valuation_rate': base_row_rate,
                        "basic_rate":base_row_rate, 	
                        "basic_amount":amount,  
                        "amount":amount,  
                        "transfer_qty":itmqty,
                        'conversion_factor': flt(conversion_factor),
                                  
        })
    else:
        frappe.throw(_("Please set base Rowmaterial in hatchery settings for {0} ").format(sett.company))
    

    if udoc.used_items:
        used_items=frappe.db.get_list('Broiler Items',filters={'parent': udoc.name,'date':['<=',transfer_date]},fields=['item_code', 'sum(qty) as qty','uom'],group_by='item_code')
        for item in used_items:
            if item.item_code:

                pv_item_qty=pv_qty.get(item.item_code) or 0
                itmqty=flt(((item.qty-pv_item_qty)/cur_live)*int(transfer_qty),2)
                broiler_item.append('materials', {
                'materal':item.item_code,
                'used_quantity':itmqty,
                'batch':batch
                })

                item_account_details = get_item_defaults(item.item_code, sett.company)
                #stock_uom = frappe.db.get_value("Item", item.item_code, "stock_uom")
                stock_uom = item_account_details.stock_uom
                conversion_factor = get_conversion_factor(item.item_code, item.uom).get("conversion_factor")
                cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
                stock_adjustment_account=frappe.db.get_value('Company',sett.company,'stock_adjustment_account')
                expense_account=stock_adjustment_account or item_account_details.get("expense_account")                
                rate = get_incoming_rate({
						"item_code": item.item_code,
						"warehouse": sett.row_material_target_warehouse,
						"posting_date": stock_entry.posting_date,
						"posting_time": stock_entry.posting_time,
						"qty": -1 * itmqty,
                        'company':sett.company
					})
                if sett.row_material_target_warehouse:
                    validate_stock_qty(item.item_code,itmqty,sett.row_material_target_warehouse,item.uom,stock_uom)                

                precision = cint(frappe.db.get_default("float_precision")) or 3    
                amount=flt(itmqty * flt(rate), precision)

                if sett.base_row_material != item.item_code:
                    total_add_cost=total_add_cost+amount
                

                stock_entry.append('items', {
					's_warehouse': sett.row_material_target_warehouse,
					'item_code': item.item_code,
					'qty': itmqty,
                    'actual_qty':itmqty,
					'uom': item.uom,
                    'cost_center':cost_center,					
					'ste_detail': item_account_details.name,
					'stock_uom': stock_uom,
                    'expense_account':expense_account,
                    'valuation_rate': rate,
                    "basic_rate":rate, 	
                    "basic_amount":amount,  
                    "amount":amount,  
                    "transfer_qty":itmqty,
					'conversion_factor': flt(conversion_factor),                    
				})


    if udoc.vaccine:
        vaccine=frappe.db.get_list('Vaccine',filters={'parent': udoc.name,'date':['<=',transfer_date]},fields=['item', 'sum(qty) as qty','uom'],group_by='item')
        for vc in vaccine:
            if vc.item:

                pv_item_qty=pv_qty.get(vc.item) or 0
                itmqty=flt(((vc.qty-pv_item_qty)/cur_live)*int(transfer_qty),2)
                broiler_item.append('materials', {
                'materal':vc.item,
                'used_quantity':itmqty,
                'batch':batch
                })

                item_account_details = get_item_defaults(vc.item, sett.company)
                stock_uom = item_account_details.stock_uom
                conversion_factor = get_conversion_factor(vc.item, vc.uom).get("conversion_factor")
                cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
                stock_adjustment_account=frappe.db.get_value('Company',sett.company,'stock_adjustment_account')
                expense_account=stock_adjustment_account or item_account_details.get("expense_account")
                rate = get_incoming_rate({
                                "item_code": vc.item,
                                "warehouse": sett.row_material_target_warehouse,
                                "posting_date": stock_entry.posting_date,
                                "posting_time": stock_entry.posting_time,
                                "qty": -1 * itmqty,
                                'company':sett.company
                            })
                if sett.row_material_target_warehouse:
                    validate_stock_qty(vc.item,itmqty,sett.row_material_target_warehouse,vc.uom,stock_uom)

                precision = cint(frappe.db.get_default("float_precision")) or 3    
                amount=flt(itmqty * flt(rate), precision)
                total_add_cost=total_add_cost+amount
                stock_entry.append('items', {
                                's_warehouse': sett.row_material_target_warehouse,
                                'item_code': vc.item,
                                'qty': itmqty,
                                'actual_qty':itmqty,
                                'uom': vc.uom,
                                'cost_center':cost_center,					
                                'ste_detail': item_account_details.name,
                                'stock_uom': stock_uom,
                                'expense_account':expense_account,
                                'valuation_rate': rate,
                                "basic_rate":rate, 	
                                "basic_amount":amount,  
                                "amount":amount,  
                                "transfer_qty":itmqty,
                                'conversion_factor': flt(conversion_factor),
                                        
                })
            
    if udoc.medicine:
        medicine=frappe.db.get_list('Medicine',filters={'parent': udoc.name,'date':['<=',transfer_date]},fields=['item', 'sum(qty) as qty','uom'],group_by='item')
        for vc in medicine:
            if vc.item:

                pv_item_qty=pv_qty.get(vc.item) or 0
                itmqty=flt(((vc.qty-pv_item_qty)/cur_live)*int(transfer_qty),2)
                broiler_item.append('materials', {
                'materal':vc.item,
                'used_quantity':itmqty,
                'batch':batch
                })
                item_account_details = get_item_defaults(vc.item, sett.company)
                stock_uom = item_account_details.stock_uom
                conversion_factor = get_conversion_factor(vc.item, vc.uom).get("conversion_factor")
                cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
                stock_adjustment_account=frappe.db.get_value('Company',sett.company,'stock_adjustment_account')
                expense_account=stock_adjustment_account or item_account_details.get("expense_account")
                rate = get_incoming_rate({
                                "item_code": vc.item,
                                "warehouse": sett.row_material_target_warehouse,
                                "posting_date": stock_entry.posting_date,
                                "posting_time": stock_entry.posting_time,
                                "qty": -1 * itmqty,
                                'company':sett.company
                            })
                if sett.row_material_target_warehouse:
                    validate_stock_qty(vc.item,itmqty,sett.row_material_target_warehouse,vc.uom,stock_uom)

                precision = cint(frappe.db.get_default("float_precision")) or 3    
                amount=flt(itmqty * flt(rate), precision)
                total_add_cost=total_add_cost+amount
                stock_entry.append('items', {
                                's_warehouse': sett.row_material_target_warehouse,
                                'item_code': vc.item,
                                'qty': itmqty,
                                'actual_qty':itmqty,
                                'uom': vc.uom,
                                'cost_center':cost_center,					
                                'ste_detail': item_account_details.name,
                                'stock_uom': stock_uom,
                                'expense_account':expense_account,
                                'valuation_rate': rate,
                                "basic_rate":rate, 	
                                "basic_amount":amount,  
                                "amount":amount,  
                                "transfer_qty":itmqty,
                                'conversion_factor': flt(conversion_factor),
                                        
                })

    if udoc.feed:
        sfeed=frappe.db.sql(""" select item,sum(qty) as qty,uom from ((select finisher_item as item,sum(finisher_qty) as qty,finisher_uom as uom from `tabFeed` where parent='{0}' and `date`<='{1}' group by item) UNION ALL (select starter_item as item,sum(starter_qty) as qty,starter_uom as uom from `tabFeed` where parent='{0}' and `date`<='{1}' group by item)) as feed group by item """.format(batch,transfer_date),as_dict=1,debug=0)
        #sfeed=frappe.db.get_list('Feed',filters={'parent': udoc.name,'date':['<=',transfer_date]},fields=['starter_item as item', 'sum(starter_qty) as qty','starter_uom as uom'],group_by='starter_item')
        
        for vc in sfeed:
            if vc.item:
                
                pv_item_qty=pv_qty.get(vc.item) or 0
                itmqty=flt(((vc.qty-pv_item_qty)/cur_live)*int(transfer_qty),2)
                #frappe.msgprint(str(vc.qty)+'-'+str(pv_item_qty))
                broiler_item.append('materials', {
                'materal':vc.item,
                'used_quantity':itmqty,
                'batch':batch
                })
                item_account_details = get_item_defaults(vc.item, sett.company)
                stock_uom = item_account_details.stock_uom
                conversion_factor = get_conversion_factor(vc.item, vc.uom).get("conversion_factor")
                #frappe.msgprint("conf1"+str(conversion_factor))
                cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
                stock_adjustment_account=frappe.db.get_value('Company',sett.company,'stock_adjustment_account')
                expense_account=stock_adjustment_account or item_account_details.get("expense_account")
                rate = get_incoming_rate({
                                "item_code": vc.item,
                                "warehouse": sett.feed_warehouse,
                                "posting_date": stock_entry.posting_date,
                                "posting_time": stock_entry.posting_time,
                                "qty": -1 * itmqty,
                                'company':sett.company
                            })
                if sett.feed_warehouse:
                    validate_stock_qty(vc.item,itmqty,sett.feed_warehouse,vc.uom,stock_uom)

                precision = cint(frappe.db.get_default("float_precision")) or 3    
                amount=flt(flt(vc.qty) * flt(rate), precision)
                total_add_cost=total_add_cost+amount
                stock_entry.append('items', {
                                's_warehouse': sett.feed_warehouse,
                                'item_code': vc.item,
                                'qty': itmqty,
                                'actual_qty':itmqty,
                                'uom': vc.uom,
                                'cost_center':cost_center,					
                                'ste_detail': item_account_details.name,
                                'stock_uom': stock_uom,
                                'expense_account':expense_account,
                                'valuation_rate': rate,
                                "basic_rate":rate, 	
                                "basic_amount":amount,  
                                "amount":amount,  
                                "transfer_qty":itmqty,
                                'conversion_factor': flt(conversion_factor),
                                        
                })

        

    if transfer_qty:

        item_account_details = get_item_defaults(sett.product, sett.company)
        stock_uom = item_account_details.stock_uom
        conversion_factor = get_conversion_factor(sett.product, stock_uom).get("conversion_factor")
        cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
        stock_adjustment_account=frappe.db.get_value('Company',sett.company,'stock_adjustment_account')
        expense_account=stock_adjustment_account or item_account_details.get("expense_account")                                  
        precision = cint(frappe.db.get_default("float_precision")) or 3
        cost=((int(transfer_qty)*base_row_rate) + total_add_cost) / int(transfer_qty)
        amount=flt(int(transfer_qty) * flt(cost), precision)
        stock_entry.append('items', {
                        't_warehouse': transfer_warehouse or sett.product_target_warehouse,
                        'item_code': sett.product,
                        'qty': transfer_qty,
                        'actual_qty':transfer_qty,
                        'uom': stock_uom,
                        'cost_center':cost_center,					
                        'ste_detail': item_account_details.name,
                        'stock_uom': stock_uom,
                        'expense_account':expense_account,
                        'valuation_rate': cost,
                        "basic_rate":cost, 	
                        "basic_amount":amount,  
                        "amount":amount,  
                        "transfer_qty":transfer_qty,
                        'conversion_factor': flt(conversion_factor),
                        'is_finished_item':1,               
        })

    
    broiler_item.scrap=tot_scrap
    broiler_item.insert(ignore_permissions=True)
    
    if tot_scrap:

        item_account_details = get_item_defaults(sett.cull, sett.company)
        stock_uom = item_account_details.stock_uom
        conversion_factor = get_conversion_factor(sett.cull, stock_uom).get("conversion_factor")
        cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
        stock_adjustment_account=frappe.db.get_value('Company',sett.company,'stock_adjustment_account')
        expense_account=stock_adjustment_account or item_account_details.get("expense_account")                                
        precision = cint(frappe.db.get_default("float_precision")) or 3
        base_row_rate = get_incoming_rate({
						"item_code": sett.base_row_material,
						"warehouse": sett.cull_target_warehouse,
						"posting_date": stock_entry.posting_date,
						"posting_time": stock_entry.posting_time,
						"qty": -1 * tot_scrap,
                        'company':sett.company
					})    
        amount=flt(flt(tot_scrap) * base_row_rate, precision)
        stock_entry.append('items', {
                        't_warehouse': sett.cull_target_warehouse,
                        'item_code': sett.cull,
                        'qty': tot_scrap,
                        'actual_qty':tot_scrap,
                        'uom': stock_uom,
                        'cost_center':cost_center,					
                        'ste_detail': item_account_details.name,
                        'stock_uom': stock_uom,
                        'expense_account':expense_account,
                        'valuation_rate': base_row_rate,
                        "basic_rate":base_row_rate, 	
                        "basic_amount":amount,  
                        "amount":amount,  
                        "transfer_qty":tot_scrap,
                        'conversion_factor': flt(conversion_factor),
                        'is_scrap_item':1,          
        })
    
    stock_entry.item_transfer=broiler_item.name
    
    return stock_entry.as_dict()

def validate_stock_qty(item_code,req_qty,warehouse,uom,stock_uom):
    
    if uom != stock_uom:
        conversion_factor = get_conversion_factor(item_code, uom).get("conversion_factor") or 1
        stock_qty=flt(req_qty*flt(conversion_factor),2)
    else:
        stock_qty=flt(req_qty,2)

    qty=frappe.db.get_value('Bin', {'item_code': item_code,'warehouse':warehouse}, ['actual_qty as qty'],debug=0)
    qty=qty or 0
    if(stock_qty > qty):
        frappe.throw(_("Req Qty {0}. There is no sufficient qty in {1} Please select another warehouse for {2}").format(stock_qty,warehouse,item_code))


@frappe.whitelist()
def update_item_stat(doc,event):
    frappe.db.set_value('Broiler Item Transfer', doc.item_transfer, 'processed', '1')
    frappe.db.sql("""update `tabBroiler Transfer Consumable` set processed='1' where parent=%s""",doc.item_transfer)
    transfer_qty=frappe.db.get_value('Broiler Item Transfer', {'name': doc.item_transfer}, ['transfer_qty']) or 0   

    batch=frappe.db.get_value('Broiler Batch', {'project': doc.project}, ['name'])
    if batch:
        udoc = frappe.get_doc('Broiler Batch', batch)
        if udoc:            
            if (int(udoc.current_alive_chicks)-int(transfer_qty)) < 1:
                udoc.item_processed = 1
            
            udoc.current_alive_chicks =udoc.current_alive_chicks-int(transfer_qty)            
            udoc.chick_transferred = int(transfer_qty)+udoc.chick_transferred
            udoc.save()

@frappe.whitelist()
def delete_item(doc,event):
    if doc.item_transfer:
        
        trn=frappe.db.get_value("Broiler Item Transfer", {'name': doc.item_transfer,'processed':'1'}, ['transfer_qty']) or 0
        if trn:
            batch,chick_transferred,current_alive_chicks,excess_production=frappe.db.get_value('Broiler Batch', {'project': doc.project}, ['name','chick_transferred','current_alive_chicks','excess_production'])
            trns=int(chick_transferred)-int(trn)
            trns2=int(current_alive_chicks)+int(trn)
            frappe.db.set_value('Broiler Batch', batch, 'chick_transferred', trns)
            frappe.db.set_value('Broiler Batch', batch, 'current_alive_chicks', trns2)

        frappe.db.delete("Broiler Transfer Consumable", {"parent": doc.item_transfer })
        frappe.db.delete("Broiler Item Transfer", {"name": doc.item_transfer })

@frappe.whitelist()
def cancel_item(doc,event):

    if doc.item_transfer:
        
        trn=frappe.db.get_value("Broiler Item Transfer", {'name': doc.item_transfer,'processed':'1'}, ['transfer_qty']) or 0
        if trn:
            batch,chick_transferred,current_alive_chicks,excess_production=frappe.db.get_value('Broiler Batch', {'project': doc.project}, ['name','chick_transferred','current_alive_chicks','excess_production'])
            trns=int(chick_transferred)-int(trn)
            trns2=int(current_alive_chicks)+int(trn)
            frappe.db.set_value('Broiler Batch', batch, 'chick_transferred', trns)
            frappe.db.set_value('Broiler Batch', batch, 'current_alive_chicks', trns2)
            frappe.db.set_value('Broiler Batch', batch, 'item_processed', '0')


        frappe.db.set_value('Broiler Item Transfer', doc.item_transfer, 'processed', '0')
        frappe.db.sql("""update `tabBroiler Transfer Consumable` set processed='0' where parent=%s""",doc.item_transfer)
    elif doc.manufacturing_type == "Broiler Chicken" and doc.stock_entry_type == "Material Receipt":
        batch,current_alive_chicks,excess_production=frappe.db.get_value('Broiler Batch', {'project': doc.project}, ['name','current_alive_chicks','excess_production'])
        qty=frappe.db.get_value('Stock Entry Detail', {'parent': doc.name}, ['qty'])
        livechk=float(current_alive_chicks)-float(qty)
        exes=float(excess_production)-float(qty)
        frappe.db.set_value('Broiler Batch', batch, 'current_alive_chicks', livechk)
        frappe.db.set_value('Broiler Batch', batch, 'excess_production', exes)

@frappe.whitelist()
def get_added_mortality(batch):
    broiler_item_transfer=frappe.db.get_list('Broiler Item Transfer',filters={'processed': '1','broiler_bach':batch},
    fields=['sum(scrap) as scrap'],group_by='broiler_bach')
    pv_scrap = 0
    for trn in broiler_item_transfer:
        pv_scrap = trn.scrap
        
    return pv_scrap