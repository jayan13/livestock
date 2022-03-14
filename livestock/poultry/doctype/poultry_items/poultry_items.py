# Copyright (c) 2022, alantechnologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PoultryItems(Document):
	pass

@frappe.whitelist()
def get_item_stock_uom(item_code):
	suom=frappe.db.get_value('Stock Entry Detail', {'item_code': item_code}, ['stock_uom'],debug=1)
	if suom:
		data=suom
	else:
		suom=frappe.db.get_value('Stock Entry Detail', {'item_code': item_code}, ['uom'],debug=1)
		if suom:
			data=suom
		else:
			suom=frappe.db.get_value('Item Price', {'item_code': item_code,'price_list':'Standard Buying'}, ['uom'],debug=1)
			if suom:
				data=suom
			else:
				data=frappe.db.get_value('Item Price', {'item_code': item_code}, ['uom'],debug=1)

	return data