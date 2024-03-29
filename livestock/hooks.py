from . import __version__ as app_version

app_name = "livestock"
app_title = "Livestock Management"
app_publisher = "alantechnologies"
app_description = "Livestock management"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "jayakumar@alantechnologies.net"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/livestock/css/livestock.css"
# app_include_js = "/assets/livestock/js/livestock.js"

# include js, css files in header of web template
# web_include_css = "/assets/livestock/css/livestock.css"
# web_include_js = "/assets/livestock/js/livestock.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "livestock/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "livestock.install.before_install"
# after_install = "livestock.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "livestock.uninstall.before_uninstall"
# after_uninstall = "livestock.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "livestock.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	'Project':'livestock.override.HatcheryProject',
	"Stock Entry": "livestock.overrides.stock_entry.CustomStockEntry",
 }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }  after_insert
doc_events = {
    "Stock Entry": {
		#"validate":"livestock.overrides.stock_entry.CustomStockEntry.validate",
        "on_submit": [
			"livestock.slaughtering.doctype.chicken_own_packing.own_packing_stock_entry.update_item_stat",
			"livestock.hatchery.doctype.hatchery_batch.hatchery_stock_entry.update_item_stat",
			"livestock.broiler.doctype.broiler_batch.broiler_stock_entry.update_item_stat",
			"livestock.hatchery.doctype.hatchery_batch.hatchery_batch.update_project_costing",
		],
		"on_trash": "livestock.broiler.doctype.broiler_batch.broiler_stock_entry.delete_item",
		"on_cancel": [
			"livestock.broiler.doctype.broiler_batch.broiler_stock_entry.cancel_item",
			"livestock.slaughtering.doctype.chicken_own_packing.own_packing_stock_entry.cancel_item",
			"livestock.hatchery.doctype.hatchery_batch.hatchery_batch.cancel_project_costing",
			"livestock.poultry.doctype.layer_batch.layer_batch.cancel_item"
		],
    },
	"Sales Invoice":{
		"on_submit":[
			"livestock.slaughtering.doctype.chicken_co_packing.sales_invoice.update_item_stat",
			"livestock.slaughtering.doctype.chicken_own_packing.own_packing_stock_entry.update_selling_cost",
			"livestock.poultry.doctype.layer_batch.layer_batch.sales_submit"
		],
		"on_cancel":[
			"livestock.slaughtering.doctype.chicken_own_packing.own_packing_stock_entry.cancel_selling_cost",
			"livestock.slaughtering.doctype.chicken_co_packing.sales_invoice.cancel_item",
			"livestock.poultry.doctype.layer_batch.layer_batch.sales_cancel"
		]
	}
}
# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"livestock.tasks.all"
# 	],
# 	"daily": [
# 		"livestock.tasks.daily"
# 	],
# 	"hourly": [
# 		"livestock.tasks.hourly"
# 	],
# 	"weekly": [
# 		"livestock.tasks.weekly"
# 	]
# 	"monthly": [
# 		"livestock.tasks.monthly"
# 	]
# }

# Testing
# -------
fixtures = [
    
    'Project Type',
	'strain',
	{
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                (                  
					"Project-own_packing_selling_cost",
					"Project-packing_cost",
					"Project-hatchery",
					"Project-total_transfer_amount",
					"Project-create_stock_entry",
					"Project-broiler_batch",
					"Project-hatchery_batch",
					"Project-cull_eggs",
					"Project-eggs_wt_gm",
					"Project-date_of_hatching",
					"Project-fertile_eggs",
					"Project-infertile_eggs",
					"Project-chicks_transfer_date",
					"Project-number_hatched",
					"Project-chicks_transferred",
					"Project-culls_no",
					"Project-shed_no",
					"Project-spoiled_fertility",
					"Project-av_chicks_wt",
					"Project-column_break_25",
					"Project-receiving_date",
					"Project-items",
					"Project-section_break_35",
					"Project-item_processed",
					"Project-number_set",
					"Project-number_received",
					"Project-setter_no",
					"Project-setting_date",
					"Project-supplier",
					"Project-strain",
					"Project-hatchery_details",
					"Sales Invoice-chicken_co_packing",
					"Sales Invoice-chicken_own_packing",
					"Sales Invoice Item-production_date",
					"Stock Entry-item_transfer",
					"Stock Entry-chicken_own_packing",
					"Stock Entry-purpose_of_issue",
					"Stock Entry-own_repack",
					"Stock Entry-manufacturing_type",
					"Stock Entry-stock_entry_type_option",
					"Stock Entry-total_items_qty"
                    
                ),
            ]
        ],
    },
	{ "doctype": "Report", "filters": [ ["name", "in", 
		( 
			"Broiler Consumables Usage",
			"Broiler Consumables Details",
			"Own Packing Material Report",
			"Broiler Consumables Usages",
		)
		
	] ] },
	{ "doctype": "Page", "filters": [ ["name", "in", ( 
		"broiler-dashbord",
		"broiler-production-a",
		"broiler-production-r",
		"store-wise-selling-r",
		"egg-production-repor",
		"poultry-dashbord",
		"daily-eggs-report",
		"daily-eggs-loading-a"
		)] ] },
	{ "doctype": "Client Script", "filters": [ ["name", "in", ( "Project-Form","Chicken Own Packing-Form","Chicken Co Packing-Form","Stock Entry-Form" )] ] },

]
# before_tests = "livestock.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "livestock.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "livestock.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"livestock.auth.validate"
# ]

