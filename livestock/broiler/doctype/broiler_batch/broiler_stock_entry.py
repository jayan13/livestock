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
#from erpnext.stock.doctype.stock_entry.stock_entry import get_uom_details

@frappe.whitelist()
def stock_entry(batch):

    from erpnext.stock.doctype.item.item import get_item_defaults    
    udoc = frappe.get_doc('Broiler Batch', batch)
    sett = frappe.get_doc('Broiler Shed',udoc.broiler_shed)
    #items=[]
    #frappe.msgprint(""" projects  {0} """.format(udoc.project_name))
    if not sett:
        frappe.throw(_("Please add Broiler settings for {0} ").format(sett.company))

    stock_entry = frappe.new_doc("Stock Entry")    
    stock_entry.company = sett.company
    stock_entry.purpose = "Manufacture"
    stock_entry.stock_entry_type = "Manufacture"
    stock_entry.manufacturing_type = "Broiler Chicken"
    stock_entry.project = udoc.project
	#stock_entry.set_stock_entry_type()
    base_row_rate=0
    total_add_cost=0

    if sett.base_row_material:
        #base_row_rate = frappe.db.get_value('Item Price', {'price_list': 'Standard Buying','item_code':sett.base_row_material}, 'price_list_rate')        
        item_account_details = get_item_defaults(sett.base_row_material, sett.company)
        stock_uom = item_account_details.stock_uom
        conversion_factor = get_conversion_factor(sett.base_row_material, stock_uom).get("conversion_factor")
        cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
        expense_account=item_account_details.get("expense_account")
        base_row_rate = get_incoming_rate({
						"item_code": sett.base_row_material,
						"warehouse": sett.row_material_target_warehouse,
						"posting_date": stock_entry.posting_date,
						"posting_time": stock_entry.posting_time,
						"qty": -1 * udoc.number_received,
                        'company':sett.company
					})
        if sett.row_material_target_warehouse:
            validate_stock_qty(sett.base_row_material,udoc.number_received,sett.row_material_target_warehouse,stock_uom,stock_uom)

        precision = cint(frappe.db.get_default("float_precision")) or 3    
        amount=flt(flt(udoc.number_received) * flt(base_row_rate), precision)
        stock_entry.append('items', {
                        's_warehouse': sett.row_material_target_warehouse,
                        'item_code': sett.base_row_material,
                        'qty': udoc.number_received,
                        'actual_qty':udoc.number_received,
                        'uom': stock_uom,
                        'cost_center':cost_center,					
                        'ste_detail': item_account_details.name,
                        'stock_uom': stock_uom,
                        'expense_account':expense_account,
                        'valuation_rate': base_row_rate,
                        "basic_rate":base_row_rate, 	
                        "basic_amount":amount,  
                        "amount":amount,  
                        "transfer_qty":udoc.number_received,
                        'conversion_factor': flt(conversion_factor),
                                  
        })
    else:
        frappe.throw(_("Please set base Rowmaterial in hatchery settings for {0} ").format(sett.company))
    

    if udoc.used_items:
        for item in udoc.used_items:
            
                item_account_details = get_item_defaults(item.item_code, sett.company)
                #stock_uom = frappe.db.get_value("Item", item.item_code, "stock_uom")
                stock_uom = item_account_details.stock_uom
                conversion_factor = get_conversion_factor(item.item_code, item.uom).get("conversion_factor")
                cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
                expense_account=item_account_details.get("expense_account")                
                rate = get_incoming_rate({
						"item_code": item.item_code,
						"warehouse": sett.row_material_target_warehouse,
						"posting_date": stock_entry.posting_date,
						"posting_time": stock_entry.posting_time,
						"qty": -1 * item.qty,
                        'company':sett.company
					})
                if sett.row_material_target_warehouse:
                    validate_stock_qty(item.item_code,item.qty,sett.row_material_target_warehouse,item.uom,stock_uom)                

                precision = cint(frappe.db.get_default("float_precision")) or 3    
                amount=flt(flt(item.qty) * flt(rate), precision)

                if sett.base_row_material != item.item_code:
                    total_add_cost=total_add_cost+amount
                

                stock_entry.append('items', {
					's_warehouse': sett.row_material_target_warehouse,
					'item_code': item.item_code,
					'qty': item.qty,
                    'actual_qty':item.qty,
					'uom': item.uom,
                    'cost_center':cost_center,					
					'ste_detail': item.name,
					'stock_uom': stock_uom,
                    'expense_account':expense_account,
                    'valuation_rate': rate,
                    "basic_rate":rate, 	
                    "basic_amount":amount,  
                    "amount":amount,  
                    "transfer_qty":item.qty,
					'conversion_factor': flt(conversion_factor),                    
				})

    
    tot_scrap=sum(c.total for c in udoc.daily_mortality)+udoc.mortality
    
    if tot_scrap:
        item_account_details = get_item_defaults(sett.cull, sett.company)
        stock_uom = item_account_details.stock_uom
        conversion_factor = get_conversion_factor(sett.cull, stock_uom).get("conversion_factor")
        cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
        expense_account=item_account_details.get("expense_account")                                
        precision = cint(frappe.db.get_default("float_precision")) or 3    
        amount=flt(flt(tot_scrap) * flt(base_row_rate), precision)
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

    if udoc.vaccine:
        vaccine=frappe.db.get_list('Vaccine',filters={'parent': udoc.name},fields=['item', 'sum(qty) as qty','uom'],group_by='item')
        for vc in vaccine:
            item_account_details = get_item_defaults(vc.item, sett.company)
            stock_uom = item_account_details.stock_uom
            conversion_factor = get_conversion_factor(vc.item, vc.uom).get("conversion_factor")
            cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
            expense_account=item_account_details.get("expense_account")
            rate = get_incoming_rate({
                            "item_code": vc.item,
                            "warehouse": sett.row_material_target_warehouse,
                            "posting_date": stock_entry.posting_date,
                            "posting_time": stock_entry.posting_time,
                            "qty": -1 * vc.qty,
                            'company':sett.company
                        })
            if sett.row_material_target_warehouse:
                validate_stock_qty(vc.item,vc.qty,sett.row_material_target_warehouse,vc.uom,stock_uom)

            precision = cint(frappe.db.get_default("float_precision")) or 3    
            amount=flt(flt(vc.qty) * flt(rate), precision)
            total_add_cost=total_add_cost+amount
            stock_entry.append('items', {
                            's_warehouse': sett.row_material_target_warehouse,
                            'item_code': vc.item,
                            'qty': vc.qty,
                            'actual_qty':vc.qty,
                            'uom': vc.uom,
                            'cost_center':cost_center,					
                            'ste_detail': item_account_details.name,
                            'stock_uom': stock_uom,
                            'expense_account':expense_account,
                            'valuation_rate': rate,
                            "basic_rate":rate, 	
                            "basic_amount":amount,  
                            "amount":amount,  
                            "transfer_qty":vc.qty,
                            'conversion_factor': flt(conversion_factor),
                                    
            })
            
    if udoc.medicine:
        medicine=frappe.db.get_list('Medicine',filters={'parent': udoc.name},fields=['item', 'sum(qty) as qty','uom'],group_by='item')
        for vc in medicine:
            item_account_details = get_item_defaults(vc.item, sett.company)
            stock_uom = item_account_details.stock_uom
            conversion_factor = get_conversion_factor(vc.item, vc.uom).get("conversion_factor")
            cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
            expense_account=item_account_details.get("expense_account")
            rate = get_incoming_rate({
                            "item_code": vc.item,
                            "warehouse": sett.row_material_target_warehouse,
                            "posting_date": stock_entry.posting_date,
                            "posting_time": stock_entry.posting_time,
                            "qty": -1 * vc.qty,
                            'company':sett.company
                        })
            if sett.row_material_target_warehouse:
                validate_stock_qty(vc.item,vc.qty,sett.row_material_target_warehouse,vc.uom,stock_uom)

            precision = cint(frappe.db.get_default("float_precision")) or 3    
            amount=flt(flt(vc.qty) * flt(rate), precision)
            total_add_cost=total_add_cost+amount
            stock_entry.append('items', {
                            's_warehouse': sett.row_material_target_warehouse,
                            'item_code': vc.item,
                            'qty': vc.qty,
                            'actual_qty':vc.qty,
                            'uom': vc.uom,
                            'cost_center':cost_center,					
                            'ste_detail': item_account_details.name,
                            'stock_uom': stock_uom,
                            'expense_account':expense_account,
                            'valuation_rate': rate,
                            "basic_rate":rate, 	
                            "basic_amount":amount,  
                            "amount":amount,  
                            "transfer_qty":vc.qty,
                            'conversion_factor': flt(conversion_factor),
                                    
            })

    if udoc.feed:
        sfeed=frappe.db.get_list('Feed',filters={'parent': udoc.name},fields=['starter_item as item', 'sum(starter_qty) as qty','starter_uom as uom'],group_by='starter_item')
        
        for vc in sfeed:
            item_account_details = get_item_defaults(vc.item, sett.company)
            stock_uom = item_account_details.stock_uom
            conversion_factor = get_conversion_factor(vc.item, vc.uom).get("conversion_factor")
            cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
            expense_account=item_account_details.get("expense_account")
            rate = get_incoming_rate({
                            "item_code": vc.item,
                            "warehouse": sett.feed_warehouse,
                            "posting_date": stock_entry.posting_date,
                            "posting_time": stock_entry.posting_time,
                            "qty": -1 * vc.qty,
                            'company':sett.company
                        })
            if sett.feed_warehouse:
                validate_stock_qty(vc.item,vc.qty,sett.feed_warehouse,vc.uom,stock_uom)

            precision = cint(frappe.db.get_default("float_precision")) or 3    
            amount=flt(flt(vc.qty) * flt(rate), precision)
            total_add_cost=total_add_cost+amount
            stock_entry.append('items', {
                            's_warehouse': sett.feed_warehouse,
                            'item_code': vc.item,
                            'qty': vc.qty,
                            'actual_qty':vc.qty,
                            'uom': vc.uom,
                            'cost_center':cost_center,					
                            'ste_detail': item_account_details.name,
                            'stock_uom': stock_uom,
                            'expense_account':expense_account,
                            'valuation_rate': rate,
                            "basic_rate":rate, 	
                            "basic_amount":amount,  
                            "amount":amount,  
                            "transfer_qty":vc.qty,
                            'conversion_factor': flt(conversion_factor),
                                    
            })

        ffeed=frappe.db.get_list('Feed',filters={'parent': udoc.name},fields=['finisher_item as item', 'sum(finisher_qty) as qty','finisher_uom as uom'],group_by='finisher_item')

        for vc in ffeed:
            item_account_details = get_item_defaults(vc.item, sett.company)
            stock_uom = item_account_details.stock_uom
            conversion_factor = get_conversion_factor(vc.item, vc.uom).get("conversion_factor")
            cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
            expense_account=item_account_details.get("expense_account")
            rate = get_incoming_rate({
                            "item_code": vc.item,
                            "warehouse": sett.feed_warehouse,
                            "posting_date": stock_entry.posting_date,
                            "posting_time": stock_entry.posting_time,
                            "qty": -1 * vc.qty,
                            'company':sett.company
                        })
            if sett.feed_warehouse:
                validate_stock_qty(vc.item,vc.qty,sett.feed_warehouse,vc.uom,stock_uom)

            precision = cint(frappe.db.get_default("float_precision")) or 3    
            amount=flt(flt(vc.qty) * flt(rate), precision)
            total_add_cost=total_add_cost+amount
            stock_entry.append('items', {
                            's_warehouse': sett.feed_warehouse,
                            'item_code': vc.item,
                            'qty': vc.qty,
                            'actual_qty':vc.qty,
                            'uom': vc.uom,
                            'cost_center':cost_center,					
                            'ste_detail': item_account_details.name,
                            'stock_uom': stock_uom,
                            'expense_account':expense_account,
                            'valuation_rate': rate,
                            "basic_rate":rate, 	
                            "basic_amount":amount,  
                            "amount":amount,  
                            "transfer_qty":vc.qty,
                            'conversion_factor': flt(conversion_factor),
                                    
            })

    if udoc.current_alive_chicks:

        item_account_details = get_item_defaults(sett.product, sett.company)
        stock_uom = item_account_details.stock_uom
        conversion_factor = get_conversion_factor(sett.product, stock_uom).get("conversion_factor")
        cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
        expense_account=item_account_details.get("expense_account")                                
        precision = cint(frappe.db.get_default("float_precision")) or 3
        cost=((udoc.current_alive_chicks*base_row_rate) + total_add_cost) / udoc.current_alive_chicks
        amount=flt(flt(udoc.current_alive_chicks) * flt(cost), precision)
        stock_entry.append('items', {
                        't_warehouse': sett.product_target_warehouse,
                        'item_code': sett.product,
                        'qty': udoc.current_alive_chicks,
                        'actual_qty':udoc.current_alive_chicks,
                        'uom': stock_uom,
                        'cost_center':cost_center,					
                        'ste_detail': item_account_details.name,
                        'stock_uom': stock_uom,
                        'expense_account':expense_account,
                        'valuation_rate': cost,
                        "basic_rate":cost, 	
                        "basic_amount":amount,  
                        "amount":amount,  
                        "transfer_qty":udoc.current_alive_chicks,
                        'conversion_factor': flt(conversion_factor),
                        'is_finished_item':1,               
        })
    

    return stock_entry.as_dict()

def validate_stock_qty(item_code,req_qty,warehouse,uom,stock_uom):
    if uom != stock_uom:
        conversion_factor = get_conversion_factor(item_code, uom).get("conversion_factor") or 1
        stock_qty=req_qty*flt(conversion_factor)
    else:
        stock_qty=req_qty

    qty=frappe.db.get_value('Bin', {'item_code': item_code,'warehouse':warehouse}, ['actual_qty as qty'],debug=0)
    qty=qty or 0
    if(stock_qty > qty):
        frappe.throw(_("There is no sufficient qty in {0} Please select another warehouse for {1}").format(warehouse,item_code))


@frappe.whitelist()
def update_item_stat(doc,event):
    batch=frappe.db.get_value('Broiler Batch', {'project': doc.project}, ['name'])
    if batch:
        udoc = frappe.get_doc('Broiler Batch', batch)
        if udoc:
            udoc.item_processed = 1
            udoc.save()


