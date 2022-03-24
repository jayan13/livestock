import frappe
#import erpnext

@frappe.whitelist()
def stock_entry(project):
    #print(doc.name)
    udoc = frappe.get_doc('Project', project)
    frappe.msgprint(""" projects  {0} """.format(udoc.project_name))
    if udoc.items:
        for item in udoc.items:
            #item.item_name
            frappe.msgprint(""" Items  {0} """.format(item.item_name))
        #udoc = frappe.get_doc('Poultry Items', doc)
        #print(f"{udoc.unit_no}")
        #udoc.contract_start_date = doc.contract_start_date        
        #udoc.save()        
    #frappe.throw("Error")