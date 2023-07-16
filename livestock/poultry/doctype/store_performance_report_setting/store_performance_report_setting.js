// Copyright (c) 2023, alantechnologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Store Performance Report Setting', {
	 refresh: function(frm) {
		frm.set_query('vehicle_maintenance', function(doc, cdt, cdn) {
			return {
			   	"filters": {
				"company": frm.doc.company,
				}
			};
		});

		frm.set_query('petty_cash_expenses', function(doc, cdt, cdn) {
			return {
			   	"filters": {
				"company": frm.doc.company,
				}
			};
		});

		frm.set_query('store', function(doc, cdt, cdn) {
			return {
			   	"filters": {
				"company": frm.doc.company,
				}
			};
		});

		frm.set_query('cost_center', function(doc, cdt, cdn) {
			return {
			   	"filters": {
				"company": frm.doc.company,
				}
			};
		});
	 }
});

