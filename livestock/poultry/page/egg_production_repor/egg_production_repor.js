

frappe.pages['egg-production-repor'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}

MyPage =Class.extend({
	
	init: function(wrapper){
			this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Egg Production & Sales Monthly Comparison Report',
			single_column: true
		});
			this.make();
	},
	make: function()
	{
		const comarry=[];
		
		
		
			let field = this.page.add_field({
			label: 'Company',
			fieldtype: 'Select',
			fieldname: 'company',
			options: [],
			change() {
				get_report();
			}
		});
		
		frappe.call({
          method: 'livestock.poultry.page.egg_production_repor.egg_production_repor.get_company_list',
          args: {},
          callback: function (r) {
            if (r.message) {
				$('[data-fieldname="company"][type="text"]').append($("<option></option>").attr("value", "").text("")); 
				$.each( r.message.companys, function( key, value ) {					
					
					$('[data-fieldname="company"][type="text"]').append($("<option></option>").attr("value", value.name).text(value.name)); 
				}); 
				
            }
          },
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
		fdate=frappe.datetime.add_months(frappe.datetime.get_today(), -2);
		field1.set_value(fdate);
		field2.set_value(frappe.datetime.get_today());		
		//this.page.add_inner_button('Get  Report', () => get_report());
		this.page.add_inner_button('Print', () => print_rep());
		let data='';
		$(frappe.render_template("egg_production_repor",data)).appendTo(this.page.main);
		
		function get_report()
		{
			$('#report_egg').html('');
			if(field.get_value())
			{		
					frappe.call({
					method: 'livestock.poultry.page.egg_production_repor.egg_production_repor.get_report',
					freeze: 1,
					freeze_message: 'Data loading ...please waite',
					args: {
					  company: field.get_value(),
					  date_from: field1.get_value(),
					  date_to: field2.get_value(),
					},
					callback: function (r) {
					  if (r.message) {
						  $('#report_egg').html(r.message);
							
							
					  }
					},
				  });
	  
			}
		}
		
		
		
	}


})

function print_rep()
		{

			  var divrear=document.getElementById('report_egg');
					
					  var newWin=window.open('','Print-Window');
					  newWin.document.open();
					  newWin.document.write('<html><style>table, th, td {border: 1px solid;border-collapse: collapse; } table{ width:100%;} table td{ text-align:right;} table td:first-child{ text-align:left;} .table-secondary td,.table-secondary th {background-color: #d5d7d9;font-weight: bold;} #rephd{ font-size: 18px; font-weight: bold; padding: 15px;}  @media print { #prod{overflow-x:unset !important;} #rer{overflow-x:unset !important;} } </style><body onload="window.print()">'+divrear.innerHTML+'</body></html>');
					  newWin.document.close();
					  setTimeout(function(){newWin.close();},10);
  
		}