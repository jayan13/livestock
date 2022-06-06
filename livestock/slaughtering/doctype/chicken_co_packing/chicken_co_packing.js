// Copyright (c) 2022, alantechnologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Chicken Co Packing', {
    refresh: function(frm) { 
        if (frm.doc.item_processed!=1)
        {       
            frm.add_custom_button(__('Create Sales Invoice'), function(){
        
                if(frm.doc.__unsaved){
					frappe.throw(__("Please save document before generate sales invoice"));
					return false;
					}
					
					
			//console.log(frm.doc);  
				frappe.call(
                    { 
                        method: "livestock.slaughtering.doctype.chicken_co_packing.sales_invoice.sales_invoice",
                        args: { 
                            //doc: d,
                            co_packing:frm.doc.name
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
           
            });
        }
        },
    chicken_net_of_mortality: function(frm) {
    if(frm.doc.total_live_weight_in_kg && frm.doc.chicken_net_of_mortality )
    {
        
            frm.doc.avg_live_weight_per_cheicken = flt(frm.doc.total_live_weight_in_kg/frm.doc.chicken_net_of_mortality,2);
            frm.refresh_fields();
           
    }
},
total_live_weight_in_kg: function(frm) {
    if(frm.doc.total_live_weight_in_kg && frm.doc.chicken_net_of_mortality )
    {
        
            frm.doc.avg_live_weight_per_cheicken = flt(frm.doc.total_live_weight_in_kg/frm.doc.chicken_net_of_mortality,2);
            frm.refresh_fields();
           
    }
},
	create_sales_invoice: function(frm, cdt, cdn) 
            { 
                 var d = locals[cdt][cdn];
                 
                
                if(frm.doc.__unsaved){
					frappe.throw(__("Please save document before generate sales invoice"));
					return false;
					}
					
					
			//console.log(frm.doc);  
				frappe.call(
                    { 
                        method: "livestock.slaughtering.doctype.chicken_co_packing.sales_invoice.sales_invoice",
                        args: { 
                            //doc: d,
                            co_packing:frm.doc.name
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
})

frappe.ui.form.on("Co Packing List", 
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
    }
);