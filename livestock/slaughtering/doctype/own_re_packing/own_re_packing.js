// Copyright (c) 2022, alantechnologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Own Re Packing', {
	 refresh: function(frm) {
		frm.add_custom_button(__('Re Pack'), function(){
        
			if(frm.doc.__unsaved){
				frappe.throw(__("Please save document before Create Stock Entry"));
				return false;
				}
				//$.each (frm.doc.re_packing_items, function(i, dt){
    
				//	dt.new_item='';
					
				//});
		//console.log(frm.doc);  
			frappe.call(
				{ 
					method: "livestock.slaughtering.doctype.chicken_own_packing.own_packing_stock_entry.re_stock_entry",
					args: { 
						//doc: d,
						own_re_packing:frm.doc.name
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
});


frappe.ui.form.on("Own Repacking Item", 
    {
		new_qty: function(frm, cdt, cdn) 
            { 
                var d = locals[cdt][cdn];

				if(d.new_qty>d.old_item_avail_qty)
				{
					d.new_qty=d.old_item_avail_qty;
				}
                    
            } 
});