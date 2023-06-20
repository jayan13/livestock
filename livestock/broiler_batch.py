# Copyright (c) 2022, alantechnologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate
from frappe.model.document import Document

@frappe.whitelist()
def update_feed():
    t=0
    feed=frappe.db.get_all('Feed',fields=['sum(starter_qty) as sqty','sum(finisher_qty) as fqty,parent'],group_by='parent')
    for f in feed:
        frappe.db.set_value('Broiler Batch',f.parent,{'total_starter_qty':f.sqty,'total_finisher_qty':f.fqty})

    return "Total Updated"
        


