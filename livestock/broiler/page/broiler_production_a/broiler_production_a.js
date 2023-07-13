
frappe.pages['broiler-production-a'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}

MyPage =Class.extend({
	
	init: function(wrapper){
			this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Broiler Production & Sales Monthly Comparison Report',
			single_column: true
		});
			this.make();
	},
	make: function()
	{
		const comarry=[];
		var date = new Date();
		var lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0);
		var firstDay = new Date(date.getFullYear(), date.getMonth()-2, 1);
			let field = this.page.add_field({
			label: 'Company',
			fieldtype: 'Link',
			fieldname: 'company',
			options: 'Company',
			change() {
				get_report();
			},
			default:'ABU DHABI MODERNE POULTRY FARM L.L.C.'
		});
		
		let field1 = this.page.add_field({
			label: 'Date',
			fieldtype: 'Date',
			fieldname: 'date_from',
			change() {
				
				get_report();
				
			}
		});

		let field2 = this.page.add_field({
			label: 'Date',
			fieldtype: 'Date',
			fieldname: 'date_to',
			change() {
				
				get_report();
				
			}
		});
		
		field1.set_value(firstDay);
		field2.set_value(lastDay);		
		
		this.page.add_inner_button('Print', () => print_rep());
		let data='';
		$(frappe.render_template("broiler_production_a",data)).appendTo(this.page.main);
		
		function get_report()
		{
			$('#broiler').html('');
			if(field.get_value())
			{		
					frappe.call({
					method: 'livestock.broiler.page.broiler_production_a.broiler_production_a.get_report',
					freeze: 1,
					freeze_message: 'Data loading ...please waite',
					args: {
					  company: field.get_value(),
					  date_from: field1.get_value(),
					  date_to: field2.get_value(),
					},
					callback: function (r) {
					  if (r.message) {
						  $('#broiler').html(r.message);
							
							
					  }
					},
				  });
	  
			}
		}
		
		
		
	}


})

function print_rep()
		{

			  var divrear=document.getElementById('broiler');
					
					  var newWin=window.open('','Print-Window');
					  newWin.document.open();
					  newWin.document.write('<html><style>table, th, td {border: 1px solid;border-collapse: collapse; } table{ width:100%;} table td{ text-align:right;} table td:first-child{ text-align:left;} .table-secondary td,.table-secondary th {background-color: #d5d7d9;font-weight: bold;} #rephd{ font-size: 18px; font-weight: bold; padding: 15px;}  @media print { #prod{overflow-x:unset !important;} #rer{overflow-x:unset !important;} } </style><body onload="window.print()">'+divrear.innerHTML+'</body></html>');
					  newWin.document.close();
					  setTimeout(function(){newWin.close();},10);
  
		}