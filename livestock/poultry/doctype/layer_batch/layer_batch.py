# Copyright (c) 2023, alantechnologies and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.utils import nowdate, cint, get_datetime, formatdate, getdate, flt
from frappe.model.document import Document
from erpnext.stock.utils import (get_incoming_rate)
from erpnext.stock.get_item_details import (get_conversion_factor)
from erpnext.stock.doctype.item.item import get_item_defaults

class LayerBatch(Document):
	def before_insert(self):		
		shed=frappe.get_doc("Rearing Shed", self.rear_shed)
		project = frappe.new_doc("Project")
		project.project_name=self.batch_name
		project.project_type="LAYER"
		project.expected_start_date=self.start_date
		project.expected_end_date=self.end_date
		project.company=shed.company
		project.cost_center=shed.cost_center
		project.insert(ignore_permissions=True)
		self.project=project.name

	def after_insert(self):
		#pjt=frappe.get_doc("Project", self.project)
		#pjt.broiler_batch=self.name
		#pjt.save()
		pass
	def on_update(self):
		pjt=frappe.get_doc("Project", self.name)
		
		if pjt.status!=self.status:
			pjt.status=	self.status
			if self.status=='Completed':
				pjt.expected_end_date=nowdate()
			pjt.save()

@frappe.whitelist()
def stock_entry(batch,transfer_qty,rooster_qty,transfer_date,transfer_warehouse=''):
	lbatch=frappe.get_doc('Layer Batch',batch)
	

	if lbatch.rearing_shed:
		sett=frappe.get_doc('Rearing Shed',lbatch.rearing_shed)
	toto_mort=0
	if lbatch.rearing_daily_mortality:
		for mor in lbatch.rearing_daily_mortality:
			toto_mort+=mor.total

	live_chk=lbatch.doc_placed-toto_mort
	lbatch.flock_transferred_to_layer=transfer_qty
	time=''
	date=''
	if time:
		time=get_datetime(time)
	if transfer_date:
		date=getdate(transfer_date)

	posting_date=date or nowdate() 
	time=time or get_datetime()
	posting_time=time.strftime("%H:%M:%S")
	total_add_cost=0

	stock_entry = frappe.new_doc("Stock Entry")    
	stock_entry.company = lbatch.company
	stock_entry.purpose = "Manufacture"
	stock_entry.stock_entry_type = "Manufacture"
	stock_entry.manufacturing_type = "Egg"
	stock_entry.project = lbatch.project
	stock_entry.posting_date=posting_date
	stock_entry.set_posting_time='1'

	if sett.base_row_material:
		itmqty=lbatch.doc_placed+lbatch.mortality
		item_account_details = get_item_defaults(sett.base_row_material, sett.company)
		stock_uom = item_account_details.stock_uom
		conversion_factor = get_conversion_factor(sett.base_row_material, stock_uom).get("conversion_factor")
		cost_center=sett.cost_center or lbatch.cost_center or item_account_details.get("buying_cost_center")
		expense_account=item_account_details.get("expense_account")
		base_row_rate = get_incoming_rate({
						"item_code": sett.base_row_material,
						"warehouse": sett.row_material_target_warehouse,
						"posting_date": posting_date,
						"posting_time": posting_time,
						"qty": -1 * itmqty,
                        'company':sett.company
					})
		precision = cint(frappe.db.get_default("float_precision")) or 3    
		amount=flt(itmqty * flt(base_row_rate), precision)
		stock_entry.append('items', {
                        's_warehouse': sett.row_material_target_warehouse,
                        'item_code': sett.base_row_material,
                        'qty': itmqty,
                        'actual_qty':itmqty,
                        'uom': stock_uom,
                        'cost_center':cost_center,					
                        'ste_detail': item_account_details.name,
                        'stock_uom': stock_uom,
                        'expense_account':expense_account,
                        'valuation_rate': base_row_rate,
                        "basic_rate":base_row_rate, 	
                        "basic_amount":amount,  
                        "amount":amount,  
                        "transfer_qty":itmqty,
                        'conversion_factor': flt(conversion_factor),
                                  
        })
	else:
		frappe.throw(_("Please set base Rowmaterial in Layer Shed settings for {0} ").format(sett.company))

	feeds=frappe.db.get_list('Layer Feed',filters={'parent':batch,'parentfield':'rearing_feed'},
    fields=['item_code,sum(qty) as qty'],group_by='item_code')
	if feeds:
		for itm in feeds:
			itmqty=itm.qty
			item_account_details = get_item_defaults(itm.item_code, sett.company)
			stock_uom = item_account_details.stock_uom
			conversion_factor = get_conversion_factor(itm.item_code, stock_uom).get("conversion_factor")
			cost_center=sett.cost_center or lbatch.cost_center or item_account_details.get("buying_cost_center")
			expense_account=item_account_details.get("expense_account")
			rate = get_incoming_rate({
							"item_code": itm.item_code,
							"warehouse": sett.feed_warehouse,
							"posting_date": posting_date,
							"posting_time": posting_time,
							"qty": -1 * itmqty,
							'company':sett.company
						})
			precision = cint(frappe.db.get_default("float_precision")) or 3    
			amount=flt(itmqty * flt(rate), precision)
			stock_entry.append('items', {
							's_warehouse': sett.feed_warehouse,
							'item_code': itm.item_code,
							'qty': itmqty,
							'actual_qty':itmqty,
							'uom': stock_uom,
							'cost_center':cost_center,					
							'ste_detail': item_account_details.name,
							'stock_uom': stock_uom,
							'expense_account':expense_account,
							'valuation_rate': rate,
							"basic_rate":rate, 	
							"basic_amount":amount,  
							"amount":amount,  
							"transfer_qty":itmqty,
							'conversion_factor': flt(conversion_factor),
									
			})
			total_add_cost=total_add_cost+amount
	
	medicines=frappe.db.get_list('Layer Medicine',filters={'parent':batch,'parentfield':'rearing_feed'},
    fields=['item_code,sum(qty) as qty'],group_by='item_code')
	if medicines:
		for itm in medicines:
			itmqty=itm.qty
			item_account_details = get_item_defaults(itm.item_code, sett.company)
			stock_uom = item_account_details.stock_uom
			conversion_factor = get_conversion_factor(itm.item_code, stock_uom).get("conversion_factor")
			cost_center=sett.cost_center or lbatch.cost_center or item_account_details.get("buying_cost_center")
			expense_account=item_account_details.get("expense_account")
			rate = get_incoming_rate({
							"item_code": itm.item_code,
							"warehouse": sett.row_material_target_warehouse,
							"posting_date": posting_date,
							"posting_time": posting_time,
							"qty": -1 * itmqty,
							'company':sett.company
						})
			precision = cint(frappe.db.get_default("float_precision")) or 3    
			amount=flt(itmqty * flt(rate), precision)
			stock_entry.append('items', {
							's_warehouse': sett.row_material_target_warehouse,
							'item_code': itm.item_code,
							'qty': itmqty,
							'actual_qty':itmqty,
							'uom': stock_uom,
							'cost_center':cost_center,					
							'ste_detail': item_account_details.name,
							'stock_uom': stock_uom,
							'expense_account':expense_account,
							'valuation_rate': rate,
							"basic_rate":rate, 	
							"basic_amount":amount,  
							"amount":amount,  
							"transfer_qty":itmqty,
							'conversion_factor': flt(conversion_factor),
									
			})
			total_add_cost=total_add_cost+amount

	vaccines=frappe.db.get_list('Layer Vaccine',filters={'parent':batch,'parentfield':'rearing_feed'},
    fields=['item_code,sum(qty) as qty'],group_by='item_code')
	if vaccines:
		for itm in vaccines:
			itmqty=itm.qty
			item_account_details = get_item_defaults(itm.item_code, sett.company)
			stock_uom = item_account_details.stock_uom
			conversion_factor = get_conversion_factor(itm.item_code, stock_uom).get("conversion_factor")
			cost_center=sett.cost_center or lbatch.cost_center or item_account_details.get("buying_cost_center")
			expense_account=item_account_details.get("expense_account")
			rate = get_incoming_rate({
							"item_code": itm.item_code,
							"warehouse": sett.row_material_target_warehouse,
							"posting_date": posting_date,
							"posting_time": posting_time,
							"qty": -1 * itmqty,
							'company':sett.company
						})
			precision = cint(frappe.db.get_default("float_precision")) or 3    
			amount=flt(itmqty * flt(rate), precision)
			stock_entry.append('items', {
							's_warehouse': sett.row_material_target_warehouse,
							'item_code': itm.item_code,
							'qty': itmqty,
							'actual_qty':itmqty,
							'uom': stock_uom,
							'cost_center':cost_center,					
							'ste_detail': item_account_details.name,
							'stock_uom': stock_uom,
							'expense_account':expense_account,
							'valuation_rate': rate,
							"basic_rate":rate, 	
							"basic_amount":amount,  
							"amount":amount,  
							"transfer_qty":itmqty,
							'conversion_factor': flt(conversion_factor),
									
			})
			total_add_cost=total_add_cost+amount

	items=frappe.db.get_list('Layer Other Items',filters={'parent':batch,'parentfield':'rearing_feed'},
    fields=['item_code,sum(qty) as qty'],group_by='item_code')
	if items:
		for itm in items:
			itmqty=itm.qty
			item_account_details = get_item_defaults(itm.item_code, sett.company)
			stock_uom = item_account_details.stock_uom
			conversion_factor = get_conversion_factor(itm.item_code, stock_uom).get("conversion_factor")
			cost_center=sett.cost_center or lbatch.cost_center or item_account_details.get("buying_cost_center")
			expense_account=item_account_details.get("expense_account")
			rate = get_incoming_rate({
							"item_code": itm.item_code,
							"warehouse": sett.row_material_target_warehouse,
							"posting_date": posting_date,
							"posting_time": posting_time,
							"qty": -1 * itmqty,
							'company':sett.company
						})
			precision = cint(frappe.db.get_default("float_precision")) or 3    
			amount=flt(itmqty * flt(rate), precision)
			stock_entry.append('items', {
							's_warehouse': sett.row_material_target_warehouse,
							'item_code': itm.item_code,
							'qty': itmqty,
							'actual_qty':itmqty,
							'uom': stock_uom,
							'cost_center':cost_center,					
							'ste_detail': item_account_details.name,
							'stock_uom': stock_uom,
							'expense_account':expense_account,
							'valuation_rate': rate,
							"basic_rate":rate, 	
							"basic_amount":amount,  
							"amount":amount,  
							"transfer_qty":itmqty,
							'conversion_factor': flt(conversion_factor),
									
			})
			total_add_cost=total_add_cost+amount

	if int(transfer_qty) > 0 :
		#live_chk
		if sett.finished_product:
			item_account_details = get_item_defaults(sett.finished_product, sett.company)
			stock_uom = item_account_details.stock_uom
			conversion_factor = get_conversion_factor(sett.finished_product, stock_uom).get("conversion_factor")
			cost_center=sett.cost_center or lbatch.cost_center or item_account_details.get("buying_cost_center")
			expense_account=item_account_details.get("expense_account")                                
			precision = cint(frappe.db.get_default("float_precision")) or 3
			cost=((int(transfer_qty)*base_row_rate) + total_add_cost) / int(transfer_qty)
			amount=flt(int(transfer_qty) * flt(cost), precision)
			stock_entry.append('items', {
							't_warehouse': transfer_warehouse or sett.product_target_warehouse,
							'item_code': sett.finished_product,
							'qty': transfer_qty,
							'actual_qty':transfer_qty,
							'uom': stock_uom,
							'cost_center':cost_center,					
							'ste_detail': item_account_details.name,
							'stock_uom': stock_uom,
							'expense_account':expense_account,
							'valuation_rate': cost,
							"basic_rate":cost, 	
							"basic_amount":amount,  
							"amount":amount,  
							"transfer_qty":transfer_qty,
							'conversion_factor': flt(conversion_factor),
							'is_finished_item':1,
			               
        	})
		else:
			frappe.throw(_("Please set Finished Item in Layer Shed settings for {0} ").format(sett.company))

	if int(toto_mort) > 0:
		if sett.cull:
			item_account_details = get_item_defaults(sett.cull, sett.company)
			stock_uom = item_account_details.stock_uom
			conversion_factor = get_conversion_factor(sett.cull, stock_uom).get("conversion_factor")
			cost_center=sett.cost_center or lbatch.cost_center or item_account_details.get("buying_cost_center")
			expense_account=item_account_details.get("expense_account")                                
			precision = cint(frappe.db.get_default("float_precision")) or 3
			base_row_rate = get_incoming_rate({
							"item_code": sett.base_row_material,
							"warehouse": sett.cull_target_warehouse,
							"posting_date": posting_date,
							"posting_time": posting_time,
							"qty": -1 * toto_mort,
							'company':sett.company
						})    
			amount=flt(flt(toto_mort) * base_row_rate, precision)
			stock_entry.append('items', {
							't_warehouse': sett.cull_target_warehouse,
							'item_code': sett.cull,
							'qty': toto_mort,
							'actual_qty':toto_mort,
							'uom': stock_uom,
							'cost_center':cost_center,					
							'ste_detail': item_account_details.name,
							'stock_uom': stock_uom,
							'expense_account':expense_account,
							'valuation_rate': base_row_rate,
							"basic_rate":base_row_rate, 	
							"basic_amount":amount,  
							"amount":amount,  
							"transfer_qty":toto_mort,
							'conversion_factor': flt(conversion_factor),
							'is_scrap_item':1,          
			})

		else:
			frappe.throw(_("Please set Cull Item in Layer Shed settings for {0} ").format(sett.company))

	#stock_entry.save()
	stock_entry.insert()
	stock_entry.docstatus=1
	stock_entry.save()
	lbatch.rooster_qty=rooster_qty
	lbatch.item_processed=1
	lbatch.save()
	items=frappe.db.get_all('Layer Other Items',filters={'parentfield':'rearing_items','parent':batch},fields=['name'])
	if items:
		for itm in items:
			litem=frappe.get_doc('Layer Other Items',itm.name)
			litem.docstatus=1
			litem.stock_entry=stock_entry.name
			litem.save()

	vaccines=frappe.db.get_all('Layer Vaccine',filters={'parentfield':'rearing_vaccine','parent':batch},fields=['name'])
	if vaccines:
		for itm in vaccines:
			litem=frappe.get_doc('Layer Vaccine',itm.name)
			litem.docstatus=1
			litem.stock_entry=stock_entry.name
			litem.save()

	medicines=frappe.db.get_all('Layer Medicine',filters={'parentfield':'rearing_medicine','parent':batch},fields=['name'])
	if medicines:
		for itm in medicines:
			litem=frappe.get_doc('Layer Medicine',itm.name)
			litem.docstatus=1
			litem.stock_entry=stock_entry.name
			litem.save()

	feeds=frappe.db.get_all('Layer Feed',filters={'parentfield':'rearing_feed','parent':batch},fields=['name'])
	if feeds:
		for itm in feeds:
			litem=frappe.get_doc('Layer Feed',itm.name)
			litem.docstatus=1
			litem.stock_entry=stock_entry.name
			litem.save()
			 

	mortalitys=frappe.db.get_all('Layer Mortality',filters={'parentfield':'rearing_daily_mortality','parent':batch},fields=['name'])
	if mortalitys:
		for itm in mortalitys:
			litem=frappe.get_doc('Layer Mortality',itm.name)
			litem.docstatus=1
			litem.stock_entry=stock_entry.name
			litem.save()
	frappe.msgprint('Stock Entry '+str(stock_entry.name)+' created')
	return stock_entry.as_dict()

def create_stock_entry_mortality(item,parent_field=''):
	lbatch=frappe.get_doc('Layer Batch',item.parent)
	sett2=frappe.get_doc('Rearing Shed',lbatch.rearing_shed)
	sett=frappe.get_doc('Laying Shed',lbatch.layer_shed)
	time=''
	date=''
	if item.date:
		date=getdate(item.date)

	if item.creation:
		time=get_datetime(item.creation)
		
	item_code=sett2.finished_product
	qty=item.total
	uom='Nos'

	posting_date=date or nowdate() 
	time=time or get_datetime()
	posting_time=time.strftime("%H:%M:%S")

	stock_entry = frappe.new_doc("Stock Entry")    
	stock_entry.company = lbatch.company	
	stock_entry.stock_entry_type = "Material Issue"	
	stock_entry.project = lbatch.project
	stock_entry.posting_date=posting_date
	stock_entry.set_posting_time='1'

	item_account_details = get_item_defaults(item_code, sett.company)
	expense_account=sett.mortality_expense_account or item_account_details.get("expense_account")
	stock_uom = item_account_details.stock_uom
	conversion_factor = get_conversion_factor(item_code, uom).get("conversion_factor")
	cost_center=sett.cost_center or lbatch.cost_center or item_account_details.get("buying_cost_center")
	row_material_target_warehouse=sett.row_material_target_warehouse
	rate = get_incoming_rate({
                                "item_code": item_code,
                                "warehouse": row_material_target_warehouse,
                                "posting_date": posting_date,
                                "posting_time": posting_time,
                                "qty": -1 * qty,
                                'company':sett.company
                            }) or 0


	precision = cint(frappe.db.get_default("float_precision")) or 3    
	amount=flt(float(qty) * float(rate), precision)
	stock_entry.append('items', {
                                's_warehouse': row_material_target_warehouse,
                                'item_code': item_code,
                                'qty': qty,
                                'actual_qty':qty,
                                'uom': uom,
                                'cost_center':cost_center,					
                                'ste_detail': item_account_details.name,
                                'stock_uom': stock_uom,
                                'expense_account':expense_account,
                                'valuation_rate': rate,
                                "basic_rate":rate, 	
                                "basic_amount":amount,  
                                "amount":amount,  
                                "transfer_qty":qty,
                                'conversion_factor': flt(conversion_factor),
                                        
                })
	stock_entry.insert()
	stock_entry.docstatus=1
	stock_entry.save()

	
	litem=frappe.get_doc('Layer Mortality',item.name)
	litem.docstatus=1
	litem.stock_entry=stock_entry.name
	litem.save()
	frappe.msgprint('Stock Entry '+str(stock_entry.name)+' created')
	return stock_entry.as_dict()

def create_stock_entry(item,parent_field=''):
	lbatch=frappe.get_doc('Layer Batch',item.parent)
	if lbatch.rearing_shed:
		sett=frappe.get_doc('Laying Shed',lbatch.layer_shed)
		sett2=frappe.get_doc('Rearing Shed',lbatch.rearing_shed)
	time=''
	date=''
	if item.date:
		date=getdate(item.date)

	if item.creation:
		time=get_datetime(item.creation)
		

	posting_date=date or nowdate() 
	time=time or get_datetime()
	posting_time=time.strftime("%H:%M:%S")

	stock_entry = frappe.new_doc("Stock Entry")    
	stock_entry.company = lbatch.company	
	stock_entry.stock_entry_type = "Material Issue"	
	stock_entry.project = lbatch.project
	stock_entry.posting_date=posting_date
	stock_entry.set_posting_time='1'
	item_account_details = get_item_defaults(item.item_code, sett.company)
	stock_uom = item_account_details.stock_uom
	conversion_factor = get_conversion_factor(item.item_code, item.uom).get("conversion_factor")
	cost_center=sett.cost_center or lbatch.cost_center or item_account_details.get("buying_cost_center")
	
	item_code=item.item_code
	row_material_target_warehouse=sett.row_material_target_warehouse
	if parent_field=='laying_items':
		expense_account=sett.other_items_expense_account or item_account_details.get("expense_account")
	elif parent_field=='laying_medicine':
		expense_account=sett.medicine_expense_account or item_account_details.get("expense_account")
	elif parent_field=='laying_vaccine':
		expense_account=sett.vaccine_expense_account or item_account_details.get("expense_account")
	elif parent_field=='laying_feed':
		expense_account=sett.feed_expense_account or item_account_details.get("expense_account")
		row_material_target_warehouse=sett.feed_warehouse
	elif parent_field=='laying_mortality':
		expense_account=sett.mortality_expense_account or item_account_details.get("expense_account")
		item_code=sett2.finished_product
	else:
		expense_account=item_account_details.get("expense_account")
	
	rate = get_incoming_rate({
                                "item_code": item_code,
                                "warehouse": row_material_target_warehouse,
                                "posting_date": posting_date,
                                "posting_time": posting_time,
                                "qty": -1 * item.qty,
                                'company':sett.company
                            }) or 0


	precision = cint(frappe.db.get_default("float_precision")) or 3    
	amount=flt(float(item.qty) * float(rate), precision)
	stock_entry.append('items', {
                                's_warehouse': row_material_target_warehouse,
                                'item_code': item_code,
                                'qty': item.qty,
                                'actual_qty':item.qty,
                                'uom': item.uom,
                                'cost_center':cost_center,					
                                'ste_detail': item_account_details.name,
                                'stock_uom': stock_uom,
                                'expense_account':expense_account,
                                'valuation_rate': rate,
                                "basic_rate":rate, 	
                                "basic_amount":amount,  
                                "amount":amount,  
                                "transfer_qty":item.qty,
                                'conversion_factor': flt(conversion_factor),
                                        
                })
	stock_entry.insert()
	stock_entry.docstatus=1
	stock_entry.save()

	tbl=''
	if parent_field=='laying_items':
		tbl='Layer Other Items'
	elif parent_field=='laying_medicine':
		tbl='Layer Medicine'
	elif parent_field=='laying_vaccine':
		tbl='Layer Vaccine'
	elif parent_field=='laying_feed':
		tbl='Layer Feed'
	elif parent_field=='laying_mortality':
		tbl='Layer Mortality'
	if tbl:
		litem=frappe.get_doc(tbl,item.name)
		litem.docstatus=1
		litem.stock_entry=stock_entry.name
		litem.save()
	frappe.msgprint('Stock Entry '+str(stock_entry.name)+' created')
	return stock_entry.as_dict()

def create_production_stock_entry(fitem):
	time=''
	date=''
	if fitem.date:
		date=getdate(fitem.date)

	if fitem.creation:
		time=get_datetime(fitem.creation)
		
		
	posting_date=date or nowdate() 
	time=time or get_datetime()
	posting_time=time.strftime("%H:%M:%S")

	lbatch=frappe.get_doc('Layer Batch',fitem.parent)
	if lbatch.rearing_shed:
		sett=frappe.get_doc('Laying Shed',lbatch.layer_shed)
	pcmaterials=frappe.get_doc('Egg Packing Materials',fitem.item_code)
	stock_entry = frappe.new_doc("Stock Entry")    
	stock_entry.company = lbatch.company     

	stock_entry.posting_date = posting_date
	stock_entry.posting_time = posting_time
	stock_entry.set_posting_time='1'
	stock_entry.purpose = "Manufacture"
	stock_entry.stock_entry_type = "Manufacture"
	stock_entry.manufacturing_type = "Egg"

	#stock_entry.set_stock_entry_type()
	precision = cint(frappe.db.get_default("float_precision")) or 3
	itemscost=0
	item_account_details = get_item_defaults(fitem.item_code, lbatch.company)
	for pcitem in pcmaterials.packing_item:
		pack_item_details = get_item_defaults(pcitem.item, lbatch.company)
		stock_uom = pack_item_details.stock_uom
		conversion_factor = get_conversion_factor(pcitem.item, pcitem.uom).get("conversion_factor")
		cost_center=sett.cost_center or pack_item_details.get("buying_cost_center")
		expense_account=pack_item_details.get("expense_account")                
		item_name=pack_item_details.get("item_name")
		packed_qty=float(pcitem.qty)*float(fitem.qty)
		pck_rate = get_incoming_rate({
						"item_code": pcitem.item,
						"warehouse": sett.row_material_target_warehouse,
						"posting_date": posting_date,
						"posting_time": posting_time,
						"qty": -1 * packed_qty,
                        'company':lbatch.company
					}) or 0
                                
		transfer_qty=flt(float(packed_qty) * float(conversion_factor),2)
		amount=flt(float(transfer_qty) * float(pck_rate), precision)
		itemscost+=transfer_qty * pck_rate
		stock_entry.append('items', {
                    's_warehouse': sett.row_material_target_warehouse,
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
	stock_uom = item_account_details.stock_uom
	
	conversion_factor = get_conversion_factor(fitem.item_code, fitem.uom).get("conversion_factor")
	cost_center=sett.cost_center or item_account_details.get("buying_cost_center")
	expense_account=item_account_details.get("expense_account")                
	item_name=item_account_details.get("item_name")
	base_rate=0

	batch_no=''
	if item_account_details.has_batch_no:
		manufacture_date=posting_date.strftime("%d-%m-%Y")
		batch = frappe.new_doc("Batch")
		batch.batch_id=str(fitem.item_code)+' '+str(manufacture_date)
		batch.item=fitem.item_code
		batch.item_name=item_name
		batch.batch_qty=fitem.qty
		batch.manufacturing_date=posting_date
		batch.stock_uom=stock_uom
		batch.insert()
		batch_no=batch.name

	if itemscost:
		base_rate=itemscost/float(fitem.qty)		
	amount=float(fitem.qty) * float(base_rate)
	stock_entry.append('items', {            
                    't_warehouse': sett.product_target_warehouse,
					'item_code': fitem.item_code,
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
                    'set_basic_rate_manually':1,
					'batch_no':batch_no,                  
			})
	stock_entry.insert()
	stock_entry.docstatus=1
	stock_entry.save()

	litem=frappe.get_doc('Egg Production',fitem.name)
	litem.docstatus=1
	litem.stock_entry=stock_entry.name
	litem.save()
	frappe.msgprint('Stock Entry '+str(stock_entry.name)+' created')
	return stock_entry.as_dict()

@frappe.whitelist()
def added_feed_rearing(batch,parentfield,date,item_code,qty,uom):
	
	item_name=frappe.db.get_value('Item',item_code,'item_name')
	itemdet=get_item_rate(batch,item_code,qty,uom,date='',time='')
	rate=itemdet.rate
	conversion_factor=itemdet.conversion_factor
	
	midx=frappe.db.sql("""select max(idx) from `tabLayer Feed` where parentfield='{0}' and parent='{1}' """.format(parentfield,batch))
	curidx=1
	if midx and midx[0][0] is not None:
		curidx = cint(midx[0][0])+1
	childtbl = frappe.new_doc("Layer Feed")
	childtbl.update({'idx':curidx,'date':date,'rate':rate,'conversion_factor':conversion_factor,'item_code':item_code,'item_name':item_name,'qty':qty,'uom':uom,'parent': batch,'parenttype': 'Layer Batch','parentfield': parentfield})
	childtbl.save()
	if parentfield=='laying_feed':
		create_stock_entry(childtbl,parentfield)

	return childtbl.as_dict()

@frappe.whitelist()
def update_feed_rearing(idx,parent,parentfield,name,date,item_code,qty,uom):
	if 'new-' in name:
		name=frappe.db.get_value('Layer Feed', {'parent': parent,'idx':idx,'parentfield':parentfield}, ['name'])
	
	itemdet=get_item_rate(parent,item_code,qty,uom,date='',time='')
	item_name=frappe.db.get_value('Item',item_code,'item_name')
	rate=itemdet.rate
	conversion_factor=itemdet.conversion_factor

	doc = frappe.get_doc('Layer Feed', name)
	doc.date = date
	doc.item_code = item_code
	doc.item_name=item_name
	doc.qty = qty
	doc.uom = uom
	doc.rate = rate
	doc.conversion_factor = conversion_factor
	#doc.docstatus=1
	doc.save()
	return doc.as_dict()

@frappe.whitelist()
def delete_feed_rearing(name):
	frappe.db.delete('Layer Feed', {"name": name })


@frappe.whitelist()
def added_medicine_rearing(batch,parentfield,date,item_code,qty,uom,remark=''):
	
	item_name=frappe.db.get_value('Item',item_code,'item_name')
	itemdet=get_item_rate(batch,item_code,qty,uom,date='',time='')
	rate=itemdet.rate
	conversion_factor=itemdet.conversion_factor
	
	midx=frappe.db.sql("""select max(idx) from `tabLayer Medicine` where parentfield='{0}' and parent='{1}' """.format(parentfield,batch))
	curidx=1
	if midx and midx[0][0] is not None:
		curidx = cint(midx[0][0])+1
	childtbl = frappe.new_doc("Layer Medicine")
	childtbl.update({'idx':curidx,'date':date,'rate':rate,'conversion_factor':conversion_factor,'item_code':item_code,'item_name':item_name,'qty':qty,'uom':uom,'remark':remark,'parent': batch,'parenttype': 'Layer Batch','parentfield': parentfield})
	childtbl.save()
	if parentfield=='laying_medicine':
		create_stock_entry(childtbl,parentfield)
	return childtbl.as_dict()
	
@frappe.whitelist()
def update_medicine_rearing(idx,parent,parentfield,name,date,item_code,qty,uom,remark=''):
	if 'new-' in name:
		name=frappe.db.get_value('Layer Medicine', {'parent': parent,'idx':idx,'parentfield':parentfield}, ['name'])

	item_name=frappe.db.get_value('Item',item_code,'item_name')
	itemdet=get_item_rate(parent,item_code,qty,uom,date='',time='')
	rate=itemdet.rate
	conversion_factor=itemdet.conversion_factor
	doc = frappe.get_doc('Layer Medicine', name)
	doc.date = date
	doc.item_code = item_code
	doc.item_name=item_name
	doc.qty = qty
	doc.uom = uom
	doc.remark=remark
	doc.rate=rate
	doc.conversion_factor=conversion_factor
	#doc.docstatus=1
	doc.save()
	return doc.as_dict()

@frappe.whitelist()
def delete_medicine_rearing(name):
	frappe.db.delete('Layer Medicine', {"name": name })

@frappe.whitelist()
def add_vaccine_rearing(batch,parentfield,date,item_code,qty,uom,remark=''):
	
	item_name=frappe.db.get_value('Item',item_code,'item_name')
	itemdet=get_item_rate(batch,item_code,qty,uom,date='',time='')
	rate=itemdet.rate
	conversion_factor=itemdet.conversion_factor
	midx=frappe.db.sql("""select max(idx) from `tabLayer Vaccine` where parentfield='{0}' and parent='{1}' """.format(parentfield,batch))
	curidx=1
	if midx and midx[0][0] is not None:
		curidx = cint(midx[0][0])+1
	childtbl = frappe.new_doc("Layer Vaccine")
	childtbl.update({'idx':curidx,'date':date,'rate':rate,'conversion_factor':conversion_factor,'item_code':item_code,'item_name':item_name,'qty':qty,'uom':uom,'remark':remark,'parent': batch,'parenttype': 'Layer Batch','parentfield': parentfield})
	childtbl.save()
	if parentfield=='laying_vaccine':
		create_stock_entry(childtbl,parentfield)
	return childtbl.as_dict()

@frappe.whitelist()
def update_vaccine_rearing(idx,parent,parentfield,name,date,item_code,qty,uom,remark=''):
	if 'new-' in name:
		name=frappe.db.get_value('Layer Vaccine', {'parent': parent,'idx':idx,'parentfield':parentfield}, ['name'])
	
	itemdet=get_item_rate(parent,item_code,qty,uom,date='',time='')
	item_name=frappe.db.get_value('Item',item_code,'item_name')
	rate=itemdet.rate
	conversion_factor=itemdet.conversion_factor
	doc = frappe.get_doc('Layer Vaccine', name)
	doc.date = date
	doc.item_code = item_code
	doc.item_name=item_name
	doc.qty = qty
	doc.uom = uom
	doc.remark=remark
	doc.rate=rate
	doc.conversion_factor=conversion_factor
	#doc.docstatus=1
	doc.save()
	return doc.as_dict()

@frappe.whitelist()
def delete_vaccine_rearing(name):
	frappe.db.delete('Layer Vaccine', {"name": name })


@frappe.whitelist()
def add_rearing_items(batch,parentfield,date,item_code,qty,uom):
	
	item_name=frappe.db.get_value('Item',item_code,'item_name')
	itemdet=get_item_rate(batch,item_code,qty,uom,date='',time='')
	rate=itemdet.rate
	conversion_factor=itemdet.conversion_factor
	
	midx=frappe.db.sql("""select max(idx) from `tabLayer Other Items` where parentfield='{0}' and parent='{1}' """.format(parentfield,batch))
	curidx=1
	if midx and midx[0][0] is not None:
		curidx = cint(midx[0][0])+1
	childtbl = frappe.new_doc("Layer Other Items")
	childtbl.update({'idx':curidx,'date':date,'item_code':item_code,'rate':rate,'conversion_factor':conversion_factor,'item_name':item_name,'qty':qty,'uom':uom,'parent': batch,'parenttype': 'Layer Batch','parentfield': parentfield})
	childtbl.save()
	if parentfield=='laying_items':
		create_stock_entry(childtbl,parentfield)
	return childtbl.as_dict()

@frappe.whitelist()
def update_items_rearing(idx,parent,parentfield,name,date,item_code,qty,uom):
	if 'new-' in name:
		name=frappe.db.get_value('Layer Other Items', {'parent': parent,'idx':idx,'parentfield':parentfield}, ['name'])
	
	itemdet=get_item_rate(parent,item_code,qty,uom,date='',time='')
	item_name=frappe.db.get_value('Item',item_code,'item_name')
	rate=itemdet.rate
	conversion_factor=itemdet.conversion_factor

	doc = frappe.get_doc('Layer Other Items', name)
	doc.date = date
	doc.item_code = item_code
	doc.qty = qty
	doc.uom = uom
	doc.rate = rate
	doc.item_name=item_name
	doc.conversion_factor = conversion_factor	
	#doc.docstatus=1
	doc.save()
	return doc.as_dict()

@frappe.whitelist()
def delete_items_rearing(name):
	frappe.db.delete('Layer Other Items', {"name": name })



@frappe.whitelist()
def add_rearing_mortality(batch,parentfield,date,age,evening=0,morning=0,remark=''):

	total=float(morning)+float(evening)
	midx=frappe.db.sql("""select max(idx) from `tabLayer Mortality` where parentfield='{0}' and parent='{1}' """.format(parentfield,batch))
	curidx=1
	if midx and midx[0][0] is not None:
		curidx = cint(midx[0][0])+1
	childtbl = frappe.new_doc("Layer Mortality")
	childtbl.update({'idx':curidx,'date':date,'age':age,'morning':morning,'evening':evening,'total':total,'remark':remark,'parent': batch,'parenttype': 'Layer Batch','parentfield': parentfield})
	childtbl.save()
	if parentfield=='laying_mortality':
		create_stock_entry_mortality(childtbl,parentfield)
	return childtbl.as_dict()

@frappe.whitelist()
def update_mortality_rearing(idx,parent,parentfield,name,date,age,evening=0,morning=0,remark=''):
	if 'new-' in name:
		name=frappe.db.get_value('Layer Mortality', {'parent': parent,'idx':idx,'parentfield':parentfield}, ['name'])
	
	doc = frappe.get_doc('Layer Mortality', name)
	doc.date = date
	doc.age = age
	doc.morning = morning
	doc.evening = evening
	doc.total = float(morning)+float(evening)
	doc.remark = remark	
	#doc.docstatus=1
	doc.save()
	return doc.as_dict()

@frappe.whitelist()
def delete_mortality_rearing(name):
	frappe.db.delete('Layer Mortality', {"name": name })

@frappe.whitelist()
def add_rearing_temperature(batch,parentfield,date,evening=0,morning=0):

	total=float(morning)+float(evening)
	midx=frappe.db.sql("""select max(idx) from `tabLayer Temperature` where parentfield='{0}' and parent='{1}' """.format(parentfield,batch))
	curidx=1
	if midx and midx[0][0] is not None:
		curidx = cint(midx[0][0])+1
	childtbl = frappe.new_doc("Layer Temperature")
	childtbl.update({'idx':curidx,'date':date,'morning':morning,'evening':evening,'parent': batch,'parenttype': 'Layer Batch','parentfield': parentfield})
	childtbl.save()
	return childtbl.as_dict()

@frappe.whitelist()
def update_temperature_rearing(idx,parent,parentfield,name,date,evening=0,morning=0):
	if 'new-' in name:
		name=frappe.db.get_value('Layer Temperature', {'parent': parent,'idx':idx,'parentfield':parentfield}, ['name'])
	
	doc = frappe.get_doc('Layer Temperature', name)
	doc.date = date
	doc.morning = morning
	doc.evening = evening
	#doc.docstatus=1
	doc.save()
	return doc.as_dict()

@frappe.whitelist()
def delete_temperature_rearing(name):
	frappe.db.delete('Layer Temperature', {"name": name })

@frappe.whitelist()
def add_rearing_weight(batch,parentfield,date,week=0,weight=0):

	midx=frappe.db.sql("""select max(idx) from `tabLayer Weight` where parentfield='{0}' and parent='{1}' """.format(parentfield,batch))
	curidx=1
	if midx and midx[0][0] is not None:
		curidx = cint(midx[0][0])+1
	childtbl = frappe.new_doc("Layer Weight")
	childtbl.update({'idx':curidx,'date':date,'week':week,'weight':weight,'parent': batch,'parenttype': 'Layer Batch','parentfield': parentfield})
	childtbl.save()
	return childtbl.as_dict()

@frappe.whitelist()
def update_weight_rearing(idx,parent,parentfield,name,date,week=0,weight=0):
	if 'new-' in name:
		name=frappe.db.get_value('Layer Weight', {'parent': parent,'idx':idx,'parentfield':parentfield}, ['name'])
	
	doc = frappe.get_doc('Layer Weight', name)
	doc.date = date
	doc.week = week
	doc.weight = weight
	#doc.docstatus=1
	doc.save()
	return doc.as_dict()

@frappe.whitelist()
def delete_weight_rearing(name):
	frappe.db.delete('Layer Weight', {"name": name })

@frappe.whitelist()
def add_egg_production(batch,parentfield,date,item_code,qty,uom):
	
	item_name=frappe.db.get_value('Item',item_code,'item_name')
	itemdet=get_item_rate(batch,item_code,qty,uom,date='',time='')
	rate=itemdet.rate
	conversion_factor=itemdet.conversion_factor
	
	midx=frappe.db.sql("""select max(idx) from `tabEgg Production` where parentfield='{0}' and parent='{1}' """.format(parentfield,batch))
	curidx=1
	if midx and midx[0][0] is not None:
		curidx = cint(midx[0][0])+1
	childtbl = frappe.new_doc("Egg Production")
	childtbl.update({'idx':curidx,'date':date,'rate':rate,'conversion_factor':conversion_factor,'item_code':item_code,'item_name':item_name,'qty':qty,'uom':uom,'parent': batch,'parenttype': 'Layer Batch','parentfield': parentfield})
	childtbl.save()

	create_production_stock_entry(childtbl)

	return childtbl.as_dict()

@frappe.whitelist()
def update_egg_production(idx,parent,parentfield,name,date,item_code,qty,uom):
	if 'new-' in name:
		name=frappe.db.get_value('Egg Production', {'parent': parent,'idx':idx,'parentfield':parentfield}, ['name'])
	
	itemdet=get_item_rate(parent,item_code,qty,uom,date='',time='')
	rate=itemdet.rate
	conversion_factor=itemdet.conversion_factor

	doc = frappe.get_doc('Egg Production', name)
	doc.date = date
	doc.item_code = item_code
	doc.qty = qty
	doc.uom = uom
	doc.rate = rate
	doc.conversion_factor = conversion_factor
	#doc.docstatus=1
	doc.save()
	return doc.as_dict()

@frappe.whitelist()
def delete_egg_production(name):
	frappe.db.delete('Egg Production', {"name": name })

def get_item_rate(batch,item,qty,uom,date='',time=''):
	res={}
	shed=frappe.get_value('Layer Batch',{'batch_name':batch},'layer_shed')
	if time:
		time=get_datetime(time)
	if date:
		date=getdate(date)

	sett = frappe.get_doc('Laying Shed',shed)
	posting_date=date or nowdate() 
	time=time or get_datetime()
	posting_time=time.strftime("%H:%M:%S")
	base_row_rate = get_incoming_rate({
										"item_code": item,
										"warehouse": sett.row_material_target_warehouse,
										"posting_date": posting_date,
										"posting_time": posting_time,
										"qty": -1 * qty,
										'company':sett.company
										})
	conversion_factor = get_conversion_factor(item, uom).get("conversion_factor")
	rate=base_row_rate * float(conversion_factor)
	res.update({'rate':base_row_rate,'conversion_factor':conversion_factor})
	return frappe._dict(res)