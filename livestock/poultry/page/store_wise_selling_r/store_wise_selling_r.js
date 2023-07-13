

frappe.pages['store-wise-selling-r'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}

MyPage =Class.extend({
	
	init: function(wrapper){
			this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Store Performance Report',
			single_column: true
		});
			this.make();
	},
	make: function()
	{
		
			let field = this.page.add_field({
			label: 'Company',
			fieldtype: 'Link',
			fieldname: 'company',
			options: 'Company',
			change() {
				get_report();
			},
			default:'ABU DHABI POULTRY FARM - SOLE PROPRIETORSHIP L.L.C.'
		});
		
		let field1 = this.page.add_field({
			label: 'Store',
			fieldtype: 'Link',
			fieldname: 'warehouse',
			options: 'Warehouse',
			change() {
				
				get_report();
				
			},
			get_query: function() {
				return {
					'doctype': 'Warehouse',
					'filters': {
						'warehouse_type': 'Store',
						'company': field.get_value()
					}
				};
			}
		});

		
		
		this.page.add_inner_button('Print', () => print_rep());
		let data='';
		$(frappe.render_template("store_wise_selling_r",data)).appendTo(this.page.main);
		
		function get_report()
		{
			$('#store').html('');
			if(field.get_value())
			{		
					frappe.call({
					method: 'livestock.poultry.page.store_wise_selling_r.store_wise_selling_r.get_report',
					freeze: 1,
					freeze_message: 'Data loading ...please waite',
					args: {
					  company: field.get_value(),
					  store: field1.get_value(),					  
					},
					callback: function (r) {
					  if (r.message) {
						  $('#store').html(r.message);
							
							
					  }
					},
				  });
	  
			}
		}
		
		
		
	}


})

function print_rep()
		{

			  var divrear=document.getElementById('store');
					
					  var newWin=window.open('','Print-Window');
					  newWin.document.open();
					  newWin.document.write('<html><style>table, th, td {border: 1px solid;border-collapse: collapse; } table{ width:100%;} table td{ text-align:right;} table td:first-child{ text-align:left;} .table-secondary td,.table-secondary th {background-color: #d5d7d9;font-weight: bold;} #rephd{ font-size: 18px; font-weight: bold; padding: 15px;}  @media print { #prod{overflow-x:unset !important;} #rer{overflow-x:unset !important;} } </style><body onload="window.print()">'+divrear.innerHTML+'</body></html>');
					  newWin.document.close();
					  setTimeout(function(){newWin.close();},10);
  
		}