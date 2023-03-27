# Copyright (c) 2023, alantechnologies and contributors
# For license information, please see license.txt
import frappe
import erpnext
from frappe.utils import nowdate, cint, get_datetime, formatdate, getdate 
from frappe.model.document import Document
from erpnext.stock.utils import (get_incoming_rate)
from erpnext.stock.get_item_details import (get_conversion_factor)

class RearingBatch(Document):
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

@frappe.whitelist()
def stock_entry(batch,transfer_qty,transfer_date,transfer_warehouse=''):
	pass


@frappe.whitelist()
def added_feed_rearing(batch,parentfield,date,item_code,qty,uom):
	
	item_name=frappe.db.get_value('Item',item_code,'item_name')
	itemdet=get_item_rate(batch,item_code,qty,uom,date='',time='')
	rate=itemdet.get('rate')
	conversion_factor=itemdet.get('conversion_factor')
	
	midx=frappe.db.sql("""select max(idx) from `tabLayer Feed` where parentfield='{0}' and parent='{1}' """.format(parentfield,batch))
	curidx=1
	if midx and midx[0][0] is not None:
		curidx = cint(midx[0][0])+1
	childtbl = frappe.new_doc("Layer Feed")
	childtbl.update({'idx':curidx,'date':date,'rate':rate,'conversion_factor':conversion_factor,'item_code':item_code,'item_name':item_name,'qty':qty,'uom':uom,'parent': batch,'parenttype': 'Rearing Batch','parentfield': parentfield})
	childtbl.save()
	return childtbl.as_dict()

@frappe.whitelist()
def update_feed_rearing(idx,parent,parentfield,name,date,item_code,qty,uom):
	if 'new-' in name:
		name=frappe.db.get_value('Layer Feed', {'parent': parent,'idx':idx,'parentfield':parentfield}, ['name'])
	
	itemdet=get_item_rate(parent,item_code,qty,uom,date='',time='')
	rate=itemdet.get('rate')
	conversion_factor=itemdet.get('conversion_factor')

	doc = frappe.get_doc('Layer Feed', name)
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
def delete_feed_rearing(name):
	frappe.db.delete('Layer Feed', {"name": name })


@frappe.whitelist()
def added_medicine_rearing(batch,parentfield,date,item_code,qty,uom,remark=''):
	
	item_name=frappe.db.get_value('Item',item_code,'item_name')
	itemdet=get_item_rate(batch,item_code,qty,uom,date='',time='')
	rate=itemdet.get('rate')
	conversion_factor=itemdet.get('conversion_factor')
	
	midx=frappe.db.sql("""select max(idx) from `tabLayer Medicine` where parentfield='{0}' and parent='{1}' """.format(parentfield,batch))
	curidx=1
	if midx and midx[0][0] is not None:
		curidx = cint(midx[0][0])+1
	childtbl = frappe.new_doc("Layer Medicine")
	childtbl.update({'idx':curidx,'date':date,'rate':rate,'conversion_factor':conversion_factor,'item_code':item_code,'item_name':item_name,'qty':qty,'uom':uom,'remark':remark,'parent': batch,'parenttype': 'Rearing Batch','parentfield': parentfield})
	childtbl.save()
	return childtbl.as_dict()

	
@frappe.whitelist()
def update_medicine_rearing(idx,parent,parentfield,name,date,item_code,qty,uom,remark=''):
	if 'new-' in name:
		name=frappe.db.get_value('Layer Medicine', {'parent': parent,'idx':idx,'parentfield':parentfield}, ['name'])

	item_name=frappe.db.get_value('Item',item_code,'item_name')
	itemdet=get_item_rate(parent,item_code,qty,uom,date='',time='')
	rate=itemdet.get('rate')
	conversion_factor=itemdet.get('conversion_factor')
	doc = frappe.get_doc('Layer Medicine', name)
	doc.date = date
	doc.item_code = item_code
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
	rate=itemdet.get('rate')
	conversion_factor=itemdet.get('conversion_factor')
	midx=frappe.db.sql("""select max(idx) from `tabLayer Vaccine` where parentfield='{0}' and parent='{1}' """.format(parentfield,batch))
	curidx=1
	if midx and midx[0][0] is not None:
		curidx = cint(midx[0][0])+1
	childtbl = frappe.new_doc("Layer Vaccine")
	childtbl.update({'idx':curidx,'date':date,'rate':rate,'conversion_factor':conversion_factor,'item_code':item_code,'item_name':item_name,'qty':qty,'uom':uom,'remark':remark,'parent': batch,'parenttype': 'Rearing Batch','parentfield': parentfield})
	childtbl.save()
	return childtbl.as_dict()

@frappe.whitelist()
def update_vaccine_rearing(idx,parent,parentfield,name,date,item_code,qty,uom,remark=''):
	if 'new-' in name:
		name=frappe.db.get_value('Layer Vaccine', {'parent': parent,'idx':idx,'parentfield':parentfield}, ['name'])
	
	itemdet=get_item_rate(parent,item_code,qty,uom,date='',time='')
	rate=itemdet.get('rate')
	conversion_factor=itemdet.get('conversion_factor')
	doc = frappe.get_doc('Layer Vaccine', name)
	doc.date = date
	doc.item_code = item_code
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
	rate=itemdet.get('rate')
	conversion_factor=itemdet.get('conversion_factor')
	
	midx=frappe.db.sql("""select max(idx) from `tabLayer Other Items` where parentfield='{0}' and parent='{1}' """.format(parentfield,batch))
	curidx=1
	if midx and midx[0][0] is not None:
		curidx = cint(midx[0][0])+1
	childtbl = frappe.new_doc("Layer Other Items")
	childtbl.update({'idx':curidx,'date':date,'item_code':item_code,'rate':rate,'conversion_factor':conversion_factor,'item_name':item_name,'qty':qty,'uom':uom,'parent': batch,'parenttype': 'Rearing Batch','parentfield': parentfield})
	childtbl.save()
	return childtbl.as_dict()

@frappe.whitelist()
def update_items_rearing(idx,parent,parentfield,name,date,item_code,qty,uom):
	if 'new-' in name:
		name=frappe.db.get_value('Layer Other Items', {'parent': parent,'idx':idx,'parentfield':parentfield}, ['name'])
	
	itemdet=get_item_rate(parent,item_code,qty,uom,date='',time='')
	rate=itemdet.rate
	conversion_factor=itemdet.conversion_factor

	doc = frappe.get_doc('Layer Other Items', name)
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
	childtbl.update({'idx':curidx,'date':date,'age':age,'morning':morning,'evening':evening,'total':total,'remark':remark,'parent': batch,'parenttype': 'Rearing Batch','parentfield': parentfield})
	childtbl.save()
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
	childtbl.update({'idx':curidx,'date':date,'morning':morning,'evening':evening,'parent': batch,'parenttype': 'Rearing Batch','parentfield': parentfield})
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
	childtbl.update({'idx':curidx,'date':date,'week':week,'weight':weight,'parent': batch,'parenttype': 'Rearing Batch','parentfield': parentfield})
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

def get_item_rate(batch,item,qty,uom,date='',time=''):
	res={}
	shed=frappe.get_value('Rearing Batch',{'batch_name':batch},'rear_shed')
	if time:
		time=get_datetime(time)
	if date:
		date=getdate(date)

	sett = frappe.get_doc('Rearing Shed',shed)
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
	return res

