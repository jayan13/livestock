
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
			default:'Accounting Period'
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
				height: 500,
				colors: ['purple', '#ffa3ef', 'light-blue'],
			
				tooltipOptions: {
					formatTooltipX: d => (d + '').toUpperCase(),
					formatTooltipY: d => d +' '+frappe.boot.sysdefaults.currency,
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
				height: 500,				
				colors: ['purple', '#ffa3ef', 'light-blue'],
			
				tooltipOptions: {
					formatTooltipX: d => (d + '').toUpperCase(),
					formatTooltipY: d => d +' '+ frappe.boot.sysdefaults.currency,
				}
			  });
		}
		//chart_page();
		//var reqsnd=0
		var rear_xl=[];
		var lay_xl=[];
		var budget_xl=[];
		var reargp_xl=[];
		var laygp_xl=[];
		var reargp_mor_xl=[];
		var laygp_mor_xl=[];
		var reargp_feed_xl=[];
		var laygp_feed_xl=[];
		var reargp_weight_xl=[];
		var laygp_weight_xl=[];
		var laygp_performance_xl=[];
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
						 $("#layer-chart").html('');
						 $("#rear-chart").html('');

						 reargp_xl=r.message.rear_graph
						 laygp_xl=r.message.lay_graph
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
						rearing_graph(field1.get_value(),field2.get_value());
						laying_graph(field1.get_value(),field2.get_value());
						laying_weight_graph(field1.get_value(),field2.get_value());
						laying_feed_graph(field1.get_value(),field2.get_value());
						rearing_weight_graph(field1.get_value(),field2.get_value());
						rearing_feed_graph(field1.get_value(),field2.get_value());
						laying_performance_graph(field1.get_value(),field2.get_value());
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
			budget_xl=get_table_data('#budgets tr');
			rear_xl=get_table_data('#rer_exp tr');
			lay_xl=get_table_data('#lay_exp tr');
			frappe.call({
				method: "livestock.poultry.page.poultry_dashbord.poultry_dashbord.down_report",
				args: {
					company: field.get_value(),
					batch: field1.get_value(),					
					rearing:JSON.stringify(rear_xl),
					laying:JSON.stringify(lay_xl),
					budget:JSON.stringify(budget_xl),
					rearing_gp:JSON.stringify(reargp_xl),
					laying_gp:JSON.stringify(laygp_xl),
					rearing_mor_gp:JSON.stringify(reargp_mor_xl),
					laying_mor_gp:JSON.stringify(laygp_mor_xl),
					rearing_feed_gp:JSON.stringify(reargp_feed_xl),
					laying_feed_gp:JSON.stringify(laygp_feed_xl),
					rearing_weight_gp:JSON.stringify(reargp_weight_xl),
					laying_weight_gp:JSON.stringify(laygp_weight_xl),
					laying_performance_gp:JSON.stringify(laygp_performance_xl),

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

		function rearing_graph(batch,period)
{
	$("#rear-mortality").html('');
	frappe.call({
		method: 'livestock.poultry.page.poultry_dashbord.poultry_dashbord.get_rear_mor_graph',
		//freeze: 1,
		//freeze_message: 'Data loading ...please waite',
		args: {
		  batch: batch,
		  period: period,					  
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
				title: "Rearing Mortality",
				type: 'line', // or 'bar', 'line', 'pie', 'percentage' #2490ef
				height: 300,				
				colors: ['#ff2e2e','#2490ef'],
				axisOptions: {					
					yLabel: "Value", // Label for y-axis					
				  },
				  tooltipOptions: {
					formatTooltipX: d => d + ' Week',
					formatTooltipY: d => ' Mor. Cum. '+d+' %',
				}
				
			  });

			 //--------------------------------------------------
			}
		  }
		},
	  }); 
}

function laying_graph(batch,period)
{
	
	$("#layer-mortality").html('');
	frappe.call({
		method: 'livestock.poultry.page.poultry_dashbord.poultry_dashbord.get_lay_mor_graph',
		//freeze: 1,
		//freeze_message: 'Data loading ...please waite',
		args: {
			batch: batch,
			period: period,					  
		  },
		callback: function (r) {
		  if (r.message) {
			laygp_mor_xl=r.message.ideal

			if(laygp_mor_xl.length){

			let ly_lbl=[]
			let ly_dta=[]
			let lyact_dta=[]
			let ly_lbl2=[]
			let ly_dta2=[]
			let lyact_dta2=[]
			let cnt=0			 
			$.each( r.message.ideal, function( key, value ) {
				if(cnt< 43) {
					ly_lbl.push(value.age);
					ly_dta.push(value.mortality);
					lyact_dta.push(value.act_mortality);
				}else{
					ly_lbl2.push(value.age);
					ly_dta2.push(value.mortality);
					lyact_dta2.push(value.act_mortality);
				} 					
				
				cnt++;
				});
				
				//console.log(ly_lbl);
			 //--------------------------------------------------
			 let chart = new frappe.Chart( "#layer-mortality", { 
				 // or DOM element ref: https://frappe.io/charts
				 data: {
					labels: ly_lbl,
				
					datasets: [
						{
							chartType: 'line',
							name: "Std.",
							values: ly_dta
						},
						{							
							chartType: 'line',
							name: "Actual",
							values: lyact_dta
						},
						
					],
				},
				title: "Laying Mortality",
				type: 'line', // or 'bar', 'line', 'pie', 'percentage'
				height: 300,				
				colors: ['#ff2e2e','#2490ef'],
				axisOptions: {					
					yLabel: "Value", // Label for y-axis
					
				  },
				  tooltipOptions: {
					formatTooltipX: d => d + ' Week',
					formatTooltipY: d => ' Mor. Cum. '+d+' %',
				}
				
			  });

			  let chart2 = new frappe.Chart( "#layer-mortality2", { 
				// or DOM element ref: https://frappe.io/charts
				data: {
				   labels: ly_lbl2,
			   
				   datasets: [
					   {
						   chartType: 'line',
						   name: "Std.",
						   values: ly_dta2
					   },
					   {							
						   chartType: 'line',
						   name: "Actual",
						   values: lyact_dta2
					   },
					   
				   ],
			   },
			   title: "Laying Mortality",
			   type: 'line', // or 'bar', 'line', 'pie', 'percentage'
			   height: 300,				
			   colors: ['#ff2e2e','#2490ef'],
			   axisOptions: {					
				   yLabel: "Value", // Label for y-axis
				   
				 },
				 tooltipOptions: {
				   formatTooltipX: d => d + ' Week',
				   formatTooltipY: d => ' Mor. Cum. '+d+' %',
			   }
			   
			 });

			 //--------------------------------------------------
			}
		  }
		},
	  });
}
//-------------------------------------------------------------------------
function laying_feed_graph(batch,period)
{
	
	$("#layer-feed").html('');
	frappe.call({
		method: 'livestock.poultry.page.poultry_dashbord.poultry_dashbord.get_lay_feed_graph',
		//freeze: 1,
		//freeze_message: 'Data loading ...please waite',
		args: {
			batch: batch,
			period: period,					  
		  },
		callback: function (r) {
		  if (r.message) {
			laygp_feed_xl=r.message.ideal

			if(laygp_feed_xl.length){

			let ly_lbl=[]
			let ly_dta1=[]
			let ly_dta2=[]
			let lyact_dta=[]
			let ly_lbl2=[]
			let ly_dta12=[]
			let ly_dta22=[]
			let lyact_dta2=[]
			let cnt=0;			 
			$.each( r.message.ideal, function( key, value ) {
				if(cnt< 43) {					
				ly_lbl.push(value.age);
				ly_dta1.push(value.v1);
				ly_dta2.push(value.v2);
				lyact_dta.push(value.act_feed);
				}else{
					ly_lbl2.push(value.age);
				ly_dta12.push(value.v1);
				ly_dta22.push(value.v2);
				lyact_dta2.push(value.act_feed);
				}
				cnt++;
				});
				
				//console.log(ly_lbl);
			 //--------------------------------------------------
			 let chart = new frappe.Chart( "#layer-feed", { 
				 // or DOM element ref: https://frappe.io/charts
				 data: {
					labels: ly_lbl,
				
					datasets: [
						{
							chartType: 'line',
							name: "Min Std. Feed Intake",
							values: ly_dta1
						},
						{
							chartType: 'line',
							name: "Max Std. Feed Intake",
							values: ly_dta2
						},
						{							
							chartType: 'line',
							name: "Actual Feed Intake",
							values: lyact_dta
						},
						
					],
				},
				title: "Laying Feed",
				type: 'line', // or 'bar', 'line', 'pie', 'percentage'
				height: 300,				
				colors: ['#ff2e2e','#55af46','#2490ef'],
				axisOptions: {					
					yLabel: "Value", // Label for y-axis
					
				  },
				  tooltipOptions: {
					formatTooltipX: d => d + ' Week',
					formatTooltipY: d => ' Feed '+d+' gm',
				}
				
			  });

			  let chart2 = new frappe.Chart( "#layer-feed2", { 
				// or DOM element ref: https://frappe.io/charts
				data: {
				   labels: ly_lbl2,
			   
				   datasets: [
					   {
						   chartType: 'line',
						   name: "Min Std. Feed Intake",
						   values: ly_dta12
					   },
					   {
						   chartType: 'line',
						   name: "Max Std. Feed Intake",
						   values: ly_dta22
					   },
					   {							
						   chartType: 'line',
						   name: "Actual Feed Intake",
						   values: lyact_dta2
					   },
					   
				   ],
			   },
			   title: "Laying Feed",
			   type: 'line', // or 'bar', 'line', 'pie', 'percentage'
			   height: 300,				
			   colors: ['#ff2e2e','#55af46','#2490ef'],
			   axisOptions: {					
				   yLabel: "Value", // Label for y-axis
				   
				 },
				 tooltipOptions: {
				   formatTooltipX: d => d + ' Week',
				   formatTooltipY: d => ' Feed '+d+' gm',
			   }
			   
			 });

			 //--------------------------------------------------
			}
		  }
		},
	  });
}

function laying_weight_graph(batch,period)
{
	
	$("#layer-weight").html('');
	frappe.call({
		method: 'livestock.poultry.page.poultry_dashbord.poultry_dashbord.get_lay_weight_graph',
		//freeze: 1,
		//freeze_message: 'Data loading ...please waite',
		args: {
			batch: batch,
			period: period,					  
		  },
		callback: function (r) {
		  if (r.message) {
			laygp_weight_xl=r.message.ideal

			if(laygp_weight_xl.length){

			let ly_lbl=[]
			let ly_dta1=[]
			let ly_dta2=[]
			let lyact_dta=[]
			let ly_lbl2=[]
			let ly_dta12=[]
			let ly_dta22=[]
			let lyact_dta2=[]
			let cnt=0;			 
			$.each( r.message.ideal, function( key, value ) {
				if(cnt< 43) {					
				ly_lbl.push(value.age);
				ly_dta1.push(value.v1);
				ly_dta2.push(value.v2);
				lyact_dta.push(value.act_weight);
				}else {
					ly_lbl2.push(value.age);
					ly_dta12.push(value.v1);
					ly_dta22.push(value.v2);
					lyact_dta2.push(value.act_weight);
				}
				cnt++;
				});
				
				//console.log(ly_lbl);
			 //--------------------------------------------------
			 let chart = new frappe.Chart( "#layer-weight", { 
				 // or DOM element ref: https://frappe.io/charts
				 data: {
					labels: ly_lbl,
				
					datasets: [
						{
							chartType: 'line',
							name: "Min Std. Weight",
							values: ly_dta1
						},
						{
							chartType: 'line',
							name: "Max Std. Weight",
							values: ly_dta2
						},
						{							
							chartType: 'line',
							name: "Actual Weight",
							values: lyact_dta
						},
						
					],
				},
				title: "Laying Weight",
				type: 'line', // or 'bar', 'line', 'pie', 'percentage'
				height: 300,				
				colors: ['#ff2e2e','#55af46','#2490ef'],
				axisOptions: {					
					yLabel: "Value", // Label for y-axis
					
				  },
				  tooltipOptions: {
					formatTooltipX: d => d + ' Week',
					formatTooltipY: d => ' Weight '+d+' Kg',
				}
				
			  });
			  let chart2 = new frappe.Chart( "#layer-weight2", { 
				// or DOM element ref: https://frappe.io/charts
				data: {
				   labels: ly_lbl2,
			   
				   datasets: [
					   {
						   chartType: 'line',
						   name: "Min Std. Weight",
						   values: ly_dta12
					   },
					   {
						   chartType: 'line',
						   name: "Max Std. Weight",
						   values: ly_dta22
					   },
					   {							
						   chartType: 'line',
						   name: "Actual Weight",
						   values: lyact_dta2
					   },
					   
				   ],
			   },
			   title: "Laying Weight",
			   type: 'line', // or 'bar', 'line', 'pie', 'percentage'
			   height: 300,				
			   colors: ['#ff2e2e','#55af46','#2490ef'],
			   axisOptions: {					
				   yLabel: "Value", // Label for y-axis
				   
				 },
				 tooltipOptions: {
				   formatTooltipX: d => d + ' Week',
				   formatTooltipY: d => ' Weight '+d+' Kg',
			   }
			   
			 });


			 //--------------------------------------------------
			}
		  }
		},
	  });
}

function rearing_feed_graph(batch,period)
{
	
	$("#rear-feed").html('');
	frappe.call({
		method: 'livestock.poultry.page.poultry_dashbord.poultry_dashbord.get_rear_feed_graph',
		//freeze: 1,
		//freeze_message: 'Data loading ...please waite',
		args: {
			batch: batch,
			period: period,					  
		  },
		callback: function (r) {
		  if (r.message) {
			reargp_feed_xl=r.message.ideal

			if(reargp_feed_xl.length){

			let ly_lbl=[]
			let ly_dta1=[]
			let ly_dta2=[]
			let lyact_dta=[]
						 
			$.each( r.message.ideal, function( key, value ) {					
				ly_lbl.push(value.age);
				ly_dta1.push(value.v1);
				ly_dta2.push(value.v2);
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
							name: "Min Std. Feed Intake",
							values: ly_dta1
						},
						{
							chartType: 'line',
							name: "Max Std. Feed Intake",
							values: ly_dta2
						},
						{							
							chartType: 'line',
							name: "Actual Feed Intake",
							values: lyact_dta
						},
						
					],
				},
				title: "Rearing Feed",
				type: 'line', // or 'bar', 'line', 'pie', 'percentage'
				height: 300,				
				colors: ['#ff2e2e','#55af46','#2490ef'],
				axisOptions: {					
					yLabel: "Value", // Label for y-axis
					
				  },
				  tooltipOptions: {
					formatTooltipX: d => d + ' Week',
					formatTooltipY: d => ' Feed '+d+' gm',
				}
				
			  });

			 //--------------------------------------------------
			}
		  }
		},
	  });
}

function rearing_weight_graph(batch,period)
{
	
	$("#rear-weight").html('');
	frappe.call({
		method: 'livestock.poultry.page.poultry_dashbord.poultry_dashbord.get_rear_weight_graph',
		//freeze: 1,
		//freeze_message: 'Data loading ...please waite',
		args: {
			batch: batch,
			period: period,					  
		  },
		callback: function (r) {
		  if (r.message) {
			reargp_weight_xl=r.message.ideal

			if(reargp_weight_xl.length){

			let ly_lbl=[]
			let ly_dta1=[]
			let ly_dta2=[]
			let lyact_dta=[]
						 
			$.each( r.message.ideal, function( key, value ) {					
				ly_lbl.push(value.age);
				ly_dta1.push(value.v1);
				ly_dta2.push(value.v2);
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
							name: "Min Std. Weight",
							values: ly_dta1
						},
						{
							chartType: 'line',
							name: "Max Std. Weight",
							values: ly_dta2
						},
						{							
							chartType: 'line',
							name: "Actual Weight",
							values: lyact_dta
						},
						
					],
				},
				title: "Rearing Weight",
				type: 'line', // or 'bar', 'line', 'pie', 'percentage'
				height: 300,				
				colors: ['#ff2e2e','#55af46','#2490ef'],
				axisOptions: {					
					yLabel: "Value", // Label for y-axis
					
				  },
				  tooltipOptions: {
					formatTooltipX: d => d + ' Week',
					formatTooltipY: d => ' Weight '+d+' kg',
				}
				
			  });

			 //--------------------------------------------------
			}
		  }
		},
	  });
}

function laying_performance_graph(batch,period)
{
	
	$("#layer-performance").html('');
	frappe.call({
		method: 'livestock.poultry.page.poultry_dashbord.poultry_dashbord.get_lay_performance',
		//freeze: 1,
		//freeze_message: 'Data loading ...please waite',
		args: {
			batch: batch,
			period: period,					  
		  },
		callback: function (r) {
		  if (r.message) {
			laygp_performance_xl=r.message.ideal

			if(laygp_performance_xl.length){

			let ly_lbl=[]
			let ly_dta1=[]
			let ly_dta2=[]
			let lyact_dta=[]
			let ly_lbl2=[]
			let ly_dta12=[]
			let ly_dta22=[]
			let lyact_dta2=[]
			let cnt=0;

			$.each( r.message.ideal, function( key, value ) {
				if(cnt<43){					
				ly_lbl.push(value.age);
				ly_dta1.push(value.v1);
				ly_dta2.push(value.v2);
				lyact_dta.push(value.act_eggs);
				}else{
					ly_lbl2.push(value.age);
					ly_dta12.push(value.v1);
					ly_dta22.push(value.v2);
					lyact_dta2.push(value.act_eggs);
				}
				cnt++;
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
							name: "Min Std. Eggs ",
							values: ly_dta1
						},
						{
							chartType: 'line',
							name: "Max Std. Eggs",
							values: ly_dta2
						},
						{							
							chartType: 'line',
							name: "Actual Eggs",
							values: lyact_dta
						},
						
					],
				},
				title: "Performance",
				type: 'line', // or 'bar', 'line', 'pie', 'percentage'
				height: 300,				
				colors: ['#ff2e2e','#55af46','#2490ef'],
				axisOptions: {					
					yLabel: "Value", // Label for y-axis
					
				  },
				  tooltipOptions: {
					formatTooltipX: d => d + ' Week',
					formatTooltipY: d => ' Egg '+d+' Nos',
				}
				
			  });

			  let chart2 = new frappe.Chart( "#layer-performance2", { 
				// or DOM element ref: https://frappe.io/charts
				data: {
				   labels: ly_lbl2,
			   
				   datasets: [
					   {
						   chartType: 'line',
						   name: "Min Std. Eggs ",
						   values: ly_dta12
					   },
					   {
						   chartType: 'line',
						   name: "Max Std. Eggs",
						   values: ly_dta22
					   },
					   {							
						   chartType: 'line',
						   name: "Actual Eggs",
						   values: lyact_dta2
					   },
					   
				   ],
			   },
			   title: "Performance",
			   type: 'line', // or 'bar', 'line', 'pie', 'percentage'
			   height: 300,				
			   colors: ['#ff2e2e','#55af46','#2490ef'],
			   axisOptions: {					
				   yLabel: "Value", // Label for y-axis
				   
				 },
				 tooltipOptions: {
				   formatTooltipX: d => d + ' Week',
				   formatTooltipY: d => ' Egg '+d+' Nos',
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
					var divlay=document.getElementById('production');
					var divbud=document.getElementById('budget');
					var divmorgp=document.getElementById('mortality');
					  var newWin=window.open('','Print-Window');
					  newWin.document.open();
					  newWin.document.write('<html><style>table, th, td {border: 1px solid;border-collapse: collapse; } table{ width:100%;} table td{ text-align:right;} #rear-chart{display:none;}#layer-chart{display:none;} .table-secondary td,.table-secondary th {background-color: #d5d7d9;font-weight: bold;}  @media print { #prod{overflow-x:unset !important;} #rer{overflow-x:unset !important;} } </style><body onload="window.print()">'+divbud.innerHTML+divrear.innerHTML+divlay.innerHTML+divmorgp.innerHTML+'</body></html>');
					  newWin.document.close();
					  setTimeout(function(){newWin.close();},10);
		  
				}

