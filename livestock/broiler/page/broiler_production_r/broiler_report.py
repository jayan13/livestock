import frappe

@frappe.whitelist()
def get_company_list():
    data = {}
    data["companys"] = frappe.get_list("Company", fields=['name'],limit_page_length=0, order_by="name",debug=0)
    return data
    
@frappe.whitelist()
def get_report(company=None,posted_on=None):
    data = {}
    if not company:
        company="ABU DHABI MODERNE POULTRY FARM L.L.C.";
        
    data['company']=company
    data['posted_on']=posted_on
    

    return data


       
    

    
    