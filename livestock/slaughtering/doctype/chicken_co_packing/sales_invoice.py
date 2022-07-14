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
def sales_invoice(co_packing):

    from erpnext.stock.doctype.item.item import get_item_defaults    
    udoc = frappe.get_doc('Chicken Co Packing', co_packing)
    pos=frappe.get_doc('Co Packing Settings')
    sales = frappe.new_doc("Sales Invoice")
    #sales.pos_profile = udoc.pos_profile
    sales.cost_center=pos.cost_center
    sales.company=pos.company
    sales.set_warehouse=pos.warehouse
    sales.customer=udoc.customer
    sales.selling_price_list="Standard Selling"
    sales.taxes_and_charges=pos.taxes_and_charges
    sales.currency=pos.currency
    sales.chicken_co_packing=co_packing
    sales.update_stock=1

    if udoc.finished_items:
        for fitem in udoc.finished_items:
            item=frappe.get_doc('Item', fitem.item)
            item_account_details = get_item_defaults(fitem.item, pos.company)
            base_rate = frappe.db.get_value('Item Price', {'price_list': "Standard Selling",'item_code':fitem.item}, 'price_list_rate') 
            stock_uom = item_account_details.stock_uom
            conversion_factor = get_conversion_factor(fitem.item, fitem.uom).get("conversion_factor")
            cost_center=pos.cost_center or item_account_details.get("buying_cost_center")
            expense_account=item_account_details.get("expense_account")                
            item_name=item_account_details.get("item_name")
            precision = cint(frappe.db.get_default("float_precision")) or 3
            #base_row_rate = get_incoming_rate({
			#			"item_code": fitem.item,
			#			"warehouse": pos.warehouse,
			#			"posting_date": sales.posting_date,
			#			"posting_time": sales.posting_time,
			#			"qty": -1 * fitem.qty,
            #           'company':pos.company
			#		})
            #base_rate=base_row_rate or base_rate             
            amount=flt(flt(fitem.qty) * flt(base_rate), precision)
                
            sales.append('items', {
                    "amount": amount,
                    "base_amount": amount,
                    "base_net_amount": amount,
                    "base_net_rate": base_rate,
                    "base_price_list_rate": base_rate,
                    "base_rate": base_rate,
                    "conversion_factor": flt(conversion_factor),
                    "cost_center": cost_center,
                    "description":item.description,
                    "expense_account": pos.expense_account,
                    "income_account": pos.income_account,
                    "item_code": item.item_code,
                    "item_group": item.item_group,
                    "item_name": item.item_name,
                    "net_amount": amount,
                    "net_rate": base_rate,
                    "price_list_rate": base_rate,
                    "qty": fitem.qty,
                    "rate": base_rate,
                    "stock_qty": fitem.qty,
                    "stock_uom": stock_uom,
                    "stock_uom_rate": base_rate,
                    #"tax_amount": 0.83,
                    #"tax_rate": 5,
                    #"total_amount": 17.33,
                    #"total_weight": 0,
                    "uom": fitem.uom,
                    "warehouse": pos.warehouse,                   

			})

    return sales.as_dict()

@frappe.whitelist()
def update_item_stat(doc,event):
    if doc.chicken_co_packing:
        udoc = frappe.get_doc('Chicken Co Packing', doc.chicken_co_packing)
        udoc.item_processed = 1
        udoc.save()

@frappe.whitelist()
def cancel_item(doc,event):
    if doc.chicken_co_packing:
        udoc = frappe.get_doc('Chicken Co Packing', doc.chicken_co_packing)
        udoc.item_processed = 0
        udoc.save()
