// Copyright (c) 2023, alantechnologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Egg Packing', {
	 refresh: function(frm) 
	 {
		
		frm.set_query('item', function(doc, cdt, cdn) {
			return {
			   "filters": {
			"item_group": 'EGGS',
		}
			};
		});
		
		frm.set_query('bom', function(doc, cdt, cdn) {
			return {
			   "filters": {
			"Item": frm.doc.item,
		}
			};
		});
		
		frm.set_query('purchase_order', function(doc, cdt, cdn) {
			return {
			   "filters": {
			"company": frm.doc.company,
		}
			};
		});
	}
});
