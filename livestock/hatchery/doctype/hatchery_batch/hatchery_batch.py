# Copyright (c) 2022, alantechnologies and contributors
# For license information, please see license.txt

from distutils.log import debug
import frappe
from frappe.utils import nowdate
from frappe.model.document import Document
from erpnext.projects.doctype.project.project import Project

class HatcheryBatch(Document):
	def before_insert(self):
		shed=frappe.get_doc("Hatchery Settings", self.hatchery)
		project = frappe.new_doc("Project")
		project.project_name=self.hatchery_batch_name
		project.project_type="Hatchery"
		project.hatchery=self.hatchery
		project.expected_start_date=self.setting_date
		#project.expected_end_date=self.date_of_hatching
		project.company=shed.company
		project.cost_center=shed.cost_center
		project.insert(ignore_permissions=True)
		self.project=project.name

	def after_insert(self):
		pjt=frappe.get_doc("Project", self.project)
		pjt.hatchery_batch=self.name
		pjt.save()

	def on_update(self):
		pjt=frappe.get_doc("Project", self.project)
		
		if pjt.status!=self.status:
			pjt.status=	self.status
			if self.status=='Completed':
				pjt.expected_end_date=nowdate()
			pjt.save()


def update_transfer_amount():		
	exists_query = '(SELECT 1 from `tab{doctype}` where docstatus = 1 and project = `tabProject`.name and stock_entry_type="Material Transfer" and (CURDATE() between DATE(modified)  and DATE_ADD(DATE(modified), INTERVAL 2 DAY)))'
	project_map = {}
	for project_details in frappe.db.sql('''
				SELECT name, 1 as order_exists, null as invoice_exists from `tabProject` where
				exists {order_exists} and project_type="Hatchery"
			'''.format(
				order_exists=exists_query.format(doctype="Stock Entry")
			), as_dict=True):
		project = project_map.setdefault(project_details.name, frappe.get_doc('Project', project_details.name))
		
		if project_details.order_exists:
			project.calculate_tranfer_amount()
			#will call override project class - livestock/override.py
			
	for project in project_map.values():
		project.save()

def update_project_costing(doc,event):
	if doc.project:		
		project=frappe.get_doc('Project', doc.project)
		if project.hatchery and project.project_type=='Hatchery':
			project.update_costing_from_trn(doc)
			project.save()

def cancel_project_costing(doc,event):		
	if doc.project:
		project=frappe.get_doc('Project', doc.project)
		if project.hatchery and project.project_type=='Hatchery':
			project.cancel_costing_from_trn(doc)
			project.save()
