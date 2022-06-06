# Copyright (c) 2022, alantechnologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate
from frappe.model.document import Document

class BroilerBatch(Document):
	def before_insert(self):		
		shed=frappe.get_doc("Broiler Shed", self.broiler_shed)
		project = frappe.new_doc("Project")
		project.project_name=self.broiler_batch_name
		project.project_type="Broiler"
		project.expected_start_date=self.start_date
		project.expected_end_date=self.end_date
		project.company=shed.company
		project.cost_center=shed.cost_center
		project.insert(ignore_permissions=True)
		self.project=project.name

	def after_insert(self):
		pjt=frappe.get_doc("Project", self.project)
		pjt.broiler_batch=self.name
		pjt.save()

	def on_update(self):
		pjt=frappe.get_doc("Project", self.project)
		
		if pjt.status!=self.status:
			pjt.status=	self.status
			if self.status=='Completed':
				pjt.expected_end_date=nowdate()
			pjt.save()