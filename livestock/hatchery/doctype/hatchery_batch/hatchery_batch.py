# Copyright (c) 2022, alantechnologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate
from frappe.model.document import Document

class HatcheryBatch(Document):
	def before_insert(self):
		shed=frappe.get_doc("Hatchery Settings", self.hatchery)
		project = frappe.new_doc("Project")
		project.project_name=self.hatchery_batch_name
		project.project_type="Hatchery"
		project.expected_start_date=self.setting_date
		#project.expected_end_date=self.date_of_hatching
		project.company=shed.company
		project.cost_center=shed.cost_center
		project.insert(ignore_permissions=True)
		self.project=project.name

	def on_update(self):
		pjt=frappe.get_doc("Project", self.project)
		
		if pjt.status!=self.status:
			pjt.status=	self.status
			if self.status=='Completed':
				pjt.expected_end_date=nowdate()
			pjt.save()
			

