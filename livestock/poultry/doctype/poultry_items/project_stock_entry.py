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
    #items=[]
    #frappe.msgprint(""" projects  {0} """.format(udoc.project_name))
    stock_entry = frappe.new_doc("Stock Entry")    
    stock_entry.company = udoc.company
    stock_entry.purpose = "Manufacture"
    stock_entry.stock_entry_type = "Manufacture"
    stock_entry.manufacturing_type = "Day Old Chicken"
    stock_entry.project = project
	#stock_entry.set_stock_entry_type()
    if udoc.items:
        for item in udoc.items:
            if item.s_warehouse or item.t_warehouse:
                item_account_details = get_item_defaults(item.item_code, udoc.company)
                #stock_uom = frappe.db.get_value("Item", item.item_code, "stock_uom")
                stock_uom = item_account_details.stock_uom
                conversion_factor = get_conversion_factor(item.item_code, item.uom).get("conversion_factor")
                cost_center=udoc.cost_center or item_account_details.get("buying_cost_center")
                expense_account=item_account_details.get("expense_account")
                
                if item.is_finished_item!=1 and item.is_scrap_item !=1:
                    if item.s_warehouse:
                        validate_stock_qty(item.item_code,item.qty,item.s_warehouse,item.uom,stock_uom)
                    #frappe.msgprint(""" Items  {0} """.format(item.item_name))
                #else:
                    #add_stock_entry(item,project)
                precision = cint(frappe.db.get_default("float_precision")) or 3    
                amount=flt(flt(item.qty) * flt(item.rate), precision)
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
                    'is_finished_item':item.is_finished_item,
                    'is_scrap_item':item.is_scrap_item,
				})
            #else:
            #    frappe.throw(_("Please select warehouse for {0}").format(item.item_name))

                
                #item.item_name                    
            #frappe.msgprint(""" Items  {0} """.format(item.item_name))
        #udoc = frappe.get_doc('Poultry Items', doc)
        #print(f"{udoc.unit_no}")
        #udoc.contract_start_date = doc.contract_start_date        
        #udoc.save()        
    #frappe.throw("Error")
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
