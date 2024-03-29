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
		if not self.project:		
			shed=frappe.get_doc("Rearing Shed", self.rearing_shed)
			project = frappe.new_doc("Project")
			project.project_name=self.batch_name
			project.project_type="LAYER"
			project.expected_start_date=self.start_date
			#project.expected_end_date=self.end_date
			project.company=shed.company
			project.cost_center=shed.cost_center
			project.insert(ignore_permissions=True)
			self.project=project.name
		else:
			self.batch_name=self.project
			
	def after_insert(self):
		#pjt=frappe.get_doc("Project", self.project)
		#pjt.broiler_batch=self.name
		#pjt.save()
		pass

	def before_rename(doctype,old,new,merge):
		name=frappe.db.get_value('Project',new,'name')
		if name:
			frappe.throw('Project with name '+str(new)+' Exist, Please Choose Another name or Delete Existing Project')
		else:
			frappe.rename_doc('Project', old, new)
			frappe.db.set_value('Layer Batch', old, 'project', new)

	def on_update(self):
		pjt=frappe.get_doc("Project", self.name)
		
		if pjt.status!=self.status:
			pjt.status=	self.status
			if self.status=='Completed':
				pjt.expected_end_date=self.completed_date
			pjt.save()

		if self.status=='Completed':
			frappe.db.set_value('Layer Batch',self.name,'item_processed','2')

@frappe.whitelist()
def stock_entry(batch,transfer_qty,rooster_qty,transfer_date,transfer_warehouse=''):
	lbatch=frappe.get_doc('Layer Batch',batch)
	transfer_qty=float(transfer_qty)
	if int(transfer_qty) <= 0 :
		frappe.throw(_("Please set Transfer Quantity "))
	if lbatch.rearing_shed:
		sett=frappe.get_doc('Rearing Shed',lbatch.rearing_shed)
	
	lbatch.flock_transferred_to_layer=transfer_qty
	#current_alive_chicks
	time=''
	date=''
	if time:
		time=get_datetime(time)
	if transfer_date:
		date=getdate(transfer_date)
	
	posting_date=date or nowdate() 
	#time=time or get_datetime()
	#posting_time=time.strftime("%H:%M:%S")
	posting_time='23:59:00'
	
	stock_entry = frappe.new_doc("Stock Entry")    
	stock_entry.company = lbatch.company
	stock_entry.letter_head = frappe.db.get_value('Company',lbatch.company,'default_letter_head') or 'No Letter Head'
	item_account_details = get_item_defaults(sett.base_row_material, sett.company)
	batch_no=''
	if sett.base_row_material==sett.finished_product:
		stock_entry.stock_entry_type = "Material Transfer"
		if item_account_details.has_batch_no:		
			batch=frappe.db.sql(""" select i.warehouse,i.batch_no from `tabPurchase Receipt` p left join `tabPurchase Receipt Item` i on i.parent=p.name 
			where p.docstatus=1 and i.item_code='{0}' and p.project='{1}' """.format(sett.base_row_material,lbatch.project),as_dict=1)
			if batch:
				batch_no=batch[0].batch_no
	else:
		stock_entry.stock_entry_type = "Repack"

	stock_entry.manufacturing_type='Layer Chicken'
	stock_entry.project = lbatch.project
	stock_entry.posting_date=posting_date
	stock_entry.posting_time=posting_time
	stock_entry.set_posting_time='1'
	transfer_warehouse=transfer_warehouse or sett.product_target_warehouse

	if stock_entry.stock_entry_type == "Repack":
		if sett.base_row_material:
			
			stock_uom = item_account_details.stock_uom
			conversion_factor = get_conversion_factor(sett.base_row_material, stock_uom).get("conversion_factor")
			cost_center=sett.cost_center or lbatch.cost_center or item_account_details.get("buying_cost_center")
			expense_account=sett.expense_account or item_account_details.get("expense_account")
			base_row_rate = get_incoming_rate({
							"item_code": sett.base_row_material,
							"warehouse": sett.row_material_target_warehouse,
							"posting_date": posting_date,
							"posting_time": posting_time,
							"qty": -1 * transfer_qty,
							'company':sett.company
						})
			precision = cint(frappe.db.get_default("float_precision")) or 3    
			amount=flt(transfer_qty * flt(base_row_rate), precision)
			stock_entry.append('items', {
							's_warehouse': sett.row_material_target_warehouse,
							'item_code': sett.base_row_material,
							'qty': transfer_qty,
							'actual_qty':transfer_qty,
							'uom': stock_uom,
							'cost_center':cost_center,					
							'ste_detail': item_account_details.name,
							'stock_uom': stock_uom,
							'expense_account':expense_account,
							'valuation_rate': base_row_rate,
							"basic_rate":base_row_rate, 	
							"basic_amount":amount,  
							"amount":amount,  
							"transfer_qty":transfer_qty,
							'conversion_factor': flt(conversion_factor),
							'batch_no':batch_no,
									
			})
		else:
			frappe.throw(_("Please set base Rowmaterial in Layer Shed settings for {0} ").format(sett.company))

		if sett.finished_product:
			item_account_details = get_item_defaults(sett.finished_product, sett.company)
			stock_uom = item_account_details.stock_uom
			conversion_factor = get_conversion_factor(sett.finished_product, stock_uom).get("conversion_factor")
			cost_center=sett.cost_center or lbatch.cost_center or item_account_details.get("buying_cost_center")
			expense_account=sett.expense_account or item_account_details.get("expense_account")                                
			precision = cint(frappe.db.get_default("float_precision")) or 3		
			amount=flt(int(transfer_qty) * flt(base_row_rate), precision)
			
			if item_account_details.has_batch_no:
				if not batch_no:
					manufacture_date=posting_date.strftime("%d-%m-%Y")
					batch_no='LY'+'-'+str(manufacture_date)+'-'+str(batch) 
					if not frappe.db.exists("Batch", {"name": batch_no}):
						ibatch = frappe.new_doc("Batch")
						ibatch.batch_id=batch_no
						ibatch.item=sett.finished_product
						ibatch.item_name=item_account_details.name
						ibatch.batch_qty=transfer_qty
						ibatch.manufacturing_date=posting_date
						ibatch.stock_uom=stock_uom
						ibatch.insert()	
			stock_entry.append('items', {
								't_warehouse': transfer_warehouse,
								'item_code': sett.finished_product,
								'qty': transfer_qty,
								'actual_qty':transfer_qty,
								'uom': stock_uom,
								'cost_center':cost_center,					
								'ste_detail': item_account_details.name,
								'stock_uom': stock_uom,
								'expense_account':expense_account,
								'valuation_rate': base_row_rate,
								"basic_rate":base_row_rate, 	
								"basic_amount":amount,  
								"amount":amount,  
								"transfer_qty":transfer_qty,
								'conversion_factor': flt(conversion_factor),
								'batch_no':batch_no,
								
							
			})
		else:
			frappe.throw(_("Please set Finished Item in Layer Shed settings for {0} ").format(sett.company))

		stock_entry.insert()
		stock_entry.docstatus=1
		stock_entry.save()
	else:
		
		if sett.row_material_target_warehouse!=transfer_warehouse:

			if sett.finished_product:

				base_row_rate = get_incoming_rate({
								"item_code": sett.base_row_material,
								"warehouse": sett.row_material_target_warehouse,
								"posting_date": posting_date,
								"posting_time": posting_time,
								"qty": -1 * transfer_qty,
								'company':sett.company
							})
							
				item_account_details = get_item_defaults(sett.finished_product, sett.company)
				stock_uom = item_account_details.stock_uom
				conversion_factor = get_conversion_factor(sett.finished_product, stock_uom).get("conversion_factor")
				cost_center=sett.cost_center or lbatch.cost_center or item_account_details.get("buying_cost_center")
				expense_account=sett.expense_account or item_account_details.get("expense_account")                                
				precision = cint(frappe.db.get_default("float_precision")) or 3		
				amount=flt(int(transfer_qty) * flt(base_row_rate), precision)
				
				if item_account_details.has_batch_no:
					if not batch_no:
						manufacture_date=posting_date.strftime("%d-%m-%Y")
						batch_no='LY'+'-'+str(manufacture_date)+'-'+str(batch) 
						if not frappe.db.exists("Batch", {"name": batch_no}):
							ibatch = frappe.new_doc("Batch")
							ibatch.batch_id=batch_no
							ibatch.item=sett.finished_product
							ibatch.item_name=item_account_details.name
							ibatch.batch_qty=transfer_qty
							ibatch.manufacturing_date=posting_date
							ibatch.stock_uom=stock_uom
							ibatch.insert()	
				stock_entry.append('items', {
									's_warehouse': sett.row_material_target_warehouse,
									't_warehouse': transfer_warehouse,
									'item_code': sett.finished_product,
									'qty': transfer_qty,
									'actual_qty':transfer_qty,
									'uom': stock_uom,
									'cost_center':cost_center,					
									'ste_detail': item_account_details.name,
									'stock_uom': stock_uom,
									'expense_account':expense_account,
									'valuation_rate': base_row_rate,
									"basic_rate":base_row_rate, 	
									"basic_amount":amount,  
									"amount":amount,  
									"transfer_qty":transfer_qty,
									'conversion_factor': flt(conversion_factor),
									'batch_no':batch_no,
									
								
				})
			else:
				frappe.throw(_("Please set Finished Item in Layer Shed settings for {0} ").format(sett.company))

			stock_entry.insert()
			stock_entry.docstatus=1
			stock_entry.save()

	#stock_entry.save()
	#stock_entry.insert()
	#stock_entry.docstatus=1
	#stock_entry.save()

	lbatch.rooster_qty=rooster_qty
	lbatch.item_processed=1
	lbatch.layer_status='Laying'
	lbatch.flock_transfer_date=posting_date
	lbatch.save()
	if stock_entry.stock_entry_type == "Material Transfer" and sett.row_material_target_warehouse==transfer_warehouse:
		frappe.msgprint('Layer Batch Status Changed to laying')
		return 'Batch Updated'
	else:
		url=frappe.utils.get_url_to_form('Stock Entry', stock_entry.name)
		frappe.msgprint('Stock Entry <a href="'+str(url)+'"  target="_blank" > '+str(stock_entry.name)+'</a> created')
		return 'Batch Updated'

def create_stock_entry_mortality(item,parent_field=''):
	lbatch=frappe.get_doc('Layer Batch',item.parent)
	if parent_field=='laying_mortality':	
		sett=frappe.get_doc('Laying Shed',lbatch.layer_shed)
	else:
		sett=frappe.get_doc('Rearing Shed',lbatch.rearing_shed)
	time=''
	date=''
	if item.date:
		date=getdate(item.date)

	if item.creation:
		time=get_datetime(item.creation)
		
	item_code=sett.base_row_material
	qty=item.total
	uom='Nos'

	posting_date=date or nowdate() 
	#time=time or get_datetime()
	#posting_time=time.strftime("%H:%M:%S")
	posting_time='23:59:00'
	stock_entry = frappe.new_doc("Stock Entry")    
	stock_entry.company = lbatch.company
	stock_entry.letter_head = frappe.db.get_value('Company',lbatch.company,'default_letter_head') or 'No Letter Head'	
	stock_entry.stock_entry_type = "Material Issue"	
	stock_entry.project = lbatch.project
	stock_entry.posting_date=posting_date
	stock_entry.posting_time=posting_time
	stock_entry.set_posting_time='1'
	batch_no=''
	item_account_details = get_item_defaults(item_code, sett.company)
	row_material_target_warehouse=sett.row_material_target_warehouse
	if item_account_details.has_batch_no:

		if parent_field=='laying_mortality':
			batch=frappe.db.sql("""select d.batch_no,d.t_warehouse as warehouse  from `tabStock Entry Detail` d left join `tabStock Entry` s on s.name=d.parent where 
			d.item_code='{0}' and s.manufacturing_type='Layer Chicken' and 
			s.docstatus=1 and s.project='{1}' """.format(item_code,lbatch.project),as_dict=1)
		else:
			batch=frappe.db.sql(""" select i.warehouse,i.batch_no from `tabPurchase Receipt` p left join `tabPurchase Receipt Item` i on i.parent=p.name 
			where p.docstatus=1 and i.item_code='{0}' and p.project='{1}' """.format(item_code,lbatch.project),as_dict=1)

		if batch:
			batch_no=batch[0].batch_no
			row_material_target_warehouse=batch[0].warehouse or sett.row_material_target_warehouse

	expense_account=sett.mortality_expense_account or item_account_details.get("expense_account")
	stock_uom = item_account_details.stock_uom
	conversion_factor = get_conversion_factor(item_code, uom).get("conversion_factor")
	cost_center=sett.cost_center or lbatch.cost_center or item_account_details.get("buying_cost_center")
	
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
								'batch_no':batch_no,
                                        
                })
	stock_entry.insert()
	stock_entry.docstatus=1
	stock_entry.save()

	
	litem=frappe.get_doc('Layer Mortality',item.name)
	litem.docstatus=1
	litem.stock_entry=stock_entry.name
	litem.issue='Yes'
	litem.save()
	frappe.db.set_value('Layer Mortality',item.name, 'docstatus', 1)
	url=frappe.utils.get_url_to_form('Stock Entry', stock_entry.name)
	frappe.msgprint('Stock Entry <a href="'+str(url)+'"  target="_blank" > '+str(stock_entry.name)+'</a> created')
	return stock_entry.as_dict()

def create_stock_entry(item,parent_field=''):
	lbatch=frappe.get_doc('Layer Batch',item.parent)	
	
	if lbatch.layer_status=='Laying':	
		sett=frappe.get_doc('Laying Shed',lbatch.layer_shed)
	else:
		sett=frappe.get_doc('Rearing Shed',lbatch.rearing_shed)
	time=''
	date=''
	if item.date:
		date=getdate(item.date)

	if item.creation:
		time=get_datetime(item.creation)
		

	posting_date=date or nowdate() 
	time=time or get_datetime()
	#posting_time=time.strftime("%H:%M:%S")
	posting_time='23:59:00'
	stock_entry = frappe.new_doc("Stock Entry")    
	stock_entry.company = lbatch.company
	stock_entry.letter_head = frappe.db.get_value('Company',lbatch.company,'default_letter_head') or 'No Letter Head'	
	stock_entry.stock_entry_type = "Material Issue"	
	stock_entry.project = lbatch.project
	stock_entry.posting_date=posting_date
	stock_entry.posting_time=posting_time
	stock_entry.set_posting_time='1'
	item_account_details = get_item_defaults(item.item_code, sett.company)
	stock_uom = item_account_details.stock_uom
	conversion_factor = get_conversion_factor(item.item_code, item.uom).get("conversion_factor")
	cost_center=sett.cost_center or lbatch.cost_center or item_account_details.get("buying_cost_center")
	
	item_code=item.item_code
	row_material_target_warehouse=sett.row_material_target_warehouse
	expense_account=item_account_details.get("expense_account")
	if parent_field in ['laying_items','rearing_items']:
		expense_account=sett.other_items_expense_account or item_account_details.get("expense_account")
		row_material_target_warehouse=sett.other_item_warehouse
	elif parent_field in ['laying_medicine','rearing_medicine'] :
		expense_account=sett.medicine_expense_account or item_account_details.get("expense_account")
		row_material_target_warehouse=sett.medicine_warehouse
	elif parent_field in ['laying_feed','rearing_feed'] :
		expense_account=sett.feed_expense_account or item_account_details.get("expense_account")
		row_material_target_warehouse=sett.feed_warehouse
	

		
	
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
	if parent_field in ['laying_items','rearing_items']:
		tbl='Layer Other Items'
	elif parent_field in ['laying_medicine','rearing_medicine']:
		tbl='Layer Medicine'
	elif parent_field in ['laying_feed','rearing_feed']:
		tbl='Layer Feed'
	
		
	if tbl:
		litem=frappe.get_doc(tbl,item.name)
		litem.docstatus=1
		#if parent_field in ['laying_items','laying_medicine','laying_vaccine','laying_feed']:
		litem.issue='Yes'
		litem.stock_entry=stock_entry.name
		litem.save()
		frappe.db.set_value(tbl, item.name, 'docstatus', 1)
	url=frappe.utils.get_url_to_form('Stock Entry', stock_entry.name)
	frappe.msgprint('Stock Entry <a href="'+str(url)+'"  target="_blank" > '+str(stock_entry.name)+'</a> created')
	return stock_entry.as_dict()

def create_production_stock_entry(fitemdata,batch,posting_date,posting_time):
	
	lbatch=frappe.get_doc('Layer Batch',batch)
	if lbatch.layer_shed:
		sett=frappe.get_doc('Laying Shed',lbatch.layer_shed)
	
	stock_entry = frappe.new_doc("Stock Entry")    
	stock_entry.company = lbatch.company
	stock_entry.letter_head = frappe.db.get_value('Company',lbatch.company,'default_letter_head') or 'No Letter Head'    
	stock_entry.posting_date = posting_date
	stock_entry.posting_time = posting_time
	stock_entry.set_posting_time='1'
	stock_entry.purpose = "Manufacture"
	stock_entry.project = lbatch.project
	stock_entry.stock_entry_type = "Manufacture"
	stock_entry.manufacturing_type = "Egg"
	pcitems=[]
	for fitem in fitemdata:

		#if fitem.date:
		#	date=getdate(fitem.date)

		#if fitem.creation:
		#	time=get_datetime(fitem.creation)
			
		#posting_date=date or nowdate() 
		#time=time or get_datetime()
		#posting_time=time.strftime("%H:%M:%S")
		#posting_time='23:59:00'

		pcmaterials=''
		if fitem.bom:
			pcmaterials=frappe.get_doc('Finished Product BOM',fitem.bom)
		else:
			bom=frappe.db.get_value('Finished Product BOM',{'item':fitem.item_code,'uom':fitem.uom,'is_default':'1'},'name')
			if not bom:
				bom=frappe.db.get_value('Finished Product BOM',{'item':fitem.item_code,'uom':fitem.uom},'name')
			if bom:
				pcmaterials=frappe.get_doc('Finished Product BOM',bom)
		#Finished Product BOM

		#stock_entry.set_stock_entry_type()
		precision = 6
		itemscost=0
		item_account_details = get_item_defaults(fitem.item_code, lbatch.company)
		stock_adjustment_account=frappe.db.get_value('Company',sett.company,'stock_adjustment_account')
		if pcmaterials:
			for pcitem in pcmaterials.packing_item:
				pack_item_details = get_item_defaults(pcitem.item, lbatch.company)
				stock_uom = pack_item_details.stock_uom
				conversion_factor = get_conversion_factor(pcitem.item, pcitem.uom).get("conversion_factor")
				cost_center=sett.cost_center or pack_item_details.get("buying_cost_center")
				#expense_account=pack_item_details.get("expense_account")		
				expense_account=stock_adjustment_account or item_account_details.get("expense_account")                
				item_name=pack_item_details.get("item_name")
				packed_qty=float(pcitem.qty)*float(fitem.qty)
				pck_rate = get_incoming_rate({
								"item_code": pcitem.item,
								"warehouse": sett.packing_material_source_warehouse,
								"posting_date": posting_date,
								"posting_time": posting_time,
								"qty": -1 * packed_qty,
								'company':lbatch.company
							}) or 0
										
				transfer_qty=flt(float(packed_qty) * float(conversion_factor),6)
				amount=flt(float(transfer_qty) * float(pck_rate), precision)
				itemscost+=transfer_qty * pck_rate
				#pcitems.append({
				stock_entry.append('items', {
							's_warehouse': sett.packing_material_source_warehouse,
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
		#expense_account=item_account_details.get("expense_account")
		expense_account=stock_adjustment_account or item_account_details.get("expense_account")                
		item_name=item_account_details.get("item_name")
		base_rate=0

		batch_no=''
		if item_account_details.has_batch_no:
			manufacture_date=posting_date
			itemname=str(fitem.item_code)
			itemname=itemname[0:2]
			cat=lbatch.batch_type or 'Layer Eggs'
			pre_fix=frappe.db.get_value('Egg Finished Item Production Settings',{'item_code':fitem.item_code,'category':cat},'batch_prefix')
			pre_fix= pre_fix or itemname
			batch_no=str(pre_fix)+'-'+str(manufacture_date)		
			if not frappe.db.exists("Batch", {"name": batch_no}):
				ibatch = frappe.new_doc("Batch")
				ibatch.batch_id=batch_no
				ibatch.item=fitem.item_code
				ibatch.item_name=item_name
				ibatch.batch_qty=fitem.qty
				ibatch.manufacturing_date=posting_date
				ibatch.stock_uom=stock_uom
				ibatch.insert()
		stock_uom_rate=0
		if itemscost:
			base_rate=itemscost/float(fitem.qty)
			stock_uom_rate=base_rate/conversion_factor		
		amount=float(fitem.qty) * float(base_rate)
		#stock_entry.append('items', {
		pcitems.append({            
						't_warehouse': sett.product_target_warehouse,
						'item_code': fitem.item_code,
						'qty': fitem.qty,
						'actual_qty':fitem.qty,
						'uom': fitem.uom,
						'cost_center':cost_center,					
						'ste_detail': item_name,
						'stock_uom': stock_uom,
						'expense_account':expense_account,
						'valuation_rate': stock_uom_rate,
						"basic_rate":stock_uom_rate, 	
						"basic_amount":amount,  
						"amount":amount,  
						"transfer_qty":fitem.qty,
						'conversion_factor': flt(conversion_factor),
						'is_finished_item':1,
						'set_basic_rate_manually':1,
						'batch_no':batch_no,                  
				})
		litem=frappe.get_doc('Egg Production',fitem.name)
		litem.rate=stock_uom_rate
		litem.save()

	for pc in pcitems:
		stock_entry.append('items',pc)

	stock_entry.insert()
	stock_entry.docstatus=1
	stock_entry.save()

	for fitem in fitemdata:
		litem=frappe.get_doc('Egg Production',fitem.name)
		litem.docstatus=1
		litem.stock_entry=stock_entry.name
		litem.save()
		frappe.db.set_value('Egg Production',fitem.name, 'docstatus', 1)

	url=frappe.utils.get_url_to_form('Stock Entry', stock_entry.name)
	frappe.msgprint('Stock Entry <a href="'+str(url)+'"  target="_blank" > '+str(stock_entry.name)+'</a> created')
	return stock_entry.as_dict()

@frappe.whitelist()
def added_feed_rearing(batch,parentfield,date,item_code,qty,uom,material_transfer=''):
	
	item_name=frappe.db.get_value('Item',item_code,'item_name')
	itemdet=get_item_rate(batch,item_code,qty,uom,'rear','Feed',date='',time='')
	rate=itemdet.rate
	conversion_factor=itemdet.conversion_factor
	
	midx=frappe.db.sql("""select max(idx) from `tabLayer Feed` where parentfield='{0}' and parent='{1}' """.format(parentfield,batch))
	curidx=1
	if midx and midx[0][0] is not None:
		curidx = cint(midx[0][0])+1
	childtbl = frappe.new_doc("Layer Feed")
	childtbl.update({'idx':curidx,'date':date,'rate':rate,'material_transfer':material_transfer,'conversion_factor':conversion_factor,'item_code':item_code,'item_name':item_name,'qty':qty,'uom':uom,'parent': batch,'parenttype': 'Layer Batch','parentfield': parentfield})
	childtbl.save()
	#if parentfield=='laying_feed':
	create_stock_entry(childtbl,parentfield)

	return childtbl.as_dict()

@frappe.whitelist()
def update_feed_rearing(idx,parent,parentfield,name,date,item_code,qty,uom):
	if 'new-' in name:
		name=frappe.db.get_value('Layer Feed', {'parent': parent,'idx':idx,'parentfield':parentfield}, ['name'])
	
	itemdet=get_item_rate(parent,item_code,qty,uom,'rear','Feed',date='',time='')
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
def added_medicine_rearing(batch,parentfield,date,item_code,qty,uom,remark='',material_transfer=''):
	
	item_name=frappe.db.get_value('Item',item_code,'item_name')
	itemdet=get_item_rate(batch,item_code,qty,uom,'rear','Med',date='',time='')
	rate=itemdet.rate
	conversion_factor=itemdet.conversion_factor
	
	midx=frappe.db.sql("""select max(idx) from `tabLayer Medicine` where parentfield='{0}' and parent='{1}' """.format(parentfield,batch))
	curidx=1
	if midx and midx[0][0] is not None:
		curidx = cint(midx[0][0])+1
	childtbl = frappe.new_doc("Layer Medicine")
	childtbl.update({'idx':curidx,'date':date,'rate':rate,'material_transfer':material_transfer,'conversion_factor':conversion_factor,'item_code':item_code,'item_name':item_name,'qty':qty,'uom':uom,'remark':remark,'parent': batch,'parenttype': 'Layer Batch','parentfield': parentfield})
	childtbl.save()
	#if parentfield=='laying_medicine':
	create_stock_entry(childtbl,parentfield)
	return childtbl.as_dict()
	
@frappe.whitelist()
def update_medicine_rearing(idx,parent,parentfield,name,date,item_code,qty,uom,remark=''):
	if 'new-' in name:
		name=frappe.db.get_value('Layer Medicine', {'parent': parent,'idx':idx,'parentfield':parentfield}, ['name'])

	item_name=frappe.db.get_value('Item',item_code,'item_name')
	itemdet=get_item_rate(parent,item_code,qty,uom,'rear','Med',date='',time='')
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
def add_rearing_items(batch,parentfield,date,item_code,qty,uom,material_transfer=''):
	
	item_name=frappe.db.get_value('Item',item_code,'item_name')
	itemdet=get_item_rate(batch,item_code,qty,uom,'rear','oth',date='',time='')
	rate=itemdet.rate
	conversion_factor=itemdet.conversion_factor
	
	midx=frappe.db.sql("""select max(idx) from `tabLayer Other Items` where parentfield='{0}' and parent='{1}' """.format(parentfield,batch))
	curidx=1
	if midx and midx[0][0] is not None:
		curidx = cint(midx[0][0])+1
	childtbl = frappe.new_doc("Layer Other Items")
	childtbl.update({'idx':curidx,'date':date,'item_code':item_code,'material_transfer':material_transfer,'rate':rate,'conversion_factor':conversion_factor,'item_name':item_name,'qty':qty,'uom':uom,'parent': batch,'parenttype': 'Layer Batch','parentfield': parentfield})
	childtbl.save()
	#if parentfield=='laying_items':
	create_stock_entry(childtbl,parentfield)
	return childtbl.as_dict()

@frappe.whitelist()
def update_items_rearing(idx,parent,parentfield,name,date,item_code,qty,uom):
	if 'new-' in name:
		name=frappe.db.get_value('Layer Other Items', {'parent': parent,'idx':idx,'parentfield':parentfield}, ['name'])
	
	itemdet=get_item_rate(parent,item_code,qty,uom,'rear','oth',date='',time='')
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
	#if parentfield=='laying_mortality':
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
def add_eggs_production(batch,parentfield,items,production_date,production_time):
	
	import json
	aList = json.loads(items)
	#frappe.msgprint(items)
	item_data=[]
	res=''
	if not production_date:
		date=getdate()
	else:
		date=getdate(production_date)

	if not production_time:
		times=get_datetime()
	else:
		times=get_datetime(production_time)

	time=times.strftime("%H:%M:%S")


	for lst in aList:
		item_code=lst.get('item_code')
		qty=lst.get('qty')
		uom=lst.get('uom')
		bom=lst.get('bom')
		#date=lst.get('date')
		item_name=frappe.db.get_value('Item',item_code,'item_name')
		itemdet=get_item_rate(batch,item_code,qty,uom,'lay','Pd',date,time)
		rate=itemdet.rate
		conversion_factor=itemdet.conversion_factor
		
		midx=frappe.db.sql("""select max(idx) from `tabEgg Production` where parentfield='{0}' and parent='{1}' """.format(parentfield,batch))
		curidx=1
		if midx and midx[0][0] is not None:
			curidx = cint(midx[0][0])+1
		childtbl = frappe.new_doc("Egg Production")
		childtbl.update({'idx':curidx,'date':date,'rate':rate,'conversion_factor':conversion_factor,'item_code':item_code,'item_name':item_name,'qty':qty,'uom':uom,'bom':bom,'parent': batch,'parenttype': 'Layer Batch','parentfield': parentfield})
		childtbl.save()
		item_data.append(childtbl)

	if aList:
		res=create_production_stock_entry(item_data,batch,date,time)

	return res

@frappe.whitelist()
def update_egg_production(idx,parent,parentfield,name,date,item_code,qty,uom):
	if 'new-' in name:
		name=frappe.db.get_value('Egg Production', {'parent': parent,'idx':idx,'parentfield':parentfield}, ['name'])
	
	itemdet=get_item_rate(parent,item_code,qty,uom,'lay','Pd',date='',time='')
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

def get_item_rate(batch,item,qty,uom,typ='lay',item_typ='',date='',time=''):
	res={}

	if typ=='lay':
		shed=frappe.get_value('Layer Batch',{'batch_name':batch},'layer_shed')
		sett = frappe.get_doc('Laying Shed',shed)
	else:
		shed=frappe.get_value('Layer Batch',{'batch_name':batch},'rearing_shed')
		sett = frappe.get_doc('Rearing Shed',shed)

	if item_typ=='Feed':
		warehouse=sett.feed_warehouse
	elif item_typ=='Med':
		warehouse=sett.medicine_warehouse
	elif item_typ=='Pd':
		warehouse=sett.product_target_warehouse
	else:
		warehouse=sett.row_material_target_warehouse

	if time:
		time=get_datetime(time)
	else:
		time=get_datetime('23:59:00')
	if date:
		date=getdate(date)

	posting_date=date or nowdate() 
	time=time or get_datetime()
	posting_time=time.strftime("%H:%M:%S")
	#posting_time='23:59:00'
	base_row_rate = get_incoming_rate({
										"item_code": item,
										"warehouse": warehouse,
										"posting_date": posting_date,
										"posting_time": posting_time,
										"qty": -1 * qty,
										'company':sett.company
										})
	conversion_factor = get_conversion_factor(item, uom).get("conversion_factor")
	rate=base_row_rate * float(conversion_factor)
	res.update({'rate':base_row_rate,'conversion_factor':conversion_factor})
	return frappe._dict(res)


@frappe.whitelist()
def get_egg_products(cat):
	finitem=frappe.db.get_all('Egg Finished Item Production Settings', filters={"category": cat },fields=['item_code','item_name','default_uom'])
	for itm in finitem:
		boms=frappe.db.get_value('Finished Product BOM',{'item':itm.item_code,'uom':itm.default_uom,'is_default':'1'},['name','uom'], as_dict=1)
		if boms:
			itm.update({'default_bom':boms.name})
			itm.update({'uom':boms.uom})
		else:
			itm.update({'default_bom':''})

	return finitem


@frappe.whitelist()
def cancel_item(doc,event):
	batch=doc.project
	if doc.manufacturing_type=='Layer Chicken':
		
		if batch:
			frappe.db.set_value('Layer Batch', batch, 'item_processed', '0')
			frappe.db.set_value('Layer Batch', batch, 'layer_status', 'Rearing')
			frappe.db.set_value('Layer Batch', batch, 'flock_transferred_to_layer', '0')
			

	frappe.db.delete("Layer Other Items", {"stock_entry": doc.name,'parent':batch})
	frappe.db.delete("Layer Feed", {"stock_entry": doc.name ,'parent':batch})
	#frappe.db.delete("Layer Vaccine", {"stock_entry": doc.name })
	frappe.db.delete("Layer Medicine", {"stock_entry": doc.name,'parent':batch})
	frappe.db.delete("Egg Production", {"stock_entry": doc.name,'parent':batch})
	lay=frappe.db.get_value("Layer Mortality",{'stock_entry':doc.name,'parent':batch},['parent','total'], as_dict=1)
	if lay:
		current_alive_chicks=frappe.db.get_value("Layer Batch",{'name':lay.parent},['current_alive_chicks'])
		current_alive_chicks=current_alive_chicks+lay.total
		frappe.db.set_value('Layer Batch', lay.parent, 'current_alive_chicks', current_alive_chicks)
		frappe.db.delete("Layer Mortality", {"stock_entry": doc.name,'parent':batch})


@frappe.whitelist()
def get_material_transfer(material_transfer,project,shed):
	sett=shed=frappe.get_doc("Rearing Shed", shed)
	values = {'parent': material_transfer,'project':project}
	posting_date=frappe.db.get_value("Stock Entry",material_transfer,'posting_date')
	data = frappe.db.sql(""" SELECT item_code,item_name,qty,uom,t_warehouse,basic_rate,conversion_factor       
    FROM `tabStock Entry Detail`  WHERE parent = %(parent)s  """, values=values, as_dict=1,debug=0)

	vacc=[]
	'''medidx=frappe.db.sql("""select max(idx) from `tabLayer Vaccine` where parentfield='rearing_vaccine' and parent='{0}' """.format(project))
	vidx=1
	if medidx and medidx[0][0] is not None:
		vidx = cint(medidx[0][0])+1'''

	med=[]
	medidx=frappe.db.sql("""select max(idx) from `tabLayer Medicine` where parentfield='rearing_medicine' and parent='{0}' """.format(project))
	midx=1
	if medidx and medidx[0][0] is not None:
		midx = cint(medidx[0][0])+1

	feed=[]
	medidx=frappe.db.sql("""select max(idx) from `tabLayer Feed` where parentfield='rearing_feed' and parent='{0}' """.format(project))
	fidx=1
	if medidx and medidx[0][0] is not None:
		fidx = cint(medidx[0][0])+1

	other=[]
	medidx=frappe.db.sql("""select max(idx) from `tabLayer Other Items` where parentfield='rearing_items' and parent='{0}' """.format(project))
	oidx=1
	if medidx and medidx[0][0] is not None:
		oidx = cint(medidx[0][0])+1

	retdata=[]

	if data:
		for dt in data:
			
			issuedqty=0
			tranqty=0
			

			if sett.medicine_warehouse==dt.t_warehouse:
				#if not frappe.db.exists("Layer Medicine", {"material_transfer": material_transfer}):
				chk=frappe.db.sql("""select sum(qty) as qty from `tabLayer Medicine` where material_transfer='{0}' and item_code='{1}' """.format(material_transfer,dt.item_code),as_dict=1)
				if chk:
					issuedqty=chk[0].qty or 0
				if float(issuedqty) < float(dt.qty):
					if issuedqty > 0:
						tranqty=float(dt.qty)-float(issuedqty)
					else:
						tranqty=float(dt.qty)
				if tranqty>0:
					dt.update({'qty':tranqty,'date':posting_date,'tbl':'medicine','material_transfer':material_transfer})
					med.append({'idx':midx,'date':posting_date,'rate':dt.basic_rate,'material_transfer':material_transfer,'conversion_factor':dt.conversion_factor,'item_code':dt.item_code,'item_name':dt.item_name,'qty':dt.qty,'uom':dt.uom,'parent': project,'parenttype': 'Layer Batch','parentfield': 'rearing_medicine'})
					midx+=1
					retdata.append(dt)

			if sett.other_item_warehouse==dt.t_warehouse:
				#if not frappe.db.exists("Layer Other Items", {"material_transfer": material_transfer}):
				chk=frappe.db.sql("""select sum(qty) as qty from `tabLayer Other Items` where material_transfer='{0}' and item_code='{1}' """.format(material_transfer,dt.item_code),as_dict=1)
				if chk:
					issuedqty=chk[0].qty or 0
				if float(issuedqty) < float(dt.qty):
					if issuedqty > 0:
						tranqty=float(dt.qty)-float(issuedqty)
					else:
						tranqty=float(dt.qty)
				if tranqty>0:
					dt.update({'qty':tranqty,'date':posting_date,'tbl':'item','material_transfer':material_transfer})
					other.append({'idx':oidx,'date':posting_date,'rate':dt.basic_rate,'material_transfer':material_transfer,'conversion_factor':dt.conversion_factor,'item_code':dt.item_code,'item_name':dt.item_name,'qty':dt.qty,'uom':dt.uom,'parent': project,'parenttype': 'Layer Batch','parentfield': 'rearing_items'})
					oidx+=1
					retdata.append(dt)

			if sett.feed_warehouse==dt.t_warehouse:
				#if not frappe.db.exists("Layer Feed", {"material_transfer": material_transfer}):
				chk=frappe.db.sql("""select sum(qty) as qty from `tabLayer Feed` where material_transfer='{0}' and item_code='{1}' """.format(material_transfer,dt.item_code),as_dict=1)
				if chk:
					issuedqty=chk[0].qty or 0
				if float(issuedqty) < float(dt.qty):
					if issuedqty > 0:
						tranqty=float(dt.qty)-float(issuedqty)
					else:
						tranqty=float(dt.qty)
				if tranqty>0:
					dt.update({'qty':tranqty,'date':posting_date,'tbl':'feed','material_transfer':material_transfer})					
					feed.append({'idx':fidx,'date':posting_date,'rate':dt.basic_rate,'material_transfer':material_transfer,'conversion_factor':dt.conversion_factor,'item_code':dt.item_code,'item_name':dt.item_name,'qty':dt.qty,'uom':dt.uom,'parent': project,'parenttype': 'Layer Batch','parentfield': 'rearing_feed'})
					fidx+=1
					retdata.append(dt)
		
		

		if len(med):
			for vc in med:
				childtbl = frappe.new_doc("Layer Medicine")
				childtbl.update(vc)
				childtbl.save()

		if len(feed):			
			for vc in feed:
				childtbl = frappe.new_doc("Layer Feed")
				childtbl.update(vc)
				childtbl.save()

		if len(other):
			for vc in other:
				childtbl = frappe.new_doc("Layer Other Items")
				childtbl.update(vc)
				childtbl.save()
			
		
	return retdata

@frappe.whitelist()
def get_material_transfer_lay(material_transfer,project,shed):
	sett=shed=frappe.get_doc("Laying Shed", shed)
	values = {'parent': material_transfer,'project':project}
	posting_date=frappe.db.get_value("Stock Entry",material_transfer,'posting_date')
	data = frappe.db.sql(""" SELECT item_code,item_name,qty,uom,t_warehouse,basic_rate,conversion_factor       
    FROM `tabStock Entry Detail`  WHERE parent = %(parent)s  """, values=values, as_dict=1,debug=0)

	
	med=[]
	medidx=frappe.db.sql("""select max(idx) from `tabLayer Medicine` where parentfield='laying_medicine' and parent='{0}' """.format(project))
	midx=1
	if medidx and medidx[0][0] is not None:
		midx = cint(medidx[0][0])+1

	feed=[]
	medidx=frappe.db.sql("""select max(idx) from `tabLayer Feed` where parentfield='laying_feed' and parent='{0}' """.format(project))
	fidx=1
	if medidx and medidx[0][0] is not None:
		fidx = cint(medidx[0][0])+1

	other=[]
	medidx=frappe.db.sql("""select max(idx) from `tabLayer Other Items` where parentfield='laying_items' and parent='{0}' """.format(project))
	oidx=1
	if medidx and medidx[0][0] is not None:
		oidx = cint(medidx[0][0])+1

	retdata=[]

	if data:
		for dt in data:
			issuedqty=0
			tranqty=0
				

			if sett.medicine_warehouse==dt.t_warehouse:
				#if not frappe.db.exists("Layer Medicine", {"material_transfer": material_transfer}):
				chk=frappe.db.sql("""select sum(qty) as qty from `tabLayer Medicine` where material_transfer='{0}' and item_code='{1}' """.format(material_transfer,dt.item_code),as_dict=1)
				if chk:
					issuedqty=chk[0].qty or 0
				if float(issuedqty) < float(dt.qty):
					if issuedqty > 0:
						tranqty=float(dt.qty)-float(issuedqty)
					else:
						tranqty=float(dt.qty)
				if tranqty>0:
					dt.update({'qty':tranqty,'date':posting_date,'tbl':'medicine','material_transfer':material_transfer})
					med.append({'idx':midx,'date':posting_date,'rate':dt.basic_rate,'material_transfer':material_transfer,'conversion_factor':dt.conversion_factor,'item_code':dt.item_code,'item_name':dt.item_name,'qty':dt.qty,'uom':dt.uom,'parent': project,'parenttype': 'Layer Batch','parentfield': 'laying_medicine'})
					midx+=1
					retdata.append(dt)

			if sett.other_item_warehouse==dt.t_warehouse:
				#if not frappe.db.exists("Layer Other Items", {"material_transfer": material_transfer}):
				chk=frappe.db.sql("""select sum(qty) as qty from `tabLayer Other Items` where material_transfer='{0}' and item_code='{1}' """.format(material_transfer,dt.item_code),as_dict=1)
				if chk:
					issuedqty=chk[0].qty or 0
				if float(issuedqty) < float(dt.qty):
					if issuedqty > 0:
						tranqty=float(dt.qty)-float(issuedqty)
					else:
						tranqty=float(dt.qty)
				if tranqty>0:
					dt.update({'qty':tranqty,'date':posting_date,'tbl':'item','material_transfer':material_transfer})
					other.append({'idx':oidx,'date':posting_date,'rate':dt.basic_rate,'material_transfer':material_transfer,'conversion_factor':dt.conversion_factor,'item_code':dt.item_code,'item_name':dt.item_name,'qty':dt.qty,'uom':dt.uom,'parent': project,'parenttype': 'Layer Batch','parentfield': 'laying_items'})
					oidx+=1
					retdata.append(dt)

			if sett.feed_warehouse==dt.t_warehouse:
				#if not frappe.db.exists("Layer Feed", {"material_transfer": material_transfer}):
				chk=frappe.db.sql("""select sum(qty) as qty from `tabLayer Feed` where material_transfer='{0}' and item_code='{1}' """.format(material_transfer,dt.item_code),as_dict=1)
				if chk:
					issuedqty=chk[0].qty or 0
				if float(issuedqty) < float(dt.qty):
					if issuedqty > 0:
						tranqty=float(dt.qty)-float(issuedqty)
					else:
						tranqty=float(dt.qty)
				if tranqty>0:
					dt.update({'qty':tranqty,'date':posting_date,'tbl':'feed','material_transfer':material_transfer})					
					feed.append({'idx':fidx,'date':posting_date,'rate':dt.basic_rate,'material_transfer':material_transfer,'conversion_factor':dt.conversion_factor,'item_code':dt.item_code,'item_name':dt.item_name,'qty':dt.qty,'uom':dt.uom,'parent': project,'parenttype': 'Layer Batch','parentfield': 'laying_feed'})
					fidx+=1
					retdata.append(dt)
		

		if len(med):
			for vc in med:
				childtbl = frappe.new_doc("Layer Medicine")
				childtbl.update(vc)
				childtbl.save()

		if len(feed):			
			for vc in feed:
				childtbl = frappe.new_doc("Layer Feed")
				childtbl.update(vc)
				childtbl.save()

		if len(other):
			for vc in other:
				childtbl = frappe.new_doc("Layer Other Items")
				childtbl.update(vc)
				childtbl.save()
			
		
	return retdata
		
@frappe.whitelist()
def laying_material_issue(batch,parentfield,items):
	import json
	aList = json.loads(items)
	lbatch=frappe.get_doc('Layer Batch',batch)	
	
	if lbatch.layer_status=='Laying':	
		sett=frappe.get_doc('Laying Shed',lbatch.layer_shed)
	else:
		sett=frappe.get_doc('Rearing Shed',lbatch.rearing_shed)
	time=''
	date=''
	if date:
		date=getdate(date)
	
	posting_date=date or nowdate() 
	#time=time or get_datetime()
	#posting_time=time.strftime("%H:%M:%S")
	posting_time='23:59:00'
	
	items=[]
	cost_center=sett.cost_center or lbatch.cost_center or item_account_details.get("buying_cost_center")
	
	for itm in aList:
		row_name=itm.get('name')

		if parentfield in ['laying_medicine','rearing_medicine']:
			item=frappe.get_doc('Layer Medicine',row_name)
			item_account_details = get_item_defaults(item.item_code, sett.company)
			expense_account=sett.medicine_expense_account or item_account_details.get("expense_account")
			row_material_target_warehouse=sett.medicine_warehouse
		if parentfield in ['laying_feed','rearing_feed']:
			item=frappe.get_doc('Layer Feed',row_name)
			item_account_details = get_item_defaults(item.item_code, sett.company)
			expense_account=sett.feed_expense_account or item_account_details.get("expense_account")
			row_material_target_warehouse=sett.feed_warehouse
		if parentfield in ['laying_items','rearing_items']:
			item=frappe.get_doc('Layer Other Items',row_name)
			item_account_details = get_item_defaults(item.item_code, sett.company)
			expense_account=sett.other_items_expense_account or item_account_details.get("expense_account")
			row_material_target_warehouse=sett.other_item_warehouse
		elif parentfield in ['laying_mortality','rearing_daily_mortality']:
			item=frappe.get_doc('Layer Mortality',row_name)
			item_account_details = get_item_defaults(item.item_code, sett.company)
			expense_account=sett.mortality_expense_account or item_account_details.get("expense_account")
			item_code=sett.base_row_material
			row_material_target_warehouse=sett.row_material_target_warehouse

		posting_date=getdate(item.date)
		stock_uom = item_account_details.stock_uom
		conversion_factor = get_conversion_factor(item.item_code, item.uom).get("conversion_factor")
		item_code=item.item_code

		stock_entry = frappe.new_doc("Stock Entry")    
		stock_entry.company = lbatch.company
		stock_entry.letter_head = frappe.db.get_value('Company',lbatch.company,'default_letter_head') or 'No Letter Head'	
		stock_entry.stock_entry_type = "Material Issue"	
		stock_entry.project = lbatch.project
		stock_entry.posting_date=posting_date
		stock_entry.set_posting_time='1'
		stock_entry.posting_time=posting_time

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

		item.docstatus=1
		item.issue='Yes'
		item.stock_entry=stock_entry.name
		item.save()
		frappe.db.set_value(item.doctype, item.name, 'docstatus', 1)
		items.append(item)
	frappe.msgprint('Stock Entrys created')
	return items

@frappe.whitelist()
def mortality_material_issue(batch,parentfield,items):
	import json
	aList = json.loads(items)
	lbatch=frappe.get_doc('Layer Batch',batch)	
	
	if lbatch.layer_status=='Laying':	
		sett=frappe.get_doc('Laying Shed',lbatch.layer_shed)
	else:
		sett=frappe.get_doc('Rearing Shed',lbatch.rearing_shed)
	time=''
	date=''
	if date:
		date=getdate(date)
	
	posting_date=date or nowdate() 
	#time=time or get_datetime()
	#posting_time=time.strftime("%H:%M:%S")
	posting_time='23:59:00'
	
	items=[]
	item_code=sett.base_row_material
	item_account_details = get_item_defaults(item_code, sett.company)
	cost_center=sett.cost_center or lbatch.cost_center or item_account_details.get("buying_cost_center")
	row_material_target_warehouse=sett.row_material_target_warehouse
	expense_account=sett.mortality_expense_account or item_account_details.get("expense_account")

	for itm in aList:
		row_name=itm.get('name')
		qty=itm.get('total')
		uom='Nos'
		item=frappe.get_doc('Layer Mortality',row_name)
		
		posting_date=getdate(item.date)
		stock_uom = item_account_details.stock_uom
		conversion_factor = get_conversion_factor(item_code, uom).get("conversion_factor")
		

		stock_entry = frappe.new_doc("Stock Entry")    
		stock_entry.company = lbatch.company
		stock_entry.letter_head = frappe.db.get_value('Company',lbatch.company,'default_letter_head') or 'No Letter Head'	
		stock_entry.stock_entry_type = "Material Issue"	
		stock_entry.project = lbatch.project
		stock_entry.posting_date=posting_date
		stock_entry.set_posting_time='1'
		stock_entry.posting_time=posting_time

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

		item.docstatus=1
		item.issue='Yes'
		item.stock_entry=stock_entry.name
		item.save()
		frappe.db.set_value(item.doctype, item.name, 'docstatus', 1)
		items.append(item)
	frappe.msgprint('Stock Entrys created')
	return items

@frappe.whitelist()
def sales_entry(batch,item,transfer_qty,transfer_date):
	lbatch=frappe.get_doc('Layer Batch',batch)
	
	
	if lbatch.item_processed=='0':
		sett=frappe.get_doc('Rearing Shed',lbatch.rearing_shed)
		warehouse=sett.row_material_target_warehouse
		batch_no=''	
	else:
		sett=frappe.get_doc('Laying Shed',lbatch.layer_shed)
		warehouse=sett.row_material_target_warehouse
		rearbatch=frappe.db.sql("""select d.batch_no,d.t_warehouse as batch_no from `tabStock Entry Detail` d left join `tabStock Entry` s on s.name=d.parent where 
	d.item_code='{0}' and s.stock_entry_type='Manufacture' and s.manufacturing_type='Layer Chicken' and 
	s.docstatus=1 and s.project='{1}' """.format(item,lbatch.project),as_dict=1)
		
		if rearbatch:
			batch_no=rearbatch[0].batch_no
			warehouse=rearbatch[0].t_warehouse or sett.row_material_target_warehouse

	if item=='MAN001':
		warehouse=''
		batch_no=''
	
	transfer_qty=float(transfer_qty)

	sales = frappe.new_doc("Sales Invoice")
	sales.company = sett.company
	sales.posting_date=transfer_date
	sales.project=lbatch.project
	sales.cost_center=sett.cost_center
	sales.set_posting_time='1'
	if item!='MAN001':
		sales.update_stock='1'
		sales.set_warehouse=warehouse

	item_account_details = get_item_defaults(item, sett.company)
	stock_uom = item_account_details.stock_uom
	conversion_factor = get_conversion_factor(item, stock_uom).get("conversion_factor")
	cost_center=sett.cost_center or item_account_details.get("buying_cost_center")
	expense_account=item_account_details.get("expense_account")
	if item!='MAN001':
		base_row_rate = get_incoming_rate({
							"item_code": item,
							"warehouse": warehouse,
							"posting_date": sales.posting_date,
							"posting_time": sales.posting_time,
							"qty": -1 * transfer_qty,
							'company':sett.company
						})
	else:
		base_row_rate=0

	# bin issue
	#if warehouse:
	#	validate_stock_qty(item,transfer_qty,warehouse,stock_uom,stock_uom)

	precision = cint(frappe.db.get_default("float_precision")) or 3    
	amount=flt(transfer_qty * flt(base_row_rate), precision)
	sales.append('items', {
                        'warehouse': warehouse,
                        'item_code': item,
						'item_name':item_account_details.item_name,
                        'qty': transfer_qty,
                        'uom': stock_uom,
                        'cost_center':cost_center,				
                        'stock_uom': stock_uom,
                        'expense_account':expense_account,
                        'rate': base_row_rate,                        
                        "amount":amount, 
                        'conversion_factor': flt(conversion_factor),                         
        })

	return sales.as_dict()

def validate_stock_qty(item_code,req_qty,warehouse,uom,stock_uom):
    
    if uom != stock_uom:
        conversion_factor = get_conversion_factor(item_code, uom).get("conversion_factor") or 1
        stock_qty=flt(req_qty*flt(conversion_factor),2)
    else:
        stock_qty=flt(req_qty,2)

    qty=frappe.db.get_value('Bin', {'item_code': item_code,'warehouse':warehouse}, ['actual_qty as qty'],debug=0)
    qty=qty or 0
    if(stock_qty > qty):
        frappe.throw(_("Req Qty {0}. There is no sufficient qty in {1} Please select another warehouse for {2}").format(stock_qty,warehouse,item_code))

@frappe.whitelist()
def sales_submit(doc,event):
	
	lbatch=frappe.db.sql(""" select * from `tabLayer Batch` where name='{0}' """.format(doc.project),as_dict=1)
	if lbatch:
		if lbatch[0].rearing_shed:
			sett=frappe.get_doc('Rearing Shed',lbatch[0].rearing_shed)
			reare_item=sett.base_row_material
			rs=frappe.db.sql(""" select i.qty as qty from `tabSales Invoice Item` i  where i.parent='{0}' and i.item_code='{1}'""".format(doc.name,reare_item),as_dict=1)
			if rs:
				sales_qty=float(lbatch[0].sales_qty)+float(rs[0].qty)
				current_alive_chicks=float(lbatch[0].current_alive_chicks)-float(rs[0].qty)
				frappe.db.set_value('Layer Batch',lbatch[0].name,'sales_qty',sales_qty)
				frappe.db.set_value('Layer Batch',lbatch[0].name,'current_alive_chicks',current_alive_chicks)
			
		if lbatch[0].layer_shed:
			sett=frappe.get_doc('Laying Shed',lbatch[0].layer_shed)
			layer_item=sett.base_row_material
			rs=frappe.db.sql(""" select i.qty as qty from `tabSales Invoice Item` i  where i.parent='{0}' and i.item_code='{1}'""".format(doc.name,layer_item),as_dict=1)
			if rs:
				sales_qty=float(lbatch[0].sales_qty)+float(rs[0].qty)
				current_alive_chicks=float(lbatch[0].current_alive_chicks)-float(rs[0].qty)
				frappe.db.set_value('Layer Batch',lbatch[0].name,'sales_qty',sales_qty)
				frappe.db.set_value('Layer Batch',lbatch[0].name,'current_alive_chicks',current_alive_chicks)
		

@frappe.whitelist()
def sales_cancel(doc,event):
	lbatch=frappe.db.sql(""" select * from `tabLayer Batch` where name='{0}' """.format(doc.project),as_dict=1)
	if lbatch:
		if lbatch[0].rearing_shed:
			sett=frappe.get_doc('Rearing Shed',lbatch[0].rearing_shed)
			reare_item=sett.base_row_material
			rs=frappe.db.sql(""" select i.qty as qty from `tabSales Invoice Item` i  where i.parent='{0}' and i.item_code='{1}'""".format(doc.name,reare_item),as_dict=1)
			if rs:
				sales_qty=float(lbatch[0].sales_qty)-float(rs[0].qty)
				current_alive_chicks=float(lbatch[0].current_alive_chicks)+float(rs[0].qty)
				frappe.db.set_value('Layer Batch',lbatch[0].name,'sales_qty',sales_qty)
				frappe.db.set_value('Layer Batch',lbatch[0].name,'current_alive_chicks',current_alive_chicks)
		if lbatch[0].layer_shed:
			sett=frappe.get_doc('Laying Shed',lbatch[0].layer_shed)
			layer_item=sett.base_row_material
			rs=frappe.db.sql(""" select i.qty as qty from `tabSales Invoice Item` i  where i.parent='{0}' and i.item_code='{1}'""".format(doc.name,layer_item),as_dict=1)
			if rs:
				sales_qty=float(lbatch[0].sales_qty)-float(rs[0].qty)
				current_alive_chicks=float(lbatch[0].current_alive_chicks)+float(rs[0].qty)
				frappe.db.set_value('Layer Batch',lbatch[0].name,'sales_qty',sales_qty)
				frappe.db.set_value('Layer Batch',lbatch[0].name,'current_alive_chicks',current_alive_chicks)