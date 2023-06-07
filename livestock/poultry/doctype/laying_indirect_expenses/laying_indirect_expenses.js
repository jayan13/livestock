// Copyright (c) 2023, alantechnologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Laying Indirect Expenses', {
	 refresh: function(frm) {
		frm.set_query('expense_accounts', function(doc, cdt, cdn) {
			return {
			   "filters": {
			"company": frm.doc.company,
		}
			};
		});
	 }
});
