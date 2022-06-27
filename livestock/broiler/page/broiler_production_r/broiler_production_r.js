frappe.pages['broiler-production-r'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Broiler Production Report',
		single_column: true
	});
}