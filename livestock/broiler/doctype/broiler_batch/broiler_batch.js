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
                        
                        frappe.prompt(
                            [
                            {  fieldtype: "Int",
                                label: __("Transfer Quantity"),
                                fieldname: "transfer_qty",
                                reqd:'1'                                
                            },{  fieldtype: "Date",
                            label: __("Transfer Date"),
                            fieldname: "transfer_date",
                            reqd:'1'                                
                            }
                            ,{  fieldtype: "Link",
                            label: __("Transfer Warehouse"),
                            fieldname: "transfer_warehouse",
                            options:"Warehouse"                                
                        }],
                            function(data) {
                                
                                frappe.call(
                                    { 
                                        method: "livestock.broiler.doctype.broiler_batch.broiler_stock_entry.stock_entry",
                                        args: {
                                            batch:frm.doc.name,
                                            transfer_qty:data.transfer_qty,
                                            transfer_date:data.transfer_date,
                                            transfer_warehouse:data.transfer_warehouse
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
                            },
                            __("Finish Item Transfer"),
                            __("Confirm")
                        );       
                //console.log(frm.doc);  
                    
               
                    }).removeClass("btn-default").addClass("btn-success");
			}
            
	},
    mortality:function(frm, cdt, cdn) 
    { 
        var d = locals[cdt][cdn];
        frm.doc.doc_placed=frm.doc.number_received-frm.doc.mortality;
        var totom=0
            $.each (frm.doc.daily_mortality, function(i, dt){
    
                totom+=dt.total;
                
            });
        frm.doc.current_alive_chicks=frm.doc.doc_placed-totom-frm.doc.chick_transferred
        frm.refresh_fields()
    },
    number_received:function(frm, cdt, cdn) 
    {
        var d = locals[cdt][cdn];
        frm.doc.doc_placed=frm.doc.number_received-frm.doc.mortality;
        var totom=0
            $.each (frm.doc.daily_mortality, function(i, dt){
    
                totom+=dt.total;
                
            });
        frm.doc.current_alive_chicks=frm.doc.doc_placed-totom-frm.doc.chick_transferred
        frm.refresh_fields()
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

frappe.ui.form.on("Mortality", 
    {
        evening:function(frm, cdt, cdn) 
        { 
            var d = locals[cdt][cdn];
            d.total=d.evening+d.morning
            var totom=0
            $.each (frm.doc.daily_mortality, function(i, dt){
    
                totom+=dt.total;
                
            });

            frm.doc.total_mortaliy=totom
            frm.doc.current_alive_chicks=frm.doc.number_received-totom-frm.doc.mortality-frm.doc.chick_transferred
            frm.refresh_fields() 
        },
        morning:function(frm, cdt, cdn) 
        { 
            var d = locals[cdt][cdn]; 
            d.total=d.evening+d.morning
            
            var totom=0
            $.each (frm.doc.daily_mortality, function(i, dt){
    
                totom+=dt.total;
                
            });

            frm.doc.total_mortaliy=totom
            frm.doc.current_alive_chicks=frm.doc.number_received-totom-frm.doc.mortality-frm.doc.chick_transferred
            frm.refresh_fields()
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

