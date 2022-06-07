// Copyright (c) 2022, alantechnologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mortality', {
	evening:function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		d.total=d.evening+d.morning
		frm.refresh_fields('total')
	},
	morning:function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		d.total=d.evening+d.morning
		frm.refresh_fields('total')
	},
});
frappe.ui.form.on('Broiler Batch', {
	refresh(frm) {
		frm.set_query('from_hatchery_project', function(doc, cdt, cdn) {
		  
			return {
			   "filters": {
			"project_type": "Hatchery",
		}
			};
		});

        if (frm.doc.item_processed!=1)
			{       
				frm.add_custom_button(__('Broiler Production Entry'), function(){
            
                    if(frm.doc.number_received < 1 || frm.doc.number_received===''){
                        frappe.throw(__("Please Enter Number Of DOC received"));
                        return false;
                        }
                        
                    if(frm.doc.doc_placed < 1 || frm.doc.doc_placed===''){
                        frappe.throw(__("Please Enter Chicks Placed "));
                        return false;
                        }	
                        
                    if(frm.doc.__unsaved){
                        frappe.throw(__("Please save document before generate stock entry"));
                        return false;
                        }
                        
                        
                //console.log(frm.doc);  
                    frappe.call(
                        { 
                            method: "livestock.broiler.doctype.broiler_batch.broiler_stock_entry.stock_entry",
                            args: {
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
               
                    }).removeClass("btn-default").addClass("btn-success");
			}
	},
	create_stock_entry: function(frm, cdt, cdn) 
            { 
                 var d = locals[cdt][cdn];
                 
                if(frm.doc.number_received < 1 || frm.doc.number_received===''){
					frappe.throw(__("Please Enter Number Of DOC received"));
					return false;
					}
					
				if(frm.doc.doc_placed < 1 || frm.doc.doc_placed===''){
					frappe.throw(__("Please Enter Chicks Placed "));
					return false;
					}	
					
                if(frm.doc.__unsaved){
					frappe.throw(__("Please save document before generate stock entry"));
					return false;
					}
					
					
			//console.log(frm.doc);  
				frappe.call(
                    { 
                        method: "livestock.broiler.doctype.broiler_batch.broiler_stock_entry.stock_entry",
                        args: {
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

frappe.ui.form.on("Broiler Items", 
    {
		item_code: function(frm, cdt, cdn) 
            { 
		    var d = locals[cdt][cdn];                
                    
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

frappe.ui.form.on("Feed", 
    {
		starter_item: function(frm, cdt, cdn) 
            { 
		        var d = locals[cdt][cdn];
                    frappe.call(
                    { 
                        method: "livestock.poultry.doctype.poultry_items.poultry_items.get_item_stock_uom",
                        args: { 
                            "item_code":d.starter_item
                        },
                        callback: function(r) 
                            { 
                                if(r.message) 
                                    { 
                                        d.starter_uom = r.message; 
					                     frm.refresh_fields()
                                    } 
                            }
                    });
            },
            finisher_item: function(frm, cdt, cdn) 
            {  
                var d = locals[cdt][cdn];
                    frappe.call(
                    { 
                        method: "livestock.poultry.doctype.poultry_items.poultry_items.get_item_stock_uom",
                        args: { 
                            "item_code":d.finisher_item
                        },
                        callback: function(r) 
                            { 
                                if(r.message) 
                                    { 
                                        d.finisher_uom = r.message; 
					                     frm.refresh_fields()
                                    } 
                            }
                    });
            } 
});

frappe.ui.form.on("Vaccine", 
    {
		item: function(frm, cdt, cdn) 
            { 
                var d = locals[cdt][cdn];
                    frappe.call(
                    { 
                        method: "livestock.poultry.doctype.poultry_items.poultry_items.get_item_stock_uom",
                        args: { 
                            "item_code":d.item
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

frappe.ui.form.on("Medicine", 
    {
		item: function(frm, cdt, cdn) 
            { 
                var d = locals[cdt][cdn];
                    frappe.call(
                    { 
                        method: "livestock.poultry.doctype.poultry_items.poultry_items.get_item_stock_uom",
                        args: { 
                            "item_code":d.item
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