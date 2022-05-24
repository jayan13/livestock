from itertools import product
import frappe
import erpnext
from frappe import _
from frappe.utils import cint, comma_or, cstr, flt, format_time, formatdate, getdate, nowdate
from erpnext.stock.get_item_details import (
	get_conversion_factor,
	get_default_cost_center,
)
#from erpnext.stock.doctype.stock_entry.stock_entry import get_uom_details

@frappe.whitelist()
def stock_entry(project):

    from erpnext.stock.doctype.item.item import get_item_defaults    
    udoc = frappe.get_doc('Project', project)
    sett = frappe.get_doc('Hatchery',udoc.hatchery)
    #items=[]
    #frappe.msgprint(""" projects  {0} """.format(udoc.project_name))
    if not sett:
        frappe.throw(_("Please add hatchery settings for {0} ").format(udoc.company))

    stock_entry = frappe.new_doc("Stock Entry")    
    stock_entry.company = udoc.company
    stock_entry.purpose = "Manufacture"
    stock_entry.stock_entry_type = "Manufacture"
    stock_entry.manufacturing_type = "Day Old Chicken"
    stock_entry.project = project
	#stock_entry.set_stock_entry_type()
    base_row_rate=0
    total_add_cost=0

    if sett.base_row_material:
        base_row_rate = frappe.db.get_value('Item Price', {'price_list': 'Standard Buying','item_code':sett.base_row_material}, 'price_list_rate')        
        item_account_details = get_item_defaults(sett.base_row_material, udoc.company)
        stock_uom = item_account_details.stock_uom
        conversion_factor = get_conversion_factor(sett.base_row_material, stock_uom).get("conversion_factor")
        cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
        expense_account=item_account_details.get("expense_account")
        
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
        frappe.throw(_("Please set base Rowmaterial in hatchery settings for {0} ").format(udoc.company))
    

    if udoc.items:
        for item in udoc.items:
            if item.s_warehouse or item.t_warehouse:
                item_account_details = get_item_defaults(item.item_code, udoc.company)
                #stock_uom = frappe.db.get_value("Item", item.item_code, "stock_uom")
                stock_uom = item_account_details.stock_uom
                conversion_factor = get_conversion_factor(item.item_code, item.uom).get("conversion_factor")
                cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
                expense_account=item_account_details.get("expense_account")                
                
                if item.s_warehouse:
                    validate_stock_qty(item.item_code,item.qty,item.s_warehouse,item.uom,stock_uom)                

                precision = cint(frappe.db.get_default("float_precision")) or 3    
                amount=flt(flt(item.qty) * flt(item.rate), precision)

                if sett.base_row_material != item.item_code:
                    total_add_cost=total_add_cost+amount
                

                stock_entry.append('items', {
					's_warehouse': item.s_warehouse,
                    't_warehouse': item.t_warehouse,
					'item_code': item.item_code,
					'qty': item.qty,
                    'actual_qty':item.qty,
					'uom': item.uom,
                    'cost_center':cost_center,					
					'ste_detail': item.name,
					'stock_uom': stock_uom,
                    'expense_account':expense_account,
                    'valuation_rate': item.rate,
                    "basic_rate":item.rate, 	
                    "basic_amount":amount,  
                    "amount":amount,  
                    "transfer_qty":item.qty,
					'conversion_factor': flt(conversion_factor),                    
				})
    
    tot_scrap= udoc.number_received - udoc.chicks_transferred
    
    if tot_scrap:
        item_account_details = get_item_defaults(sett.scrap, udoc.company)
        stock_uom = item_account_details.stock_uom
        conversion_factor = get_conversion_factor(sett.scrap, stock_uom).get("conversion_factor")
        cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
        expense_account=item_account_details.get("expense_account")                                
        precision = cint(frappe.db.get_default("float_precision")) or 3    
        amount=flt(flt(tot_scrap) * flt(base_row_rate), precision)
        stock_entry.append('items', {
                        't_warehouse': sett.scrap_target_warehouse,
                        'item_code': sett.scrap,
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
        
    if udoc.chicks_transferred:

        item_account_details = get_item_defaults(sett.product, udoc.company)
        stock_uom = item_account_details.stock_uom
        conversion_factor = get_conversion_factor(sett.product, stock_uom).get("conversion_factor")
        cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
        expense_account=item_account_details.get("expense_account")                                
        precision = cint(frappe.db.get_default("float_precision")) or 3
        cost=((udoc.chicks_transferred*base_row_rate) + total_add_cost) / udoc.chicks_transferred
        amount=flt(flt(udoc.chicks_transferred) * flt(cost), precision)
        stock_entry.append('items', {
                        't_warehouse': sett.product_target_warehouse,
                        'item_code': sett.product,
                        'qty': udoc.chicks_transferred,
                        'actual_qty':udoc.chicks_transferred,
                        'uom': stock_uom,
                        'cost_center':cost_center,					
                        'ste_detail': item_account_details.name,
                        'stock_uom': stock_uom,
                        'expense_account':expense_account,
                        'valuation_rate': cost,
                        "basic_rate":cost, 	
                        "basic_amount":amount,  
                        "amount":amount,  
                        "transfer_qty":udoc.chicks_transferred,
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

def add_stock_entry(item,project):
    frappe.msgprint(""" Item code  {0} """.format(item.item_code))

@frappe.whitelist()
def update_project_item_stat(doc,event):
    if doc.project:
        udoc = frappe.get_doc('Project', doc.project)
        if doc.manufacturing_type == "Day Old Chicken":
            udoc.item_processed = 1
            udoc.save()

@frappe.whitelist()
def project_item_tranfer_margin(project):
    amount=0    
    pjt=frappe.get_doc('Project',project) 
    account = frappe.db.get_value('Hatchery', pjt.hatchery, 'account')
    accu=frappe.db.get_list("Stock Entry",filters={'Project': project,'stock_entry_type':"Material Transfer","docstatus":'1'},fields=['name'])
    
    for ac in accu:
        
        acc=frappe.get_doc('Stock Entry',ac.name)        
        exp_amt=0
        base_amount=0
        is_add_cost=0        
        for cost in acc.additional_costs:
            if cost.expense_account==account:
                exp_amt+=cost.amount
                is_add_cost=1
        if is_add_cost==1:
            for item in acc.items:
                base_amount+=item.basic_amount

        amount+=exp_amt+base_amount
        
    return amount
