frappe.ui.form.on("Poultry Items", 
    { 
        item_code: function(frm, cdt, cdn) 
            { 
		var d = locals[cdt][cdn];
                
                frappe.call(
                    { 
                        method: "frappe.client.get_value",
                        args: { 
                            doctype: "Item Price", 
                            filters: {
                                item_code: d.item_code
                            },
                            fieldname:["price_list_rate","uom"]
                        },
                        callback: function(r) 
                            { 
                                if(r.message) 
                                    { 
                                        var item_price = r.message; 
					                    if(item_price.price_list_rate){
				                    	d.rate=item_price.price_list_rate;
				                    	d.uom=item_price.uom;
				                    	d.qty=1;
                                        frm.refresh_fields()
					                    }
                                    } 
                            }
                    });   
            } 
    }
);