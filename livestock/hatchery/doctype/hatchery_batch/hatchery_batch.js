// Copyright (c) 2022, alantechnologies and contributors
// For license information, please see license.txt



// Copyright (c) 2022, alantechnologies and contributors
// For license information, please see license.txt
frappe.ui.form.on("Hatchery Batch", "before_save", function(frm, cdt, cdn) {
	var item = locals[cdt][cdn];	
	$.each (item.used_items, function(i, d){
		
				d.project=frm.doc.project_name;
			});
	});
frappe.ui.form.on('Hatchery Batch', {
	create_stock_entry: function(frm, cdt, cdn) 
            { 
                 var d = locals[cdt][cdn];
                 
                if(frm.doc.number_received < 1 || frm.doc.number_received===''){
					frappe.throw(__("Please Enter Number Of received eggs "));
					return false;
					}
					
				if(frm.doc.chicks_transferred < 1 || frm.doc.chicks_transferred===''){
					frappe.throw(__("Please Enter Chicks tranfered "));
					return false;
					}	
					
                if(frm.doc.__unsaved){
					frappe.throw(__("Please save document before generate stock entry"));
					return false;
					}
					
					
			//console.log(frm.doc);  
				frappe.call(
                    { 
                        method: "livestock.hatchery.doctype.hatchery_batch.hatchery_stock_entry.stock_entry",
                        args: { 
                            //doc: d,
                            batch:frm.doc.name
                        },
                        callback: function(r) 
                            { 
                                if(r.message) 
                                    { 
				                    	var doclist = frappe.model.sync(r.message);
				                        frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
                                    } 
                            }
                    });
			}
});
frappe.ui.form.on("Hatchery Items", 
    {
		item_code: function(frm, cdt, cdn) 
            { 
		var d = locals[cdt][cdn];
                const args = {
							"item_code": d.item_code,
							"posting_date":d.date,
							"warehouse":d.s_warehouse,
							"company":frm.doc.company,
							"qty":d.qty || 1,
							"allow_zero_valuation":1,
				};
                frappe.call(
                    { 
                        method: "erpnext.stock.utils.get_incoming_rate",
                        args: { 
                            args: args
                        },
                        callback: function(r) 
                            { 
                                if(r.message) 
                                    { 
                                        
				                    	d.rate=r.message;
				                    	d.qty=(d.qty)?d.qty:1;
                                        frm.refresh_fields()
					                    
                                    } 
                            }
                    });
                    
                    frappe.call(
                    { 
                        method: "livestock.poultry.doctype.poultry_items.poultry_items.get_item_stock_uom",
                        args: { 
                            "item_code":d.item_code
                        },
                        callback: function(r) 
                            { 
                                if(r.message) 
                                    { 
                                        d.uom = r.message; 
					                     frm.refresh_fields()
                                    } 
                            }
                    });
            } 
});

