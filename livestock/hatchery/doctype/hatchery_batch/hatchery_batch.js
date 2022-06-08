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
    refresh: function(frm) { 
        if (frm.doc.item_processed!=1)
        {       
          frm.add_custom_button(__('DOC Production Entry'), function(){
            
                 
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
        }).removeClass("btn-default").addClass("btn-success");
    }
      },
      number_received: function(frm, cdt, cdn) 
      { 
        frm.doc.number_set=frm.doc.number_received-frm.doc.cull_eggs;
        frm.refresh_fields();
      },
      cull_eggs: function(frm, cdt, cdn) 
      { 
        frm.doc.number_set=frm.doc.number_received-frm.doc.cull_eggs;
        frm.refresh_fields();
      },
      fertile_eggs: function(frm, cdt, cdn) 
      { 
        frm.doc.number_hatched=frm.doc.fertile_eggs-frm.doc.infertile_eggs-frm.doc.spoiled_fertility;
        frm.refresh_fields();
      },
      infertile_eggs: function(frm, cdt, cdn) 
      { 
        frm.doc.number_hatched=frm.doc.fertile_eggs-frm.doc.infertile_eggs-frm.doc.spoiled_fertility;
        frm.refresh_fields();
      },
      spoiled_fertility: function(frm, cdt, cdn) 
      { 
        frm.doc.number_hatched=frm.doc.fertile_eggs-frm.doc.infertile_eggs-frm.doc.spoiled_fertility;
        frm.refresh_fields();
      },
      number_hatched: function(frm, cdt, cdn) 
      { 
        frm.doc.chicks_transferred=frm.doc.number_hatched-frm.doc.culls_no;
        frm.refresh_fields();
      },
      culls_no: function(frm, cdt, cdn) 
      { 
        frm.doc.chicks_transferred=frm.doc.number_hatched-frm.doc.culls_no;
        frm.refresh_fields();
      }, 
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

