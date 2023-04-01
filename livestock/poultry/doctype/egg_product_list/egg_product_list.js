// Copyright (c) 2023, alantechnologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Egg Product list', {
	refresh: function(frm) {
		frm.set_query('item_code', function(doc, cdt, cdn) {
		  
			return {
			   "filters": {
			"item_group": "EGGS",
		}
			};
		});
	}
});
