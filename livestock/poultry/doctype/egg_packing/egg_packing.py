# Copyright (c) 2023, alantechnologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import erpnext
from frappe import _
from frappe.utils import nowdate, cint, get_datetime, formatdate, getdate, flt
from frappe.model.document import Document
from erpnext.stock.utils import (get_incoming_rate)
from erpnext.stock.get_item_details import (get_conversion_factor)
from erpnext.stock.doctype.item.item import get_item_defaults

class EggPacking(Document):
	def before_submit(self):
		
		times=get_datetime()
		posting_time=times.strftime("%H:%M:%S")
		posting_date=getdate(self.date)
		
		stock_entry = frappe.new_doc("Stock Entry")    
		stock_entry.company = self.company
		stock_entry.letter_head = frappe.db.get_value('Company',self.company,'default_letter_head') or 'No Letter Head'    
		stock_entry.posting_date = posting_date
		stock_entry.posting_time = posting_time
		stock_entry.set_posting_time='1'
		stock_entry.purpose = "Manufacture"
		stock_entry.stock_entry_type = "Manufacture"
		stock_entry.manufacturing_type = "Egg"
		pcitems=[]
		
		pcmaterials=''
		if self.bom:
			pcmaterials=frappe.get_doc('Finished Product BOM',self.bom)
		else:
			bom=frappe.db.get_value('Finished Product BOM',{'item':self.item,'uom':self.uom,'is_default':'1'},'name')
			if not bom:
				bom=frappe.db.get_value('Finished Product BOM',{'item':self.item,'uom':self.uom},'name')
			if bom:
				pcmaterials=frappe.get_doc('Finished Product BOM',bom)
			
		precision = 6
		itemscost=0
		item_account_details = get_item_defaults(self.item, self.company)
		stock_adjustment_account=frappe.db.get_value('Company',self.company,'stock_adjustment_account')
		if pcmaterials:
			for pcitem in pcmaterials.packing_item:
				pack_item_details = get_item_defaults(pcitem.item, self.company)
				stock_uom = pack_item_details.stock_uom
				conversion_factor = get_conversion_factor(pcitem.item, pcitem.uom).get("conversion_factor")
				cost_center=pack_item_details.get("buying_cost_center")
					#expense_account=pack_item_details.get("expense_account")		
				expense_account=stock_adjustment_account or item_account_details.get("expense_account")                
				item_name=pack_item_details.get("item_name")
				packed_qty=float(pcitem.qty)*float(self.qty)
				pck_rate = get_incoming_rate({
									"item_code": pcitem.item,
									"warehouse": self.packing_warehouse,
									"posting_date": posting_date,
									"posting_time": posting_time,
									"qty": -1 * packed_qty,
									'company':self.company
								}) or 0
											
				transfer_qty=flt(float(packed_qty) * float(conversion_factor),6)
				amount=flt(float(transfer_qty) * float(pck_rate), precision)
				itemscost+=transfer_qty * pck_rate
					#pcitems.append({
				stock_entry.append('items', {
								's_warehouse': self.packing_warehouse,
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
								"transfer_qty":transfer_qty,
								'conversion_factor': flt(conversion_factor),
								}) 

		stock_uom = item_account_details.stock_uom
		conversion_factor = get_conversion_factor(self.item, self.uom).get("conversion_factor")
		cost_center=item_account_details.get("buying_cost_center")
			#expense_account=item_account_details.get("expense_account")
		expense_account=stock_adjustment_account or item_account_details.get("expense_account")                
		item_name=item_account_details.get("item_name")
		base_rate=0

		batch_no=''
		if item_account_details.has_batch_no:
			manufacture_date=posting_date
			itemname=str(self.item)
			itemname=itemname[0:2]
			cat='Layer Eggs'
			pre_fix=frappe.db.get_value('Egg Finished Item Production Settings',{'item_code':self.item,'category':cat},'batch_prefix')
			pre_fix= pre_fix or itemname
			batch_no=str(pre_fix)+'-'+str(manufacture_date)		
			if not frappe.db.exists("Batch", {"name": batch_no}):
				batch = frappe.new_doc("Batch")
				batch.batch_id=batch_no
				batch.item=self.item
				batch.item_name=item_name
				batch.batch_qty=self.qty
				batch.manufacturing_date=posting_date
				batch.stock_uom=stock_uom
				batch.insert()
		stock_uom_rate=0
		if itemscost:
			base_rate=itemscost/float(self.qty)
			stock_uom_rate=base_rate/conversion_factor		
		amount=float(self.qty) * float(base_rate)
		pcitems.append({            
							't_warehouse': self.target_warehouse,
							'item_code': self.item,
							'qty': self.qty,
							'actual_qty':self.qty,
							'uom': self.uom,
							'cost_center':cost_center,					
							'ste_detail': item_name,
							'stock_uom': stock_uom,
							'expense_account':expense_account,
							'valuation_rate': stock_uom_rate,
							"basic_rate":stock_uom_rate, 	
							"basic_amount":amount,  
							"amount":amount,  
							"transfer_qty":self.qty,
							'conversion_factor': flt(conversion_factor),
							'is_finished_item':1,
							'set_basic_rate_manually':1,
							'batch_no':batch_no,                  
					})

		for pc in pcitems:
			stock_entry.append('items',pc)

		stock_entry.insert()
		stock_entry.submit()
		#stock_entry.docstatus=1
		stock_entry.save()

		self.stock_entry=stock_entry.name

	def on_cancel(self):
		doc=frappe.get_doc('Stock Entry',self.stock_entry)
		doc.cancel()
		doc.save()

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def item_list(doctype, txt, searchfield, start, page_len, filters):
	return frappe.get_all(
		"Finished Product BOM",
		fields=['item as name'],group_by='item',
		as_list=1,
	)
