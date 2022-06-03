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
def stock_entry(own_packing):

    from erpnext.stock.doctype.item.item import get_item_defaults    
    udoc = frappe.get_doc('Chicken Own Packing', own_packing)
    sett = frappe.get_doc('Own Packing Settings')
    stock_entry = frappe.new_doc("Stock Entry")    
    stock_entry.company = udoc.company
    #stock_entry.project = udoc.project
    stock_entry.purpose = "Manufacture"
    stock_entry.stock_entry_type = "Manufacture"
    stock_entry.manufacturing_type = "Chicken Slaughtering"
    stock_entry.own_packing=own_packing
	#stock_entry.set_stock_entry_type()
    precision = cint(frappe.db.get_default("float_precision")) or 3
    base_row_rate=0
    row_cost=0

    if udoc.item:
        #base_row_rate = frappe.db.get_value('Item Price', {'price_list': 'Standard Buying','item_code':udoc.item}, 'price_list_rate')        
        item_account_details = get_item_defaults(udoc.item, udoc.company)
        stock_uom = item_account_details.stock_uom
        conversion_factor = get_conversion_factor(udoc.item, stock_uom).get("conversion_factor")
        cost_center=sett.cost_center or item_account_details.get("buying_cost_center")
        expense_account=item_account_details.get("expense_account")        
        base_row_rate = get_incoming_rate({
						"item_code": udoc.item,
						"warehouse": udoc.warehouse,
						"posting_date": stock_entry.posting_date,
						"posting_time": stock_entry.posting_time,
						"qty": -1 * udoc.number_of_chicken,
                        'company':udoc.company
					})
        if udoc.warehouse:
            validate_stock_qty(udoc.item,udoc.number_of_chicken,udoc.warehouse,stock_uom,stock_uom)
            
        amount=flt(flt(udoc.number_of_chicken) * flt(base_row_rate), precision)
        row_cost+=amount
        stock_entry.append('items', {
                        's_warehouse': udoc.warehouse,
                        'item_code': udoc.item,
                        'qty': udoc.number_of_chicken,
                        'actual_qty':udoc.number_of_chicken,
                        'uom': stock_uom,
                        'cost_center':cost_center,					
                        'ste_detail': item_account_details.name,
                        'stock_uom': stock_uom,
                        'expense_account':expense_account,
                        'valuation_rate': base_row_rate,
                        "basic_rate":base_row_rate, 	
                        "basic_amount":amount,  
                        "amount":amount,  
                        "transfer_qty":udoc.number_of_chicken,
                        'conversion_factor': flt(conversion_factor),
                                  
        })
    else:
        frappe.throw(_("Please enter processing item "))
    

    if udoc.finished_items:
        total_finished_item=0        
        
        for fitem in udoc.finished_items:
            item_account_details = get_item_defaults(fitem.item, udoc.company)            
            #weight_per_unit=item_account_details.get("weight_per_unit")
            #weight_uom=item_account_details.get("weight_uom")
            total_finished_item+=int(fitem.qty)*item_account_details.weight_per_unit

        unit_cost=(row_cost/total_finished_item)

        for fitem in udoc.finished_items:
            pcitems=[]
            itemscost=0
            item_account_details = get_item_defaults(fitem.item, udoc.company)
            pcmaterials=frappe.get_doc('Packing Materials',fitem.item)           
            
            for pcitem in pcmaterials.packing_item:
                pack_item_details = get_item_defaults(pcitem.item, udoc.company)
                stock_uom = pack_item_details.stock_uom
                conversion_factor = get_conversion_factor(pcitem.item, pcitem.uom).get("conversion_factor")
                cost_center=sett.cost_center or pack_item_details.get("buying_cost_center")
                expense_account=pack_item_details.get("expense_account")                
                item_name=pack_item_details.get("item_name")
                pck_rate = get_incoming_rate({
						"item_code": pcitem.item,
						"warehouse": udoc.warehouse,
						"posting_date": stock_entry.posting_date,
						"posting_time": stock_entry.posting_time,
						"qty": -1 * pcitem.qty,
                        'company':udoc.company
					})
                packed_qty=float(pcitem.qty)*float(fitem.qty)
                amount=flt(flt(packed_qty) * flt(pck_rate), precision)
                itemscost+=amount
                pcitems.append({
                    's_warehouse': udoc.warehouse,
					'item_code': pcitem.item,
					'qty': packed_qty,
                    'actual_qty':packed_qty,
					'uom': pcitem.uom,
                    'cost_center':cost_center,					
					'ste_detail': item_name,
					'stock_uom': stock_uom,
                    'expense_account':expense_account,
                    'valuation_rate': pck_rate,
                    "basic_rate":pck_rate, 	
                    "basic_amount":amount,  
                    "amount":amount,  
                    "transfer_qty":packed_qty,
					'conversion_factor': flt(conversion_factor),                    
			        })    
                


            #base_rate = frappe.db.get_value('Item Price', {'price_list': 'Standard Selling','item_code':fitem.item}, 'price_list_rate') 
            stock_uom = item_account_details.stock_uom
            conversion_factor = get_conversion_factor(fitem.item, fitem.uom).get("conversion_factor")
            cost_center=sett.cost_center or item_account_details.get("buying_cost_center")
            expense_account=item_account_details.get("expense_account")                
            item_name=item_account_details.get("item_name")
            #weight_per_unit=item_account_details.get("weight_per_unit")
            packing_rate_of_item=itemscost/float(fitem.qty)

            base_rate=packing_rate_of_item+(unit_cost*item_account_details.weight_per_unit)
  
            amount=flt(flt(fitem.qty) * flt(base_rate), precision)
                
            stock_entry.append('items', {
                    't_warehouse': sett.warehouse,
					'item_code': fitem.item,
					'qty': fitem.qty,
                    'actual_qty':fitem.qty,
					'uom': fitem.uom,
                    'cost_center':cost_center,					
					'ste_detail': item_name,
					'stock_uom': stock_uom,
                    'expense_account':expense_account,
                    'valuation_rate': base_rate,
                    "basic_rate":base_rate, 	
                    "basic_amount":amount,  
                    "amount":amount,  
                    "transfer_qty":fitem.qty,
					'conversion_factor': flt(conversion_factor),                    
			})

            for pc in pcitems:
                stock_entry.append('items',pc)
    
    return stock_entry.as_dict()

def validate_stock_qty(item_code,req_qty,warehouse,uom,stock_uom):
    if uom != stock_uom:
        conversion_factor = get_conversion_factor(item_code, uom).get("conversion_factor") or 1
        stock_qty=req_qty*flt(conversion_factor)
    else:
        stock_qty=req_qty
    
    qty=frappe.db.get_value('Bin', {'item_code': item_code,'warehouse':warehouse}, ['actual_qty as qty'],debug=0)
    qty=qty or 0
    
    if(int(stock_qty) > int(qty)):
        frappe.throw(_("There is no sufficient qty in {0} Please select another warehouse for {1}").format(warehouse,item_code))

@frappe.whitelist()
def update_item_stat(doc,event):
    if doc.own_packing:
        udoc = frappe.get_doc('Chicken Own Packing', doc.own_packing)
        if doc.manufacturing_type == "Chicken Slaughtering":
            udoc.item_processed = 1
            udoc.save()
