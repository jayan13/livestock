
frappe.pages['broiler-dashbord'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}


var script = document.createElement("script");
script.src = '/assets/js/bootstrap-4-web.min.js';  // set its src to the provided URL
document.head.appendChild(script);

MyPage =Class.extend({
	
	init: function(wrapper){
			this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Broiler Dashbord',
			single_column: true
		});
			this.make();
	},
	make: function()
	{
		const comarry=[];
		
		
		
			let field = this.page.add_field({
			label: 'Company',
			fieldtype: 'Link',
			fieldname: 'company',
			options: 'Company',
			change() {
				load_batch();
				get_report();
			},
			default:'ABU DHABI MODERNE POULTRY FARM L.L.C.'
		});
		
		
		
		let field1 = this.page.add_field({
			label: 'Broiler Batch',
			fieldtype: 'Select',
			fieldname: 'batch',
			options: [],
			change() {
				get_report();
			}
		});

		
		this.page.add_inner_button('Print', () => print_rep());
		this.page.add_inner_button('Download', () => download_rep());
		let load_batch=function(){
			if(field.get_value()){
				$('[data-fieldname="batch"][type="text"]').empty();
				frappe.call({
					method: 'livestock.broiler.page.broiler_dashbord.broiler_dashbord.get_batch_list',
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
		}
		
/*
		
		var d = new Date();
		field2.set_value(new Date(d.getFullYear(),d.getMonth(),1));
		field3.set_value(frappe.datetime.get_today());
*/
		
		//this.page.add_inner_button('Get  Report', () => get_report());
		//this.page.add_inner_button('Print', () => print_rep());
		let data='';
		$(frappe.render_template("broiler_dashbord",data)).appendTo(this.page.main);

		//$("#exp_data").html("test");
		load_batch();
		
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
			
				title: "Expenses",
				type: 'pie', // or 'bar', 'line', 'pie', 'percentage'
				height: 500,
				colors: ['purple', '#ffa3ef', 'light-blue'],
			
				tooltipOptions: {
					formatTooltipX: d => (d + '').toUpperCase(),
					formatTooltipY: d => d +' '+frappe.boot.sysdefaults.currency,
				}
			  });
		}

		
		//chart_page();
		//var reqsnd=0
		var rear_xl=[];		
		var budget_xl=[];
		var reargp_xl=[];
		var reargp_mor_xl=[];
		var reargp_feed_xl=[];
		var reargp_weight_xl=[];
		var gp_frc_xl=[];
		function get_report()
		{
			//console.log('rs='+reqsnd);
			if(field.get_value() && field1.get_value())
			{ 
				//reqsnd=1;
				frappe.call({
					method: 'livestock.broiler.page.broiler_dashbord.broiler_dashbord.get_report',
					freeze: 1,
					freeze_message: 'Data loading ...please waite',
					args: {
					  company: field.get_value(),
					  batch: field1.get_value(),					  				  
					},
					callback: function (r) {
					  if (r.message) {
						//reqsnd=0;
						 $('#rer_exp').html(r.message.rear);
						 //$('#lay_exp').html(r.message.lay);
						 $('#budgets').html(r.message.budget);
						 $("#layer-chart").html('');
						 $("#rear-chart").html('');

						 reargp_xl=r.message.rear_graph
						 
						 let r_lbl=[]
						 let r_dta=[]
						
						$.each( r.message.rear_graph, function( key, value ) {					
							r_lbl.push(value.label);					  
							r_dta.push(value.data);					 
						});
						if(r_lbl.length){
							
							chart_rear(r_lbl,r_dta);
						}
						
						rearing_graph(field1.get_value());											
						rearing_weight_graph(field1.get_value());
						rearing_feed_graph(field1.get_value());
						fcr_graph(field1.get_value());
					  }
					},
				  }); 
			}
			
		}
		//---------------------------------------------------
		function download_rep()
		{
			budget_xl=get_table_data('#budgets tr');
			rear_xl=get_table_data('#rer_exp tr');
			
			frappe.call({
				method: "livestock.broiler.page.broiler_dashbord.broiler_dashbord.down_report",
				args: {
					company: field.get_value(),
					batch: field1.get_value(),					
					rearing:JSON.stringify(rear_xl),					
					budget:JSON.stringify(budget_xl),
					rearing_gp:JSON.stringify(reargp_xl),					
					rearing_mor_gp:JSON.stringify(reargp_mor_xl),					
					rearing_feed_gp:JSON.stringify(reargp_feed_xl),					
					rearing_weight_gp:JSON.stringify(reargp_weight_xl),					
					frc_gp:JSON.stringify(gp_frc_xl),
				},
				callback: function(response) {
				  var files = response.message;
				  //window.open("/api/method/livestock.poultry.page.poultry_dashbord.poultry_dashbord.down_file");
				  let url='/api/method/livestock.broiler.page.broiler_dashbord.broiler_dashbord.down_file';
				  open_url_post(url, {file: files}); 
				}
			  }); 

			  
		}
		//--------------------------------------------------------
		
		function get_table_data(id)
		{
			const trs = document.querySelectorAll(id);

			const result = [];
			
			for(let tr of trs) {
				let th_array=[];
				let td_array=[];
				let th_td_array=[];
				let th = tr.getElementsByTagName('th');
				if (th.length > 0) {
					th_array = Array.from(th);
					th_array = th_array.map(tag => tag.innerText);
					
				}

				let td = tr.getElementsByTagName('td');
				if (td.length > 0) {
					td_array = Array.from(td);
					td_array = td_array.map(tag => tag.innerText);
					
				}
				
				th_td_array = th_td_array.concat(th_array,td_array); // get the text of each element
				result.push(th_td_array);
			}
			return result;
		}

function rearing_graph(batch)
{
	$("#rear-mortality").html('');
	frappe.call({
		method: 'livestock.broiler.page.broiler_dashbord.broiler_dashbord.get_rear_mor_graph',
		//freeze: 1,
		//freeze_message: 'Data loading ...please waite',
		args: {
		  batch: batch,		  
		},
		callback: function (r) {
		  if (r.message) {
			reargp_mor_xl=r.message.ideal
			if(reargp_mor_xl.length){
			let l_lbl=[]
			let l_dta=[]
			let act_dta=[]			 
			$.each( r.message.ideal, function( key, value ) {					
				l_lbl.push(value.age);
				l_dta.push(value.mortality);
				act_dta.push(value.act_mortality);
				});

				
			 //--------------------------------------------------
			 let chart = new frappe.Chart( "#rear-mortality", { 
				 // or DOM element ref: https://frappe.io/charts
				data: {
					labels: l_lbl,
				
					datasets: [
						{							
							chartType: 'line',
							name: "Std.",
							values: l_dta
						},
						{							
							chartType: 'line',
							name: "Actual",
							values: act_dta
						},
						
					],
				},
				title: "Mortality",
				type: 'line', // or 'bar', 'line', 'pie', 'percentage' #2490ef
				height: 300,				
				colors: ['#ff2e2e','#2490ef'],
				axisOptions: {					
					yLabel: "Value", // Label for y-axis					
				  },
				  tooltipOptions: {
					formatTooltipX: d => d + ' Days',
					formatTooltipY: d => ' Mor. Cum. '+d+' %',
				}
				
			  });

			 //--------------------------------------------------
			}
		  }
		},
	  }); 
}

function rearing_feed_graph(batch)
{
	
	$("#rear-feed").html('');
	frappe.call({
		method: 'livestock.broiler.page.broiler_dashbord.broiler_dashbord.get_rear_feed_graph',
		//freeze: 1,
		//freeze_message: 'Data loading ...please waite',
		args: {
			batch: batch,  
		  },
		callback: function (r) {
		  if (r.message) {
			reargp_feed_xl=r.message.ideal

			if(reargp_feed_xl.length){

			let ly_lbl=[]
			let ly_dta=[]
			let lyact_dta=[]
						 
			$.each( r.message.ideal, function( key, value ) {					
				ly_lbl.push(value.age);
				ly_dta.push(value.feed);				
				lyact_dta.push(value.act_feed);
				});
				
				//console.log(ly_lbl);
			 //--------------------------------------------------
			 let chart = new frappe.Chart( "#rear-feed", { 
				 // or DOM element ref: https://frappe.io/charts
				 data: {
					labels: ly_lbl,
				
					datasets: [
						{
							chartType: 'line',
							name: "Feed Intake",
							values: ly_dta
						},
						{							
							chartType: 'line',
							name: "Actual Feed Intake",
							values: lyact_dta
						},
						
					],
				},
				title: "Feed",
				type: 'line', // or 'bar', 'line', 'pie', 'percentage'
				height: 300,				
				colors: ['#ff2e2e','#55af46','#2490ef'],
				axisOptions: {					
					yLabel: "Value", // Label for y-axis
					
				  },
				  tooltipOptions: {
					formatTooltipX: d => d + ' Days',
					formatTooltipY: d => ' Feed '+d+' gm',
				}
				
			  });

			 //--------------------------------------------------
			}
		  }
		},
	  });
}

function rearing_weight_graph(batch)
{
	
	$("#rear-weight").html('');
	frappe.call({
		method: 'livestock.broiler.page.broiler_dashbord.broiler_dashbord.get_rear_weight_graph',
		//freeze: 1,
		//freeze_message: 'Data loading ...please waite',
		args: {
			batch: batch, 
		  },
		callback: function (r) {
		  if (r.message) {
			reargp_weight_xl=r.message.ideal

			if(reargp_weight_xl.length){

			let ly_lbl=[]
			let ly_dta=[]
			let lyact_dta=[]
						 
			$.each( r.message.ideal, function( key, value ) {					
				ly_lbl.push(value.age);
				ly_dta.push(value.weight);
				lyact_dta.push(value.act_weight);
				});
				
				//console.log(ly_lbl);
			 //--------------------------------------------------
			 let chart = new frappe.Chart( "#rear-weight", { 
				 // or DOM element ref: https://frappe.io/charts
				 data: {
					labels: ly_lbl,
				
					datasets: [
						{
							chartType: 'line',
							name: "Std. Weight",
							values: ly_dta
						},						
						{							
							chartType: 'line',
							name: "Actual Weight",
							values: lyact_dta
						},
						
					],
				},
				title: "Weight",
				type: 'line', // or 'bar', 'line', 'pie', 'percentage'
				height: 300,				
				colors: ['#ff2e2e','#55af46','#2490ef'],
				axisOptions: {					
					yLabel: "Value", // Label for y-axis
					
				  },
				  tooltipOptions: {
					formatTooltipX: d => d + ' days',
					formatTooltipY: d => ' Weight '+d+' gm',
				}
				
			  });

			 //--------------------------------------------------
			}
		  }
		},
	  });
}
//layer-performance
function fcr_graph(batch)
{
	
	$("#layer-performance").html('');
	frappe.call({
		method: 'livestock.broiler.page.broiler_dashbord.broiler_dashbord.get_frc_graph',
		//freeze: 1,
		//freeze_message: 'Data loading ...please waite',
		args: {
			batch: batch, 
		  },
		callback: function (r) {
		  if (r.message) {
			gp_frc_xl=r.message.ideal

			if(gp_frc_xl.length){

			let ly_lbl=[]
			let ly_dta=[]
			let lyact_dta=[]
						 
			$.each( r.message.ideal, function( key, value ) {					
				ly_lbl.push(value.age);
				ly_dta.push(value.fcr);
				lyact_dta.push(value.act_fcr);
				});
				
				//console.log(ly_lbl);
			 //--------------------------------------------------
			 let chart = new frappe.Chart( "#layer-performance", { 
				 // or DOM element ref: https://frappe.io/charts
				 data: {
					labels: ly_lbl,
				
					datasets: [
						{
							chartType: 'line',
							name: "Std. FCR",
							values: ly_dta
						},						
						{							
							chartType: 'line',
							name: "Actual FCR",
							values: lyact_dta
						},
						
					],
				},
				title: "FCR",
				type: 'line', // or 'bar', 'line', 'pie', 'percentage'
				height: 300,				
				colors: ['#ff2e2e','#55af46','#2490ef'],
				axisOptions: {					
					yLabel: "Value", // Label for y-axis
					
				  },
				  tooltipOptions: {
					formatTooltipX: d => d + ' days',
					formatTooltipY: d => ' FCR '+d,
				}
				
			  });

			 //--------------------------------------------------
			}
		  }
		},
	  });
}
//-----------------------------------------------------------------------------
		
	}
})

function print_rep()
				{
					
					var divrear=document.getElementById('rearing');					
					var divbud=document.getElementById('budget');
					var divmorgp=document.getElementById('mortality');
					  var newWin=window.open('','Print-Window');
					  newWin.document.open();
					  newWin.document.write('<html><style>table, th, td {border: 1px solid;border-collapse: collapse; } table{ width:100%;} table td{ text-align:right;} #rear-chart{display:none;}#layer-chart{display:none;} .table-secondary td,.table-secondary th {background-color: #d5d7d9;font-weight: bold;}  @media print { #prod{overflow-x:unset !important;} #rer{overflow-x:unset !important;} } </style><body onload="window.print()">'+divbud.innerHTML+divrear.innerHTML+divmorgp.innerHTML+'</body></html>');
					  newWin.document.close();
					  setTimeout(function(){newWin.close();},10);
		  
				}