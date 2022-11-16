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
from erpnext.stock.stock_ledger import get_valuation_rate
#from erpnext.stock.doctype.stock_entry.stock_entry import get_uom_details

@frappe.whitelist()
def stock_entry(own_packing):

    from erpnext.stock.doctype.item.item import get_item_defaults    
    udoc = frappe.get_doc('Chicken Own Packing', own_packing)
    sett = frappe.get_doc('Own Packing Settings')
    stock_entry = frappe.new_doc("Stock Entry")    
    stock_entry.company = udoc.company     
    ownpacktime=format_time(str(udoc.creation))
    stock_entry.posting_date = udoc.date
    stock_entry.posting_time = ownpacktime
    stock_entry.set_posting_time='1'
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
                        "qty": -1*flt(udoc.number_of_chicken),
			            "voucher_type": stock_entry.doctype,
			            "voucher_no": stock_entry.name,
			            "company": stock_entry.company,
			            "allow_zero_valuation": '',
					})
                    
        if udoc.warehouse:
            validate_stock_qty(udoc.item,udoc.number_of_chicken,udoc.warehouse,stock_uom,stock_uom)

        

        amount=flt(udoc.number_of_chicken * flt(base_row_rate),precision)
        row_cost+=(udoc.number_of_chicken * base_row_rate)
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

        unit_cost=(row_cost/flt(total_finished_item,3))
        
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
                                
                transfer_qty=flt(flt(packed_qty) * flt(conversion_factor),2)
                amount=flt(flt(transfer_qty) * flt(pck_rate), precision)
                itemscost+=transfer_qty * pck_rate
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
            amount=flt(fitem.qty) * base_rate
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

    

    return stock_entry.as_dict()

@frappe.whitelist()
def re_packing(own_packing):
    udoc = frappe.get_doc('Chicken Own Packing', own_packing)
    sett = frappe.get_doc('Own Packing Settings')
    own_repk = frappe.new_doc("Own Re Packing")
    own_repk.own_packing=udoc.name
    own_repk.own_paking_date=udoc.date
    own_repk.source_warehouse=sett.warehouse
    own_repk.traget_warehouse=sett.warehouse
    own_repk.packing_item_warehouse=sett.packing_item_warehouse
    
    for fitem in udoc.finished_items:
        if fitem.qty > fitem.updated_qty:
            vrate=frappe.db.sql("""select d.valuation_rate from `tabStock Entry Detail` d left join `tabStock Entry` s on s.name=d.parent where d.item_code ='{0}' and s.chicken_own_packing='{1}' and s.docstatus=1 order by s.creation  """.format(fitem.item_code,own_packing),as_dict=1)[0]
            own_repk.append('re_packing_items', {
                    'item_code': fitem.item_code,
                    'item_name':fitem.item_name,
					'old_item_qty': fitem.qty,
                    'old_item_avail_qty': fitem.qty-fitem.updated_qty,
                    'old_uom':fitem.uom,
                    'old_item_rate': vrate.valuation_rate,					
			        })

    return own_repk.as_dict()

@frappe.whitelist()
def re_stock_entry(own_re_packing):
    from erpnext.stock.doctype.item.item import get_item_defaults
    udoc = frappe.get_doc('Own Re Packing', own_re_packing)
    sett = frappe.get_doc('Own Packing Settings')    
    company=frappe.db.get_value('Chicken Own Packing',udoc.own_packing,'company')
    stock_entry = frappe.new_doc("Stock Entry")    
    stock_entry.company = company     
    ownpacktime=format_time(str(udoc.creation))
    stock_entry.posting_date = udoc.own_paking_date
    stock_entry.posting_time = ownpacktime
    stock_entry.set_posting_time='1'
    stock_entry.purpose = "Manufacture"
    stock_entry.stock_entry_type = "Manufacture"
    stock_entry.manufacturing_type = "Chicken Slaughtering Repack"
    stock_entry.own_repack=own_re_packing
    stock_entry.chicken_own_packing=udoc.own_packing
    precision = cint(frappe.db.get_default("float_precision")) or 3

    if udoc.re_packing_items:
        pcitems=[]
        for fitem in udoc.re_packing_items:
            if not fitem.new_item or fitem.new_qty == 0:
                continue

            if fitem.new_qty > int(fitem.old_item_avail_qty):
                frappe.throw(" Repack Item Qty must be less than or equal to Available Item")

            old_item_details = get_item_defaults(fitem.item_code, company)
            stock_uom = old_item_details.stock_uom
            conversion_factor = get_conversion_factor(fitem.item_code, fitem.old_uom).get("conversion_factor")
            cost_center=sett.cost_center or old_item_details.get("buying_cost_center")
            expense_account=old_item_details.get("expense_account")                
            item_name=old_item_details.get("item_name")
            qty=fitem.new_qty
            #rate = fitem.old_item_rate
            rate = get_incoming_rate({
						"item_code": fitem.item_code,
						"warehouse": udoc.source_warehouse,
						"posting_date": stock_entry.posting_date,
						"posting_time": stock_entry.posting_time,
						"qty": -1 * qty,
                        'company':company
					})
            amount=int(qty)*float(rate) 
            stock_entry.append('items', {
                    's_warehouse': udoc.source_warehouse,
					'item_code': fitem.item_code,
					'qty': qty,
                    'actual_qty':qty,
					'uom': fitem.old_uom,
                    'cost_center':cost_center,					
					'ste_detail': item_name,
					'stock_uom': stock_uom,
                    'expense_account':expense_account,
                    'valuation_rate': rate,
                    "basic_rate":rate, 	
                    "basic_amount":amount,  
                    "amount":amount,  
                    "transfer_qty":qty,
					'conversion_factor': flt(conversion_factor),
			        })

            itemscost=0
            
            item_account_details = get_item_defaults(fitem.new_item, company)
            pcmaterials=frappe.get_doc('Packing Materials',fitem.new_item)           
            
            for pcitem in pcmaterials.packing_item:
                pack_item_details = get_item_defaults(pcitem.item, company)
                stock_uom = pack_item_details.stock_uom
                conversion_factor = get_conversion_factor(pcitem.item, pcitem.uom).get("conversion_factor")
                cost_center=sett.cost_center or pack_item_details.get("buying_cost_center")
                expense_account=pack_item_details.get("expense_account")                
                item_name=pack_item_details.get("item_name")
                packed_qty=float(pcitem.qty)*float(fitem.new_qty)
                pck_rate = get_incoming_rate({
						"item_code": pcitem.item,
						"warehouse": udoc.packing_item_warehouse,
						"posting_date": stock_entry.posting_date,
						"posting_time": stock_entry.posting_time,
						"qty": -1 * packed_qty,
                        'company':company
					})
                                
                transfer_qty=flt(flt(packed_qty) * flt(conversion_factor),2)
                amount=flt(flt(transfer_qty) * flt(pck_rate), precision)
                itemscost+=transfer_qty * pck_rate
                stock_entry.append('items', {
                    's_warehouse': udoc.packing_item_warehouse,
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
                


            #base_rate = frappe.db.get_value('Item Price', {'price_list': 'Standard Selling','item_code':fitem.item}, 'price_list_rate') 
            stock_uom = item_account_details.stock_uom
            conversion_factor = get_conversion_factor(fitem.new_item, fitem.old_uom).get("conversion_factor")
            cost_center=sett.cost_center or item_account_details.get("buying_cost_center")
            expense_account=item_account_details.get("expense_account")                
            item_name=item_account_details.get("item_name")
            #weight_per_unit=item_account_details.get("weight_per_unit")
            packing_rate_of_item=itemscost/float(fitem.new_qty)
            base_rate=packing_rate_of_item+float(rate)
            amount=flt(fitem.new_qty) * base_rate
            pcitems.append({            
                    't_warehouse': udoc.traget_warehouse,
					'item_code': fitem.new_item,
					'qty': fitem.new_qty,
                    'actual_qty':fitem.new_qty,
					'uom': fitem.old_uom,
                    'cost_center':cost_center,					
					'ste_detail': item_name,
					'stock_uom': stock_uom,
                    'expense_account':expense_account,
                    'valuation_rate': base_rate,
                    "basic_rate":base_rate, 	
                    "basic_amount":amount,  
                    "amount":amount,  
                    "transfer_qty":fitem.new_qty,
					'conversion_factor': flt(conversion_factor),
                    'is_finished_item':1,
                    'set_basic_rate_manually':1                  
			})

        for pc in pcitems:
            stock_entry.append('items',pc)
        
    return stock_entry.as_dict()    

def get_old_valuerate(item,stock=None):
    vrate=0
    if stock:    
        vrate=frappe.db.get_value('Stock Entry Detail', {'item_code': item,'parent':stock}, 'valuation_rate')
    return vrate

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
    if doc.own_repack:
        
        pklist=frappe.db.get_all('Own Repacking Item',filters={'parent': doc.own_repack},fields=['new_qty', 'new_item','item_code'],debug=0)
        idxmax=frappe.db.sql("""select max(idx) as idx from `tabOwn Packing List`  where parent='{0}'   """.format(doc.chicken_own_packing),as_dict=1)[0]
        idx=idxmax.idx or 0
        for pklst in pklist:
            if pklst.new_qty and pklst.new_item:
                plist=frappe.db.get_value('Own Packing List', {'item_code': pklst.item_code,'parent':doc.chicken_own_packing},['parent','parenttype','name', 'qty','uom','grade'], as_dict=1,debug=0)
                if idx:
                    idx=idx+1
                item_name=frappe.db.get_value('Item',pklst.new_item,'item_name')
                newqty=int(plist.qty)-int(pklst.new_qty)
                frappe.db.set_value('Own Packing List', plist.name, 'qty', newqty)  
                udoc = frappe.get_doc('Chicken Own Packing', doc.chicken_own_packing)                                
                udoc.append('finished_items', {
                    'qty': pklst.new_qty,
                    'idx':idx,
					'item_code': pklst.new_item,
					'item': pklst.new_item,
                    'item_name':item_name,
                    'is_billing_updated':'0',
                    'parentfield':'finished_items',
					'uom': plist.uom,
                    'grade':plist.grade,					
					're_packing': doc.own_repack,					
			        })
                udoc.save()
                           
        

@frappe.whitelist()
def cancel_item(doc,event):
    if doc.chicken_own_packing:
        udoc = frappe.get_doc('Chicken Own Packing', doc.chicken_own_packing)
        if doc.manufacturing_type == "Chicken Slaughtering":
            udoc.item_processed = 0
            udoc.save()

    if doc.own_repack:
        pklist=frappe.db.get_all('Own Repacking Item',filters={'parent': doc.own_repack},fields=['new_qty', 'new_item','item_code'])
        for pklst in pklist:
            if pklst.new_qty and pklst.new_item:
                plist=frappe.db.get_value('Own Packing List', {'item_code': pklst.item_code,'parent':doc.chicken_own_packing},['name', 'qty','uom','grade'], as_dict=1)
                newqty=int(plist.qty)+int(pklst.new_qty)
                frappe.db.set_value('Own Packing List', plist.name, 'qty', newqty)
                frappe.db.delete("Own Packing List", {'re_packing':doc.own_repack,'item_code':pklst.new_item})
            
        
        

def update_selling_cost(doc,event):
    itemgp=['CHICKEN PRODUCTS - ACACIA','CHICKEN PRODUCTS - AL FAKHER','CHICKEN PRODUCTS - AUH']
    for i in doc.items:
        if i.item_code:
            group,weight=frappe.db.get_value('Item', i.item_code, ['item_group','weight_per_unit'])
            if group in itemgp:
                qty=i.stock_qty or i.qty
                rate=i.stock_uom_rate or i.rate
                #if i.uom=='Kg':
                #   qty=flt(i.qty/weight,4)
                #  rate=flt(i.rate*weight,4)
                #if i.uom=='ctn':
                #   qty=flt(i.qty/10,4)
                #  rate=flt(i.rate/10,4)
                    
                update_project(doc,i.item_code,qty,rate,i.production_date)
            


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
        own_pack=frappe.db.sql("""select l.item,o.project,l.name,l.updated_qty,l.qty from 
        `tabOwn Packing List` l left join `tabChicken Own Packing` o  on l.parent=o.name left join `tabProject` p on p.name=o.project where l.is_billing_updated<>'1' 
        and o.date <= '{0}' and o.item_processed=1 and p.status='Open' and l.item='{1}' order by o.`date` limit 0,1 """.format(doc.posting_date,item_code), as_dict=1)
        
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
    


