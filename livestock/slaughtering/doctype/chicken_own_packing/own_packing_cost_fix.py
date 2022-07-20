import frappe
from frappe.utils import flt
def fix_cost():
    frappe.db.sql("""SET SQL_SAFE_UPDATES = 0""")
    frappe.db.sql(""" update `tabOwn Packing List` set updated_qty='0',is_billing_updated='0' """)
    frappe.db.sql(""" update `tabProject` set own_packing_selling_cost='0' """)
    frappe.db.sql(""" SET SQL_SAFE_UPDATES = 1 """)
    frappe.db.truncate("Own Pack Sales Cost")
    sales=frappe.db.sql(""" select name,posting_date,is_return from `tabSales Invoice` where company='ABU DHABI MODERNE POULTRY FARM L.L.C.' and posting_date>'2022-06-29' and docstatus=1 and is_return<>1 order by posting_date""",as_dict=1)
    itemgp=['CHICKEN PRODUCTS - ACACIA','CHICKEN PRODUCTS - AL FAKHER','CHICKEN PRODUCTS - AUH']
    for inv in sales:
        #print(str(inv.name)+"-"+str(inv.is_return)+'-'+str(inv.posting_date))
        sinv=frappe.get_doc('Sales Invoice', inv.name)
        for i in sinv.items:
            group,weight=frappe.db.get_value('Item', i.item_code, ['item_group','weight_per_unit'])
            if group in itemgp:
                qty=i.qty
                rate=i.rate
                if i.uom=='Kg':
                    qty=flt(i.qty/weight,4)
                    rate=flt(i.rate*weight,4)
                #print(str(i.item_code)+" - "+str(i.qty)) amount
                #if i.item_code=='CCPR0007':
                    #print(str(inv.posting_date)+"-"+str(i.item_code)+" - "+str(i.qty))
                update_project(sinv,i.item_code,qty,rate,i.production_date) 

    print("db updated")    
    #frappe.db.commit()

def update_project(doc,item_code,qty,rate,production_date):

    if doc.is_return:
        own_pack=''
        if production_date:
            own_pack=frappe.db.sql("""select l.item,o.project,l.name,l.updated_qty,l.qty from 
        `tabOwn Packing List` l left join `tabChicken Own Packing` o  on l.parent=o.name left join `tabProject` p on p.name=o.project where  
         o.date='{0}' and l.updated_qty > 0 and o.item_processed=1 and p.status='Open' and l.item='{1}' order by o.`date` limit 0,1 """.format(production_date, item_code),as_dict=1,debug=0)
        if not own_pack:
            own_pack=frappe.db.sql("""select l.item,o.project,l.name,l.updated_qty,l.qty from 
        `tabOwn Packing List` l left join `tabChicken Own Packing` o  on l.parent=o.name left join `tabProject` p on p.name=o.project where  
         (o.date between DATE_SUB('{0}', INTERVAL 3 DAY) and '{1}') and l.updated_qty > 0 and o.item_processed=1 and p.status='Open' and l.item='{2}' order by o.`date` limit 0,1 """.format(doc.posting_date, doc.posting_date, item_code),as_dict=1,debug=0)
        
        if own_pack:            
            if own_pack[0]['updated_qty'] >= abs(qty):
                selling_cost=frappe.db.get_value('Project', own_pack[0]['project'], ['own_packing_selling_cost']) or 0
                selling_cost=selling_cost+(qty*rate)
                updated_qty=own_pack[0]['updated_qty']-abs(qty)
                frappe.db.set_value('Own Packing List', own_pack[0]['name'], {'updated_qty':updated_qty,'is_billing_updated':'0'})
                frappe.db.set_value('Project', own_pack[0]['project'], 'own_packing_selling_cost', selling_cost)
                project=frappe.get_doc('Project', own_pack[0]['project'])
                project.update_costing()
                project.save()
                sales_cost=frappe.new_doc("Own Pack Sales Cost") #used when sales invoice canceled - removing sales cost from projects
                sales_cost.sales_invoice=doc.name
                sales_cost.project=own_pack[0]['project']
                sales_cost.item=item_code
                sales_cost.amount=qty*rate
                sales_cost.qty=qty
                sales_cost.own_pack_list=own_pack[0]['name']
                sales_cost.insert(ignore_permissions=True)
            else:
                remqty=own_pack[0]['updated_qty']+qty
                reqty=own_pack[0]['updated_qty']*-1
                selling_cost=frappe.db.get_value('Project', own_pack[0]['project'], ['own_packing_selling_cost']) or 0
                selling_cost=selling_cost+(reqty*rate)
                frappe.db.set_value('Own Packing List', own_pack[0]['name'], {'updated_qty':'0','is_billing_updated':'0'})
                frappe.db.set_value('Project', own_pack[0]['project'], 'own_packing_selling_cost', selling_cost)
                project=frappe.get_doc('Project', own_pack[0]['project'])
                project.update_costing()
                project.save()
                sales_cost=frappe.new_doc("Own Pack Sales Cost") #used when sales invoice canceled - removing sales cost from projects
                sales_cost.sales_invoice=doc.name
                sales_cost.project=own_pack[0]['project']
                sales_cost.item=item_code
                sales_cost.amount=reqty*rate
                sales_cost.qty=reqty
                sales_cost.own_pack_list=own_pack[0]['name']
                sales_cost.insert(ignore_permissions=True)
                update_project(doc,item_code,remqty,rate,production_date)
    else:
        sql="""select l.item,o.project,l.name,l.updated_qty,l.qty from 
        `tabOwn Packing List` l left join `tabChicken Own Packing` o  on l.parent=o.name left join `tabProject` p on p.name=o.project where l.is_billing_updated<>'1' 
        and o.date <= '{0}' and o.item_processed=1 and p.status='Open' and l.item='{1}' order by o.`date` limit 0,1 """.format(doc.posting_date,item_code)
        #print(sql)
        own_pack=frappe.db.sql(sql, as_dict=1,debug=0)
        
        if own_pack:
            remqty=own_pack[0]['qty']-own_pack[0]['updated_qty']
            if qty > remqty:
                ownqty=qty-remqty
                selling_cost=frappe.db.get_value('Project', own_pack[0]['project'], ['own_packing_selling_cost']) or 0
                selling_cost=selling_cost+(remqty*rate)
                frappe.db.set_value('Own Packing List', own_pack[0]['name'], {'updated_qty':own_pack[0]['qty'],'is_billing_updated':'1'})
                frappe.db.set_value('Project', own_pack[0]['project'], 'own_packing_selling_cost', selling_cost)
                
                project=frappe.get_doc('Project', own_pack[0]['project'])
                project.update_costing()
                project.save()
                sales_cost=frappe.new_doc("Own Pack Sales Cost") #used when sales invoice canceled - removing sales cost from projects
                sales_cost.sales_invoice=doc.name
                sales_cost.project=own_pack[0]['project']
                sales_cost.item=item_code
                sales_cost.amount=remqty*rate
                sales_cost.qty=remqty
                sales_cost.own_pack_list=own_pack[0]['name']
                sales_cost.insert(ignore_permissions=True)

                update_project(doc,item_code,ownqty,rate,production_date)
            else:
                cqty=remqty-qty
                selling_cost=frappe.db.get_value('Project', own_pack[0]['project'], ['own_packing_selling_cost']) or 0
                selling_cost=selling_cost+(qty*rate)
                frappe.db.set_value('Project', own_pack[0]['project'], 'own_packing_selling_cost', selling_cost)
                upqty=own_pack[0]['updated_qty']+qty
                frappe.db.set_value('Own Packing List', own_pack[0]['name'], 'updated_qty',upqty)    
                if cqty==0:
                    frappe.db.set_value('Own Packing List', own_pack[0]['name'], 'is_billing_updated', '1')

                project=frappe.get_doc('Project', own_pack[0]['project'])
                project.update_costing()
                project.save()
                sales_cost=frappe.new_doc("Own Pack Sales Cost")
                sales_cost.sales_invoice=doc.name
                sales_cost.project=own_pack[0]['project']
                sales_cost.item=item_code
                sales_cost.amount=qty*rate
                sales_cost.own_pack_list=own_pack[0]['name']
                sales_cost.qty=qty
                sales_cost.insert(ignore_permissions=True)
