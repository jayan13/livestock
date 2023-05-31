
frappe.pages['poultry-dashbord'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}


var script = document.createElement("script");
script.src = '/assets/js/bootstrap-4-web.min.js';  // set its src to the provided URL
document.head.appendChild(script);

MyPage =Class.extend({
	
	init: function(wrapper){
			this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Layer Poultry Dashbord',
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
				load_batch();
				get_report();
			}
		});
		
		frappe.call({
          method: 'livestock.poultry.page.poultry_dashbord.poultry_dashbord.get_company_list',
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
			label: 'Layer Batch',
			fieldtype: 'Select',
			fieldname: 'batch',
			options: [],
			change() {
				get_report();
			}
		});

		let field2 = this.page.add_field({
			label: 'Period based On',
			fieldtype: 'Select',
			fieldname: 'period',
			options: ['','Accounting Period','Start Date Of Project'],
			change() {
				get_report();
			},
			default:'Start Date Of Project'
		});
		this.page.add_inner_button('Print', () => print_rep());
		this.page.add_inner_button('Download', () => download_rep());
		let load_batch=function(){
			$('[data-fieldname="batch"][type="text"]').empty();
			frappe.call({
				method: 'livestock.poultry.page.poultry_dashbord.poultry_dashbord.get_batch_list',
				args: {company: field.get_value(),},
				callback: function (r) {
					
				  if (r.message) {
					  $('[data-fieldname="batch"][type="text"]').append($("<option></option>").attr("value", "").text("")); 
					  $.each( r.message.batchs, function( key, value ) {					
						  
						  $('[data-fieldname="batch"][type="text"]').append($("<option></option>").attr("value", value.name).text(value.name)); 
					  }); 
					  
				  }
				},
			  });
		}
		
/*
		
		var d = new Date();
		field2.set_value(new Date(d.getFullYear(),d.getMonth(),1));
		field3.set_value(frappe.datetime.get_today());
*/
		
		
		//this.page.add_inner_button('Get  Report', () => get_report());
		//this.page.add_inner_button('Print', () => print_rep());
		let data='';
		$(frappe.render_template("poultry_dashbord",data)).appendTo(this.page.main);

		//$("#exp_data").html("test");
		
		$('#myTab a').on('click', function (e) {
			
			e.preventDefault();
			$(this).tab('show');
			return false;
		  })
		

		let chart_rear =function(lbl,val){
			//console.log(lbl);
			let chart = new frappe.Chart( "#rear-chart", { // or DOM element ref: https://frappe.io/charts
				data: {
				labels: lbl,
				datasets: [
					{
						name: "Some Data", chartType: 'pie',
						values: val
					},
					
				],
			
				/*yMarkers: [{ label: "Marker", value: 70,
					options: { labelPos: 'left' }}],
				yRegions: [{ label: "Region", start: -10, end: 50,
					options: { labelPos: 'right' }}]*/
				},
			
				title: "Rearing",
				type: 'pie', // or 'bar', 'line', 'pie', 'percentage'
				height: 300,
				colors: ['purple', '#ffa3ef', 'light-blue'],
			
				tooltipOptions: {
					formatTooltipX: d => (d + '').toUpperCase(),
					formatTooltipY: d => d + ' Dhr',
				}
			  });
		}

		let chart_layer =function(lbl,val){

			let chart = new frappe.Chart( "#layer-chart", { // or DOM element ref: https://frappe.io/charts
				data: {
				labels: lbl,
			
				datasets: [
					{
						name: "Some Data", chartType: 'pie',
						values: val
					},
					
				],
			
				/*yMarkers: [{ label: "Marker", value: 70,
					options: { labelPos: 'left' }}],
				yRegions: [{ label: "Region", start: -10, end: 50,
					options: { labelPos: 'right' }}]*/
				},
			
				title: "Laying",
				type: 'pie', // or 'bar', 'line', 'pie', 'percentage'
				height: 300,
				colors: ['purple', '#ffa3ef', 'light-blue'],
			
				tooltipOptions: {
					formatTooltipX: d => (d + '').toUpperCase(),
					formatTooltipY: d => d + ' Dhr',
				}
			  });
		}
		//chart_page();
		//var reqsnd=0
		var rear_xl=[];
		var lay_xl=[];
		function get_report()
		{
			//console.log('rs='+reqsnd);
			if(field.get_value() && field1.get_value())
			{ 
				//reqsnd=1;
				frappe.call({
					method: 'livestock.poultry.page.poultry_dashbord.poultry_dashbord.get_report',
					freeze: 1,
					freeze_message: 'Data loading ...please waite',
					args: {
					  company: field.get_value(),
					  batch: field1.get_value(),
					  period: field2.get_value(),					  
					},
					callback: function (r) {
					  if (r.message) {
						//reqsnd=0;
						 $('#rer_exp').html(r.message.rear);
						 $('#lay_exp').html(r.message.lay);
						 $('#budgets').html(r.message.budget);
						 rear_xl=r.message.rear_xl
						 lay_xl=r.message.lay_xl
						 let l_lbl=[]
						 let l_dta=[]
						 let r_lbl=[]
						 let r_dta=[]
						 $.each( r.message.lay_graph, function( key, value ) {					
							l_lbl.push(value.label);
							l_dta.push(value.data);
						});
						
						$.each( r.message.rear_graph, function( key, value ) {					
							r_lbl.push(value.label);					  
							r_dta.push(value.data);					 
						});
						if(l_lbl.length)
						{
							chart_layer(l_lbl,l_dta);
						}
						if(r_lbl.length){
							
							chart_rear(r_lbl,r_dta);
						}
						
							//let data2=r.message;
							
							//$(frappe.render_template("daily_eggs_report_data",data2)).appendTo("#report_egg");
					  }
					},
				  }); 
			}
			
		}
		//---------------------------------------------------
		function download_rep()
		{
			
			frappe.call({
				method: "livestock.poultry.page.poultry_dashbord.poultry_dashbord.down_report",
				args: {
					company: field.get_value(),
					batch: field1.get_value(),
					period: field2.get_value(),
					rearing:JSON.stringify(rear_xl),
					laying:JSON.stringify(lay_xl)	
				},
				callback: function(response) {
				  var files = response.message;
				  //window.open("/api/method/livestock.poultry.page.poultry_dashbord.poultry_dashbord.down_file");
				  let url='/api/method/livestock.poultry.page.poultry_dashbord.poultry_dashbord.down_file';
				  open_url_post(url, {file: files}); 
				}
			  }); 

			  
		}
		//--------------------------------------------------------
		
	}
})

function print_rep()
				{
					
					var divrear=document.getElementById('rearing');
					var divlay=document.getElementById('production');
					
					  var newWin=window.open('','Print-Window');
					  newWin.document.open();
					  newWin.document.write('<html><style>table, th, td {border: 1px solid;border-collapse: collapse; } table{ width:100%;} table td{ text-align:right;} #rear-chart{display:none;}#layer-chart{display:none;}  @media print { #prod{overflow-x:unset !important;} #rer{overflow-x:unset !important;} } </style><body onload="window.print()">'+divrear.innerHTML+divlay.innerHTML+'</body></html>');
					  newWin.document.close();
					  setTimeout(function(){newWin.close();},10);
		  
				}

