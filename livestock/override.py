# Copyright (c) 2022, alantechnologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_days, flt, get_datetime, get_time, get_url, nowtime, today
from erpnext.projects.doctype.project.project import Project
from frappe.model.document import Document

class HatcheryProject(Document):
	def onload(self):
		self.set_onload('activity_summary', frappe.db.sql('''select activity_type,
			sum(hours) as total_hours
			from `tabTimesheet Detail` where project=%s and docstatus < 2 group by activity_type
			order by total_hours desc''', self.name, as_dict=True))

		self.update_costing()
	def update_costing(self):
		from_time_sheet = frappe.db.sql("""select
			sum(costing_amount) as costing_amount,
			sum(billing_amount) as billing_amount,
			min(from_time) as start_date,
			max(to_time) as end_date,
			sum(hours) as time
			from `tabTimesheet Detail` where project = %s and docstatus = 1""", self.name, as_dict=1)[0]

		from_expense_claim = frappe.db.sql("""select
			sum(total_sanctioned_amount) as total_sanctioned_amount
			from `tabExpense Claim` where project = %s
			and docstatus = 1""", self.name, as_dict=1)[0]

		self.actual_start_date = from_time_sheet.start_date
		self.actual_end_date = from_time_sheet.end_date

		self.total_costing_amount = from_time_sheet.costing_amount
		self.total_billable_amount = from_time_sheet.billing_amount
		self.actual_time = from_time_sheet.time

		self.total_expense_claim = from_expense_claim.total_sanctioned_amount
		self.update_purchase_costing()
		self.update_sales_amount()
		self.update_billed_amount()

		if self.project_type=='Hatchery':
			self.calculate_tranfer_amount()

		self.calculate_gross_margin()


	def calculate_tranfer_amount(self):		
		amount=0		
		account = frappe.db.get_value('Hatchery Settings', self.hatchery, 'account')
		accu=frappe.db.get_list("Stock Entry",filters={'Project': self.name,'stock_entry_type':"Material Transfer","docstatus":'1'},fields=['name'])
		
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
		self.total_transfer_amount=amount


	def calculate_gross_margin(self):
		if self.project_type=='Hatchery':
			expense_amount = (flt(self.total_costing_amount) + flt(self.total_expense_claim)
                                + flt(self.total_purchase_cost) + flt(self.get('total_consumed_material_cost', 0)))
			inc=self.total_billed_amount+self.total_transfer_amount
			self.gross_margin = flt(inc) - expense_amount
			if inc:
				self.per_gross_margin = (self.gross_margin / flt(inc)) * 100
		else:
			expense_amount = (flt(self.total_costing_amount) + flt(self.total_expense_claim)
                        + flt(self.total_purchase_cost) + flt(self.get('total_consumed_material_cost', 0)))

			self.gross_margin = flt(self.total_billed_amount) - expense_amount
			if self.total_billed_amount:
				self.per_gross_margin = (self.gross_margin / flt(self.total_billed_amount)) * 100       

	def update_purchase_costing(self):
		total_purchase_cost = frappe.db.sql("""select sum(base_net_amount)
                        from `tabPurchase Invoice Item` where project = %s and docstatus=1""", self.name)

		self.total_purchase_cost = total_purchase_cost and total_purchase_cost[0][0] or 0


	def update_sales_amount(self):
		total_sales_amount = frappe.db.sql("""select sum(base_net_total)
                        from `tabSales Order` where project = %s and docstatus=1""", self.name)

		self.total_sales_amount = total_sales_amount and total_sales_amount[0][0] or 0

	def update_billed_amount(self):
		total_billed_amount = frappe.db.sql("""select sum(base_net_total)
                        from `tabSales Invoice` where project = %s and docstatus=1""", self.name)

		self.total_billed_amount = total_billed_amount and total_billed_amount[0][0] or 0
		
