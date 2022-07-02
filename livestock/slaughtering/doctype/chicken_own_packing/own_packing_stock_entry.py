from itertools import product
import frappe
import erpnext
from frappe import _
from frappe.utils import cint, comma_or, cstr, flt, format_time, formatdate, getdate, nowdate
from erpnext.stock.get_item_details import (
	get_conversion_factor,
	get_default_cost_center,
)
from erpnext.stock.utils import (get_incoming_rate)
#from erpnext.stock.doctype.stock_entry.stock_entry import get_uom_details

@frappe.whitelist()
def stock_entry(own_packing):

    from erpnext.stock.doctype.item.item import get_item_defaults    
    udoc = frappe.get_doc('Chicken Own Packing', own_packing)
    sett = frappe.get_doc('Own Packing Settings')
    stock_entry = frappe.new_doc("Stock Entry")    
    stock_entry.company = udoc.company
    #stock_entry.project = udoc.project
    stock_entry.purpose = "Manufacture"
    stock_entry.stock_entry_type = "Manufacture"
    stock_entry.manufacturing_type = "Chicken Slaughtering"
    stock_entry.chicken_own_packing=own_packing
	#stock_entry.set_stock_entry_type()
    precision = cint(frappe.db.get_default("float_precision")) or 3
    base_row_rate=0
    row_cost=0
    
    if udoc.item:
        #base_row_rate = frappe.db.get_value('Item Price', {'price_list': 'Standard Buying','item_code':udoc.item}, 'price_list_rate')        
        item_account_details = get_item_defaults(udoc.item, udoc.company)
        stock_uom = item_account_details.stock_uom
        conversion_factor = get_conversion_factor(udoc.item, stock_uom).get("conversion_factor")
        cost_center=sett.cost_center or item_account_details.get("buying_cost_center")
        expense_account=item_account_details.get("expense_account")        
        base_row_rate = get_incoming_rate({
						"item_code": udoc.item,
						"warehouse": udoc.warehouse,
						"posting_date": stock_entry.posting_date,
						"posting_time": stock_entry.posting_time,
						"qty": -1 * udoc.number_of_chicken,
                        'company':udoc.company
					})
        if udoc.warehouse:
            validate_stock_qty(udoc.item,udoc.number_of_chicken,udoc.warehouse,stock_uom,stock_uom)
            
        amount=flt(udoc.number_of_chicken) * base_row_rate
        row_cost+=amount
        stock_entry.append('items', {
                        's_warehouse': udoc.warehouse,
                        'item_code': udoc.item,
                        'qty': udoc.number_of_chicken,
                        'actual_qty':udoc.number_of_chicken,
                        'uom': stock_uom,
                        'cost_center':cost_center,					
                        'ste_detail': item_account_details.name,
                        'stock_uom': stock_uom,
                        'expense_account':expense_account,
                        'valuation_rate': base_row_rate,
                        "basic_rate":base_row_rate, 	
                        "basic_amount":amount,  
                        "amount":amount,  
                        "transfer_qty":udoc.number_of_chicken,
                        'conversion_factor': flt(conversion_factor),
                                  
        })
    else:
        frappe.throw(_("Please enter processing item "))
    

    if udoc.finished_items:
        total_finished_item=0        
        
        for fitem in udoc.finished_items:
            item_account_details = get_item_defaults(fitem.item, udoc.company)            
            weight_per_unit=item_account_details.get("weight_per_unit")
            weight_uom=item_account_details.get("weight_uom")
            #if weight_uom=='Kg':
                #weight_per_unit=weight_per_unit*1000
            total_finished_item+=int(fitem.qty)*weight_per_unit

        unit_cost=(row_cost/total_finished_item)
        
        pcitems=[]
        for fitem in udoc.finished_items:
            
            itemscost=0
            item_account_details = get_item_defaults(fitem.item, udoc.company)
            pcmaterials=frappe.get_doc('Packing Materials',fitem.item)           
            
            for pcitem in pcmaterials.packing_item:
                pack_item_details = get_item_defaults(pcitem.item, udoc.company)
                stock_uom = pack_item_details.stock_uom
                conversion_factor = get_conversion_factor(pcitem.item, pcitem.uom).get("conversion_factor")
                cost_center=sett.cost_center or pack_item_details.get("buying_cost_center")
                expense_account=pack_item_details.get("expense_account")                
                item_name=pack_item_details.get("item_name")
                packed_qty=float(pcitem.qty)*float(fitem.qty)
                pck_rate = get_incoming_rate({
						"item_code": pcitem.item,
						"warehouse": sett.packing_item_warehouse,
						"posting_date": stock_entry.posting_date,
						"posting_time": stock_entry.posting_time,
						"qty": -1 * packed_qty,
                        'company':udoc.company
					})
                                
                transfer_qty=flt(flt(packed_qty) * flt(conversion_factor))
                amount=flt(flt(transfer_qty) * flt(pck_rate), 2)
                itemscost+=amount
                stock_entry.append('items', {
                    's_warehouse': sett.packing_item_warehouse,
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
                    'set_basic_rate_manually':1                    
			        })    
                


            #base_rate = frappe.db.get_value('Item Price', {'price_list': 'Standard Selling','item_code':fitem.item}, 'price_list_rate') 
            stock_uom = item_account_details.stock_uom
            conversion_factor = get_conversion_factor(fitem.item, fitem.uom).get("conversion_factor")
            cost_center=sett.cost_center or item_account_details.get("buying_cost_center")
            expense_account=item_account_details.get("expense_account")                
            item_name=item_account_details.get("item_name")
            #weight_per_unit=item_account_details.get("weight_per_unit")
            packing_rate_of_item=itemscost/float(fitem.qty)
            base_rate=packing_rate_of_item+(unit_cost*item_account_details.weight_per_unit)
            amount=flt(flt(fitem.qty) * base_rate, precision)
            pcitems.append({            
                    't_warehouse': sett.warehouse,
					'item_code': fitem.item,
					'qty': fitem.qty,
                    'actual_qty':fitem.qty,
					'uom': fitem.uom,
                    'cost_center':cost_center,					
					'ste_detail': item_name,
					'stock_uom': stock_uom,
                    'expense_account':expense_account,
                    'valuation_rate': base_rate,
                    "basic_rate":base_rate, 	
                    "basic_amount":amount,  
                    "amount":amount,  
                    "transfer_qty":fitem.qty,
					'conversion_factor': flt(conversion_factor),
                    'is_finished_item':1,
                    'set_basic_rate_manually':1                  
			})

        for pc in pcitems:
            stock_entry.append('items',pc)

    if udoc.mortality_while_receving or udoc.number_of_culls:
        tot_scrap=udoc.mortality_while_receving+udoc.number_of_culls
        item_account_details = get_item_defaults(sett.scrap_item, udoc.company)
        stock_uom = item_account_details.stock_uom
        conversion_factor = get_conversion_factor(sett.scrap_item, stock_uom).get("conversion_factor")
        cost_center=sett.cost_center or udoc.cost_center or item_account_details.get("buying_cost_center")
        expense_account=item_account_details.get("expense_account")                                
        precision = cint(frappe.db.get_default("float_precision")) or 3    
        amount=flt(flt(tot_scrap) * flt(base_row_rate), precision)
        stock_entry.append('items', {
                        't_warehouse': sett.scrap_item_warehouse,
                        'item_code': sett.scrap_item,
                        'qty': tot_scrap,
                        'actual_qty':tot_scrap,
                        'uom': stock_uom,
                        'cost_center':cost_center,					
                        'ste_detail': item_account_details.name,
                        'stock_uom': stock_uom,
                        'expense_account':expense_account,
                        'valuation_rate': base_row_rate,
                        "basic_rate":base_row_rate, 	
                        "basic_amount":amount,  
                        "amount":amount,  
                        "transfer_qty":tot_scrap,
                        'conversion_factor': flt(conversion_factor),
                        'is_scrap_item':1,                                           
        })

    return stock_entry.as_dict()

def validate_stock_qty(item_code,req_qty,warehouse,uom,stock_uom):
    if uom != stock_uom:
        conversion_factor = get_conversion_factor(item_code, uom).get("conversion_factor") or 1
        stock_qty=req_qty*flt(conversion_factor)
    else:
        stock_qty=req_qty
    
    qty=frappe.db.get_value('Bin', {'item_code': item_code,'warehouse':warehouse}, ['actual_qty as qty'],debug=0)
    qty=qty or 0
    
    if(int(stock_qty) > int(qty)):
        frappe.throw(_("There is no sufficient qty in {0} Please select another warehouse for {1}").format(warehouse,item_code))

@frappe.whitelist()
def update_item_stat(doc,event):
    if doc.chicken_own_packing:
        udoc = frappe.get_doc('Chicken Own Packing', doc.chicken_own_packing)
        if doc.manufacturing_type == "Chicken Slaughtering":
            udoc.item_processed = 1
            udoc.save()

def update_selling_cost(doc,event):
    itemary=[]
    ownpacking_items=frappe.db.sql("select d.item_code from `tabStock Entry Detail` d left join `tabStock Entry` s  on d.parent=s.name where s.manufacturing_type='Chicken Slaughtering' and d.is_finished_item=1 group by d.item_code",as_dict=1)
    
    for it in ownpacking_items:
        itemary.append(str(it.item_code))
    
    for i in doc.items:
        if i.item_code in itemary:
            update_project(doc,i.item_code,i.qty,i.rate)
            


def update_project(doc,item_code,qty,rate):

    own_pack=frappe.db.sql("""select l.item,o.project,l.name,l.updated_qty,l.qty from 
    `tabOwn Packing List` l left join `tabChicken Own Packing` o  on l.parent=o.name where l.is_billing_updated<>'1' 
    and o.item_processed=1 and l.item=%s order by o.`date` limit 0,1 """, item_code,as_dict=1)
    
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
        sales_cost=frappe.new_doc("Own Pack Sales Cost")
        sales_cost.sales_invoice=doc.name
        sales_cost.project=own_pack[0]['project']
        sales_cost.item=item_code
        sales_cost.amount=remqty*rate
        sales_cost.qty=remqty
        sales_cost.own_pack_list=own_pack[0]['name']
        sales_cost.insert(ignore_permissions=True)

        update_project(doc,item_code,ownqty,rate)
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

def cancel_selling_cost(doc,event):
    own_pack=frappe.db.sql("""select sum(amount) as amount,project from  `tabOwn Pack Sales Cost`  
    where sales_invoice=%s group by project""", doc.name,as_dict=1)
    for pck in own_pack:
        project=frappe.get_doc('Project', pck.project)
        project.own_packing_selling_cost=project.own_packing_selling_cost-pck.amount
        project.update_costing()
        project.save()

    own_pack_list=frappe.db.sql("""select qty,own_pack_list,item,name from  `tabOwn Pack Sales Cost` where sales_invoice=%s """, doc.name,as_dict=1)
    for pklist in own_pack_list:        
        updated_qty=frappe.db.get_value('Own Packing List', pklist.own_pack_list, ['updated_qty']) or 0
        updated_qty=updated_qty-pklist.qty
        frappe.db.set_value('Own Packing List', pklist.own_pack_list, {'updated_qty':updated_qty,'is_billing_updated':'0'})
        frappe.db.delete('Own Pack Sales Cost',{'name':pklist.name})
    


