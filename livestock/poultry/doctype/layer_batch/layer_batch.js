// Copyright (c) 2023, alantechnologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Layer Batch', {
	 refresh: function(frm) {
		$(".grid-add-row").hide();
        frm.set_query('from_hatchery_project', function(doc, cdt, cdn) {
		  
			return {
			   "filters": {
			"project_type": "Hatchery",
		}
			};
		});
        
        var totom=0
        $.each (frm.doc.laying_mortality, function(i, dt){
            totom+=dt.total; 
        });
        frm.doc.total_laying_mortality=totom
        frm.refresh_field('total_laying_mortality');

        var totom=0
        $.each (frm.doc.rearing_daily_mortality, function(i, dt){
            totom+=dt.total; 
        });
        frm.doc.total_mortaliy=totom
        frm.refresh_field('total_mortaliy');


        frm.doc.current_alive_chicks=frm.doc.doc_placed-frm.doc.total_laying_mortality-frm.doc.total_mortaliy
        frm.refresh_field('current_alive_chicks');

        //====================================================
        if (frm.doc.item_processed!=1)
        {       
            frm.add_custom_button(__('Transfer Flock To layer Shed'), function(){
        
                if(frm.doc.number_received < 1 || frm.doc.number_received===''){
                    frappe.throw(__("Please Enter Number Of DOC received"));
                    return false;
                    }
                    
                if(frm.doc.doc_placed < 1 || frm.doc.doc_placed===''){
                    frappe.throw(__("Please Enter Chicks Placed "));
                    return false;
                    }	
                    
                if(frm.doc.__unsaved){
                    frappe.throw(__("Please save document before generate stock entry"));
                    return false;
                    }
                    
                    frappe.prompt(
                        [
                        {  fieldtype: "Int",
                            label: __("Flock Transfer Quantity"),
                            fieldname: "transfer_qty",
                            reqd:'1',
                            default:frm.doc.current_alive_chicks,                                
                        },
                        {  fieldtype: "Int",
                            label: __("No of Rooster In Flock"),
                            fieldname: "rooster_qty",
                            reqd:'1',
                            default:'0',                                
                        },
                        {  fieldtype: "Date",
                        label: __("Transfer Date"),
                        fieldname: "transfer_date",
                        reqd:'1'                                
                        }
                        ,{  fieldtype: "Link",
                        label: __("Transfer Warehouse"),
                        fieldname: "transfer_warehouse",
                        options:"Warehouse"                                
                    }],
                        function(data) {
                            
                            frappe.call(
                                { 
                                    method: "livestock.poultry.doctype.layer_batch.layer_batch.stock_entry",
                                    args: {
                                        batch:frm.doc.name,
                                        transfer_qty:data.transfer_qty,
                                        rooster_qty:data.rooster_qty,
                                        transfer_date:data.transfer_date,
                                        transfer_warehouse:data.transfer_warehouse
                                    },
                                    callback: function(r) 
                                        { 
                                            if(r.message) 
                                                { 
                                                    var doclist = frappe.model.sync(r.message);
                                                    //frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
                                                } 
                                        }
                                });
                        },
                        __("Item Transfer"),
                        __("Confirm")
                    );       
            //console.log(frm.doc);  
                
           
                }).removeClass("btn-default").addClass("btn-success");
        }
	 },
     number_received:function(frm)
     {
        frm.doc.doc_placed=frm.doc.number_received-frm.doc.mortality
        frm.doc.current_alive_chicks=frm.doc.doc_placed
        frm.refresh_field('doc_placed');
        frm.refresh_field('current_alive_chicks');
     },
     mortality:function(frm)
     {
        frm.doc.doc_placed=frm.doc.number_received-frm.doc.mortality
        frm.doc.current_alive_chicks=frm.doc.doc_placed
        frm.refresh_field('doc_placed');
        frm.refresh_field('current_alive_chicks');
     },
     total_laying_mortality:function(frm)
     {
        frm.doc.current_alive_chicks=frm.doc.doc_placed-frm.doc.total_laying_mortality
        frm.refresh_field('current_alive_chicks');
     },
     total_mortaliy:function(frm)
     {
        frm.doc.current_alive_chicks=frm.doc.doc_placed-frm.doc.total_mortaliy
        frm.refresh_field('current_alive_chicks');
     },
     add_rearing_feed:function(frm)
     {
         let d = new frappe.ui.Dialog({
             title: 'Add Feed',
             fields: [                        
                 {
                     label: 'Date',
                     fieldname: 'date',
                     fieldtype: 'Date',
                     reqd:'1'
                 },
                 {
                     label: 'Item',
                     fieldname: 'item_code',
                     fieldtype: 'Link',
                     options:'Item',
                     reqd:'1'
                 },
                 {
                     label: 'Qty',
                     fieldname: 'qty',
                     fieldtype: 'Int',
                     reqd:'1'
                 },
                 {
                     label: 'Uom',
                     fieldname: 'uom',
                     fieldtype: 'Link',
                     options:'UOM',
                     reqd:'1'
                 }
             ],
             primary_action_label: 'Add Feed',
             primary_action(values) {                        

                 let rw=frm.add_child("rearing_feed");
                 rw.date=values.date;
                 rw.item_code=values.item_code;
                 rw.qty=values.qty;
                 rw.uom=values.uom;
                 frm.refresh_field('rearing_feed');
                 d.hide();
                 $(".grid-add-row").hide();
                 frm.doc.__unsaved=0;
                 
                 frappe.call(
                     { 
                         method: "livestock.poultry.doctype.layer_batch.layer_batch.added_feed_rearing",
                         args: {
                             batch:frm.doc.name,
                             parentfield:'rearing_feed',
                             date:values.date,
                             item_code:values.item_code,
                             qty:values.qty,
                             uom:values.uom
                         },
                         callback: function(r) 
                             { 
                                 if(r.message) 
                                     { 
                                         //var doclist = frappe.model.sync(r.message);
                                         //doclist[0].name
                                        rw.rate=r.message.rate;
                                        rw.conversion_factor=r.message.conversion_factor;
                                        rw.item_name=r.message.item_name;
                                        frm.refresh_field('rearing_feed');
                                     } 
                             }
                     });

             }
         });
         
         d.show();
         
     },
            add_laying_feed:function(frm)
            {
                let d = new frappe.ui.Dialog({
                    title: 'Add Feed',
                    fields: [                        
                        {
                            label: 'Date',
                            fieldname: 'date',
                            fieldtype: 'Date',
                            reqd:'1'
                        },
						{
                            label: 'Item',
                            fieldname: 'item_code',
                            fieldtype: 'Link',
							options:'Item',
                            reqd:'1'
                        },
						{
                            label: 'Qty',
                            fieldname: 'qty',
                            fieldtype: 'Int',
                            reqd:'1'
                        },
						{
                            label: 'Uom',
                            fieldname: 'uom',
                            fieldtype: 'Link',
							options:'UOM',
                            reqd:'1'
                        }
                    ],
                    primary_action_label: 'Add Feed',
                    primary_action(values) {                        

                        let rw=frm.add_child("laying_feed");
						rw.date=values.date;
						rw.item_code=values.item_code;
						rw.qty=values.qty;
						rw.uom=values.uom;
						frm.refresh_field('laying_feed');
						d.hide();
						$(".grid-add-row").hide();
                        frm.doc.__unsaved=0;
                        
						frappe.call(
                            { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.added_feed_rearing",
                                args: {
                                    batch:frm.doc.name,
                                    parentfield:'laying_feed',
                                    date:values.date,
									item_code:values.item_code,
									qty:values.qty,
									uom:values.uom
                                },
                                callback: function(r) 
                                    { 
                                        if(r.message) 
                                            { 
                                                rw.rate=r.message.rate;
                                                rw.conversion_factor=r.message.conversion_factor;
                                                rw.item_name=r.message.item_name;
                                                frm.refresh_field('laying_feed');
                                                //var doclist = frappe.model.sync(r.message);
                                                //doclist[0].name
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                
            },
			add_rearing_medicine:function(frm)
            {
                let d = new frappe.ui.Dialog({
                    title: 'Add Medicine',
                    fields: [                        
                        {
                            label: 'Date',
                            fieldname: 'date',
                            fieldtype: 'Date',
                            reqd:'1'
                        },
						{
                            label: 'Item',
                            fieldname: 'item_code',
                            fieldtype: 'Link',
							options:'Item',
                            reqd:'1'
                        },
						{
                            label: 'Qty',
                            fieldname: 'qty',
                            fieldtype: 'Int',
                            reqd:'1'
                        },
						{
                            label: 'Uom',
                            fieldname: 'uom',
                            fieldtype: 'Link',
							options:'UOM',
                            reqd:'1'
                        },
						{
                            label: 'Remark',
                            fieldname: 'remark',
                            fieldtype: 'Text',							
                            
                        }
                    ],
                    primary_action_label: 'Add Medicine',
                    primary_action(values) {                        

                        let rw=frm.add_child("rearing_medicine");
						rw.date=values.date;
						rw.item_code=values.item_code;
						rw.qty=values.qty;
						rw.uom=values.uom;
						rw.remark=values.remark;
						frm.refresh_field('rearing_medicine');
						d.hide();
						$(".grid-add-row").hide();
                        frm.doc.__unsaved=0;
                        
						frappe.call(
                            { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.added_medicine_rearing",
                                args: {
                                    batch:frm.doc.name,
                                    date:values.date,
                                    parentfield:'rearing_medicine',
									item_code:values.item_code,
									qty:values.qty,
									uom:values.uom,
									remark:values.remark
                                },
                                callback: function(r) 
                                    { 
                                        if(r.message) 
                                            { 
                                                rw.rate=r.message.rate;
                                        rw.conversion_factor=r.message.conversion_factor;
                                        rw.item_name=r.message.item_name;
                                        frm.refresh_field('rearing_medicine');
                                                //var doclist = frappe.model.sync(r.message);
                                                //doclist[0].name
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                
            },
            add_laying_medicine:function(frm)
            {
                let d = new frappe.ui.Dialog({
                    title: 'Add Medicine',
                    fields: [                        
                        {
                            label: 'Date',
                            fieldname: 'date',
                            fieldtype: 'Date',
                            reqd:'1'
                        },
						{
                            label: 'Item',
                            fieldname: 'item_code',
                            fieldtype: 'Link',
							options:'Item',
                            reqd:'1'
                        },
						{
                            label: 'Qty',
                            fieldname: 'qty',
                            fieldtype: 'Int',
                            reqd:'1'
                        },
						{
                            label: 'Uom',
                            fieldname: 'uom',
                            fieldtype: 'Link',
							options:'UOM',
                            reqd:'1'
                        },
						{
                            label: 'Remark',
                            fieldname: 'remark',
                            fieldtype: 'Text',							
                            
                        }
                    ],
                    primary_action_label: 'Add Medicine',
                    primary_action(values) {                        

                        let rw=frm.add_child("laying_medicine");
						rw.date=values.date;
						rw.item_code=values.item_code;
						rw.qty=values.qty;
						rw.uom=values.uom;
						rw.remark=values.remark;
						frm.refresh_field('laying_medicine');
						d.hide();
						$(".grid-add-row").hide();
                        frm.doc.__unsaved=0;
                        
						frappe.call(
                            { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.added_medicine_rearing",
                                args: {
                                    batch:frm.doc.name,
                                    date:values.date,
                                    parentfield:'laying_medicine',
									item_code:values.item_code,
									qty:values.qty,
									uom:values.uom,
									remark:values.remark
                                },
                                callback: function(r) 
                                    { 
                                        if(r.message) 
                                            { 
                                                rw.rate=r.message.rate;
                                        rw.conversion_factor=r.message.conversion_factor;
                                        rw.item_name=r.message.item_name;
                                        frm.refresh_field('laying_medicine');
                                                //var doclist = frappe.model.sync(r.message);
                                                //doclist[0].name
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                
            },
            add_rearing_vaccine:function(frm)
            {
                let d = new frappe.ui.Dialog({
                    title: 'Add Vaccine',
                    fields: [                        
                        {
                            label: 'Date',
                            fieldname: 'date',
                            fieldtype: 'Date',
                            reqd:'1'
                        },
						{
                            label: 'Item',
                            fieldname: 'item_code',
                            fieldtype: 'Link',
							options:'Item',
                            reqd:'1'
                        },
						{
                            label: 'Qty',
                            fieldname: 'qty',
                            fieldtype: 'Int',
                            reqd:'1'
                        },
						{
                            label: 'Uom',
                            fieldname: 'uom',
                            fieldtype: 'Link',
							options:'UOM',
                            reqd:'1'
                        },
						{
                            label: 'Remark',
                            fieldname: 'remark',
                            fieldtype: 'Text',							
                            
                        }
                    ],
                    primary_action_label: 'Add Vaccine',
                    primary_action(values) {                        

                        let rw=frm.add_child("rearing_vaccine");
						rw.date=values.date;
						rw.item_code=values.item_code;
						rw.qty=values.qty;
						rw.uom=values.uom;
						rw.remark=values.remark;
						frm.refresh_field('rearing_vaccine');
						d.hide();
						$(".grid-add-row").hide();
                        frm.doc.__unsaved=0;
                        
						frappe.call(
                            { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.add_vaccine_rearing",
                                args: {
                                    batch:frm.doc.name,
                                    parentfield:'rearing_vaccine',
                                    date:values.date,
									item_code:values.item_code,
									qty:values.qty,
									uom:values.uom,
									remark:values.remark
                                },
                                callback: function(r) 
                                    { 
                                        if(r.message) 
                                            { 
                                                rw.rate=r.message.rate;
                                        rw.conversion_factor=r.message.conversion_factor;
                                        rw.item_name=r.message.item_name;
                                        frm.refresh_field('rearing_vaccine');
                                                //var doclist = frappe.model.sync(r.message);
                                                //doclist[0].name
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                
            },
            add_laying_vaccine:function(frm)
            {
                let d = new frappe.ui.Dialog({
                    title: 'Add Vaccine',
                    fields: [                        
                        {
                            label: 'Date',
                            fieldname: 'date',
                            fieldtype: 'Date',
                            reqd:'1'
                        },
						{
                            label: 'Item',
                            fieldname: 'item_code',
                            fieldtype: 'Link',
							options:'Item',
                            reqd:'1'
                        },
						{
                            label: 'Qty',
                            fieldname: 'qty',
                            fieldtype: 'Int',
                            reqd:'1'
                        },
						{
                            label: 'Uom',
                            fieldname: 'uom',
                            fieldtype: 'Link',
							options:'UOM',
                            reqd:'1'
                        },
						{
                            label: 'Remark',
                            fieldname: 'remark',
                            fieldtype: 'Text',							
                            
                        }
                    ],
                    primary_action_label: 'Add Vaccine',
                    primary_action(values) {                        

                        let rw=frm.add_child("laying_vaccine");
						rw.date=values.date;
						rw.item_code=values.item_code;
						rw.qty=values.qty;
						rw.uom=values.uom;
						rw.remark=values.remark;
						frm.refresh_field('laying_vaccine');
						d.hide();
						$(".grid-add-row").hide();
                        frm.doc.__unsaved=0;
                        
						frappe.call(
                            { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.add_vaccine_rearing",
                                args: {
                                    batch:frm.doc.name,
                                    parentfield:'laying_vaccine',
                                    date:values.date,
									item_code:values.item_code,
									qty:values.qty,
									uom:values.uom,
									remark:values.remark
                                },
                                callback: function(r) 
                                    { 
                                        if(r.message) 
                                            { 
                                                rw.rate=r.message.rate;
                                        rw.conversion_factor=r.message.conversion_factor;
                                        rw.item_name=r.message.item_name;
                                        frm.refresh_field('laying_vaccine');
                                                //var doclist = frappe.model.sync(r.message);
                                                //doclist[0].name
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                
            },
            add_rearing_items:function(frm)
            {
                let d = new frappe.ui.Dialog({
                    title: 'Add Items',
                    fields: [                        
                        {
                            label: 'Date',
                            fieldname: 'date',
                            fieldtype: 'Date',
                            reqd:'1'
                        },
						{
                            label: 'Item',
                            fieldname: 'item_code',
                            fieldtype: 'Link',
							options:'Item',
                            reqd:'1'
                        },
						{
                            label: 'Qty',
                            fieldname: 'qty',
                            fieldtype: 'Int',
                            reqd:'1'
                        },
						{
                            label: 'Uom',
                            fieldname: 'uom',
                            fieldtype: 'Link',
							options:'UOM',
                            reqd:'1'
                        },
						
                    ],
                    primary_action_label: 'Add Items',
                    primary_action(values) {                        

                        let rw=frm.add_child("rearing_items");
						rw.date=values.date;
						rw.item_code=values.item_code;
						rw.qty=values.qty;
						rw.uom=values.uom;						
						frm.refresh_field('rearing_items');
						d.hide();
						$(".grid-add-row").hide();
                        frm.doc.__unsaved=0;
                        
						frappe.call(
                            { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.add_rearing_items",
                                args: {
                                    batch:frm.doc.name,
                                    parentfield:'rearing_items',
                                    date:values.date,
									item_code:values.item_code,
									qty:values.qty,
									uom:values.uom,
                                },
                                callback: function(r) 
                                    { 
                                        if(r.message) 
                                            { 
                                                rw.rate=r.message.rate;
                                        rw.conversion_factor=r.message.conversion_factor;
                                        rw.item_name=r.message.item_name;
                                        frm.refresh_field('rearing_items');
                                                //var doclist = frappe.model.sync(r.message);
                                                //doclist[0].name
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                
            },
            add_laying_items:function(frm)
            {
                let d = new frappe.ui.Dialog({
                    title: 'Add Items',
                    fields: [                        
                        {
                            label: 'Date',
                            fieldname: 'date',
                            fieldtype: 'Date',
                            reqd:'1'
                        },
						{
                            label: 'Item',
                            fieldname: 'item_code',
                            fieldtype: 'Link',
							options:'Item',
                            reqd:'1'
                        },
						{
                            label: 'Qty',
                            fieldname: 'qty',
                            fieldtype: 'Int',
                            reqd:'1'
                        },
						{
                            label: 'Uom',
                            fieldname: 'uom',
                            fieldtype: 'Link',
							options:'UOM',
                            reqd:'1'
                        },
						
                    ],
                    primary_action_label: 'Add Items',
                    primary_action(values) {                        

                        let rw=frm.add_child("laying_items");
						rw.date=values.date;
						rw.item_code=values.item_code;
						rw.qty=values.qty;
						rw.uom=values.uom;						
						frm.refresh_field('laying_items');
						d.hide();
						$(".grid-add-row").hide();
                        frm.doc.__unsaved=0;
                        
						frappe.call(
                            { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.add_rearing_items",
                                args: {
                                    batch:frm.doc.name,
                                    parentfield:'laying_items',
                                    date:values.date,
									item_code:values.item_code,
									qty:values.qty,
									uom:values.uom,
                                },
                                callback: function(r) 
                                    { 
                                        if(r.message) 
                                            { 
                                                rw.rate=r.message.rate;
                                        rw.conversion_factor=r.message.conversion_factor;
                                        rw.item_name=r.message.item_name;
                                        frm.refresh_field('laying_items');
                                                //var doclist = frappe.model.sync(r.message);
                                                //doclist[0].name
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                
            },
            add_rearing_mortality:function(frm)
            {
                let d = new frappe.ui.Dialog({
                    title: 'Add Mortality',
                    fields: [                        
                        {
                            label: 'Date',
                            fieldname: 'date',
                            fieldtype: 'Date',
                            reqd:'1'
                        },
						{
                            label: 'Age In Days',
                            fieldname: 'age',
                            fieldtype: 'Int',
							default:'0',
                            reqd:'1'
                        },
						{
                            label: 'Evening',
                            fieldname: 'evening',
                            fieldtype: 'Int',
							default:'0',
                        },
						{
                            label: 'Morning',
                            fieldname: 'morning',
                            fieldtype: 'Int',
							default:'0',
                        },
						{
                            label: 'Remark',
                            fieldname: 'remark',
                            fieldtype: 'Text',							
                            
                        }
                    ],
                    primary_action_label: 'Add Mortality',
                    primary_action(values) {                        

                        let rw=frm.add_child("rearing_daily_mortality");
						rw.date=values.date;
						rw.age=values.age;
						rw.evening=values.evening;
						rw.morning=values.morning;
						rw.total=values.evening+values.morning;
                        rw.remark=values.remark;
						frm.refresh_field('rearing_daily_mortality');
						d.hide();
						$(".grid-add-row").hide();
                        frm.doc.__unsaved=0;
                        
						frappe.call(
                            { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.add_rearing_mortality",
                                args: {
                                    batch:frm.doc.name,
                                    parentfield:'rearing_daily_mortality',
                                    date:values.date,
									age:values.age,
									evening:values.evening,
									morning:values.morning,
                                    remark:values.remark
                                },
                                callback: function(r) 
                                    { 
                                        if(r.message) 
                                            { 
                                                //var doclist = frappe.model.sync(r.message);
                                                //doclist[0].name
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                
            },
            add_laying_mortality:function(frm)
            {
                let d = new frappe.ui.Dialog({
                    title: 'Add Mortality',
                    fields: [                        
                        {
                            label: 'Date',
                            fieldname: 'date',
                            fieldtype: 'Date',
                            reqd:'1'
                        },
						{
                            label: 'Age In Days',
                            fieldname: 'age',
                            fieldtype: 'Int',
							default:'0',
                            reqd:'1'
                        },
						{
                            label: 'Evening',
                            fieldname: 'evening',
                            fieldtype: 'Int',
							default:'0',
                        },
						{
                            label: 'Morning',
                            fieldname: 'morning',
                            fieldtype: 'Int',
							default:'0',
                        },
						{
                            label: 'Remark',
                            fieldname: 'remark',
                            fieldtype: 'Text',							
                            
                        }
                    ],
                    primary_action_label: 'Add Mortality',
                    primary_action(values) {                        

                        let rw=frm.add_child("laying_mortality");
						rw.date=values.date;
						rw.age=values.age;
						rw.evening=values.evening;
						rw.morning=values.morning;
						rw.total=values.evening+values.morning;
                        rw.remark=values.remark;
						frm.refresh_field('laying_mortality');
						d.hide();
						$(".grid-add-row").hide();
                        frm.doc.__unsaved=0;
                        
						frappe.call(
                            { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.add_rearing_mortality",
                                args: {
                                    batch:frm.doc.name,
                                    parentfield:'laying_mortality',
                                    date:values.date,
									age:values.age,
									evening:values.evening,
									morning:values.morning,
                                    remark:values.remark
                                },
                                callback: function(r) 
                                    { 
                                        if(r.message) 
                                            { 
                                                //var doclist = frappe.model.sync(r.message);
                                                //doclist[0].name
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                
            },
            add_rearing_temperature:function(frm)
            {
                let d = new frappe.ui.Dialog({
                    title: 'Add Temperature',
                    fields: [                        
                        {
                            label: 'Date',
                            fieldname: 'date',
                            fieldtype: 'Date',
                            reqd:'1'
                        },						
						{
                            label: 'Evening',
                            fieldname: 'evening',
                            fieldtype: 'Float',
							default:'0',
                        },
						{
                            label: 'Morning',
                            fieldname: 'morning',
                            fieldtype: 'Float',
							default:'0',
                        },						
                    ],
                    primary_action_label: 'Add Temperature',
                    primary_action(values) {                        

                        let rw=frm.add_child("rearing_temperature");
						rw.date=values.date;						
						rw.evening=values.evening;
						rw.morning=values.morning;						
						frm.refresh_field('rearing_temperature');
						d.hide();
						$(".grid-add-row").hide();
                        frm.doc.__unsaved=0;
                        
						frappe.call(
                            { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.add_rearing_temperature",
                                args: {
                                    batch:frm.doc.name,
                                    parentfield:'rearing_temperature',
                                    date:values.date,
									evening:values.evening,
									morning:values.morning,
                                },
                                callback: function(r) 
                                    { 
                                        if(r.message) 
                                            { 
                                                //var doclist = frappe.model.sync(r.message);
                                                //doclist[0].name
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                
            },
            add_laying_temperature:function(frm)
            {
                let d = new frappe.ui.Dialog({
                    title: 'Add Temperature',
                    fields: [                        
                        {
                            label: 'Date',
                            fieldname: 'date',
                            fieldtype: 'Date',
                            reqd:'1'
                        },						
						{
                            label: 'Evening',
                            fieldname: 'evening',
                            fieldtype: 'Float',
							default:'0',
                        },
						{
                            label: 'Morning',
                            fieldname: 'morning',
                            fieldtype: 'Float',
							default:'0',
                        },						
                    ],
                    primary_action_label: 'Add Temperature',
                    primary_action(values) {                        

                        let rw=frm.add_child("laying_temperature");
						rw.date=values.date;						
						rw.evening=values.evening;
						rw.morning=values.morning;						
						frm.refresh_field('laying_temperature');
						d.hide();
						$(".grid-add-row").hide();
                        frm.doc.__unsaved=0;
                        
						frappe.call(
                            { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.add_rearing_temperature",
                                args: {
                                    batch:frm.doc.name,
                                    parentfield:'laying_temperature',
                                    date:values.date,
									evening:values.evening,
									morning:values.morning,
                                },
                                callback: function(r) 
                                    { 
                                        if(r.message) 
                                            { 
                                                //var doclist = frappe.model.sync(r.message);
                                                //doclist[0].name
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                
            },
            add_rearing_weight:function(frm)
            {
                let d = new frappe.ui.Dialog({
                    title: 'Add Weight',
                    fields: [                        
                        {
                            label: 'Date',
                            fieldname: 'date',
                            fieldtype: 'Date',
                            reqd:'1'
                        },						
						{
                            label: 'Week',
                            fieldname: 'week',
                            fieldtype: 'Int',
							default:'0',
                        },
						{
                            label: 'Weight',
                            fieldname: 'weight',
                            fieldtype: 'Float',
							default:'0',
                        },						
                    ],
                    primary_action_label: 'Add Weight',
                    primary_action(values) {                        

                        let rw=frm.add_child("rearing_weight");
						rw.date=values.date;						
						rw.week=values.week;
						rw.weight=values.weight;						
						frm.refresh_field('rearing_weight');
						d.hide();
						$(".grid-add-row").hide();
                        frm.doc.__unsaved=0;
                        
						frappe.call(
                            { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.add_rearing_weight",
                                args: {
                                    batch:frm.doc.name,
                                    parentfield:'rearing_weight',
                                    date:values.date,
									week:values.week,
									weight:values.weight,
                                },
                                callback: function(r) 
                                    { 
                                        if(r.message) 
                                            { 
                                                //var doclist = frappe.model.sync(r.message);
                                                //doclist[0].name
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                
            },
            add_laying_weight:function(frm)
            {
                let d = new frappe.ui.Dialog({
                    title: 'Add Weight',
                    fields: [                        
                        {
                            label: 'Date',
                            fieldname: 'date',
                            fieldtype: 'Date',
                            reqd:'1'
                        },						
						{
                            label: 'Week',
                            fieldname: 'week',
                            fieldtype: 'Int',
							default:'0',
                        },
						{
                            label: 'Weight',
                            fieldname: 'weight',
                            fieldtype: 'Float',
							default:'0',
                        },						
                    ],
                    primary_action_label: 'Add Weight',
                    primary_action(values) {                        

                        let rw=frm.add_child("laying_weight");
						rw.date=values.date;						
						rw.week=values.week;
						rw.weight=values.weight;						
						frm.refresh_field('laying_weight');
						d.hide();
						$(".grid-add-row").hide();
                        frm.doc.__unsaved=0;
                        
						frappe.call(
                            { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.add_rearing_weight",
                                args: {
                                    batch:frm.doc.name,
                                    parentfield:'laying_weight',
                                    date:values.date,
									week:values.week,
									weight:values.weight,
                                },
                                callback: function(r) 
                                    { 
                                        if(r.message) 
                                            { 
                                                //var doclist = frappe.model.sync(r.message);
                                                //doclist[0].name
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                
            },
            add_egg_production:function(frm)
            {
                let d = new frappe.ui.Dialog({
                    title: 'Add Egg',
                    fields: [                        
                        {
                            label: 'Date',
                            fieldname: 'date',
                            fieldtype: 'Date',
                            reqd:'1'
                        },
						{
                            label: 'Item',
                            fieldname: 'item_code',
                            fieldtype: 'Link',
							options:'Item',
                            reqd:'1'
                        },
						{
                            label: 'Qty',
                            fieldname: 'qty',
                            fieldtype: 'Int',
                            reqd:'1'
                        },
						{
                            label: 'Uom',
                            fieldname: 'uom',
                            fieldtype: 'Link',
							options:'UOM',
                            reqd:'1'
                        }
                    ],
                    primary_action_label: 'Add Egg',
                    primary_action(values) {                        

                        let rw=frm.add_child("egg_production");
						rw.date=values.date;
						rw.item_code=values.item_code;
						rw.qty=values.qty;
						rw.uom=values.uom;
						frm.refresh_field('egg_production');
						d.hide();
						$(".grid-add-row").hide();
                        frm.doc.__unsaved=0;
                        
						frappe.call(
                            { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.add_egg_production",
                                args: {
                                    batch:frm.doc.name,
                                    parentfield:'egg_production',
                                    date:values.date,
									item_code:values.item_code,
									qty:values.qty,
									uom:values.uom
                                },
                                callback: function(r) 
                                    { 
                                        if(r.message) 
                                            { 
                                                rw.rate=r.message.rate;
                                                rw.conversion_factor=r.message.conversion_factor;
                                                rw.item_name=r.message.item_name;
                                                frm.refresh_field('egg_production');
                                                //var doclist = frappe.model.sync(r.message);
                                                //doclist[0].name
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                
            }
});


//-------------------- Feed ---------------------------
frappe.ui.form.on('Layer Feed', {
    refresh: function(frm, cdt, cdn) {
        //console.log("ref");
    },
    qty:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_feed_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    uom:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_feed_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    item_code:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_feed_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    date:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_feed_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        d.__unsaved=0;
        frm.doc.__unsaved=0;
        
    },
    before_rearing_feed_remove:function(frm, cdt, cdn) {
        
        let row = frappe.get_doc(cdt, cdn);
        if (row.docstatus==1)
        {
            frappe.throw('cannot delete this data, it have associate entry in stock entry please delete stock entry and delete this data');
        }else{
            if(!row.__islocal)
            {
                frappe.call(
                    { 
                            method: "livestock.poultry.doctype.layer_batch.layer_batch.delete_feed_rearing",
                            args: {                               
                                name:row.name,   
                            },
                            callback: function(r) {  if(r.message) 
                                { 
                                    //var doclist = frappe.model.sync(r.message);
                                    //doclist[0].name
                                }   }
                    });
            }
        }
 
    },
    before_laying_feed_remove:function(frm, cdt, cdn) {
        
        let row = frappe.get_doc(cdt, cdn);
        if (row.docstatus==1)
        {
            frappe.throw('cannot delete this data, it have associate entry in stock entry please delete stock entry and delete this data');
        }else{
            if(!row.__islocal)
            {
                frappe.call(
                    { 
                            method: "livestock.poultry.doctype.layer_batch.layer_batch.delete_feed_rearing",
                            args: {                               
                                name:row.name,   
                            },
                            callback: function(r) {    }
                    });
            }
        }
 
    }
});

//--------------------- end feed------------------------------

//------------------ Medicine --------------------------------

frappe.ui.form.on('Layer Medicine', {
    refresh: function(frm, cdt, cdn) {
        //console.log("ref");
    },
    qty:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_medicine_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom,
                        remark:d.remark
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    uom:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_medicine_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom,
                        remark:d.remark
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    item_code:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_medicine_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom,
                        remark:d.remark
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    date:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_medicine_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom,
                        remark:d.remark
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        d.__unsaved=0;
        frm.doc.__unsaved=0;
        
    },
    remark:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_medicine_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom,
                        remark:d.remark
                    },
                    callback: function(r) { if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }    }
            });
        d.__unsaved=0;
        frm.doc.__unsaved=0;
        
    },
    before_rearing_medicine_remove:function(frm, cdt, cdn) {
        
        let row = frappe.get_doc(cdt, cdn);
        if (row.docstatus==1)
        {
            frappe.throw('cannot delete this data, it have associate entry in stock entry please delete stock entry and delete this data');
        }else{
            if(!row.__islocal)
            {
                frappe.call(
                    { 
                            method: "livestock.poultry.doctype.layer_batch.layer_batch.delete_medicine_rearing",
                            args: {                               
                                name:row.name,   
                            },
                            callback: function(r) {  if(r.message) 
                                { 
                                    //var doclist = frappe.model.sync(r.message);
                                    //doclist[0].name
                                }   }
                    });
            }
        }
 
    },
    before_laying_medicine_remove:function(frm, cdt, cdn) {
        
        let row = frappe.get_doc(cdt, cdn);
        if (row.docstatus==1)
        {
            frappe.throw('cannot delete this data, it have associate entry in stock entry please delete stock entry and delete this data');
        }else{
            if(!row.__islocal)
            {
                frappe.call(
                    { 
                            method: "livestock.poultry.doctype.layer_batch.layer_batch.delete_medicine_rearing",
                            args: {                               
                                name:row.name,   
                            },
                            callback: function(r) {    }
                    });
            }
        }
 
    }
});

//--------------------- end Medicine------------------------------

//------------------ Vaccine --------------------------------

frappe.ui.form.on('Layer Vaccine', {
    refresh: function(frm, cdt, cdn) {
        //console.log("ref");
    },
    qty:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_vaccine_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom,
                        remark:d.remark
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    uom:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_vaccine_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom,
                        remark:d.remark
                    },
                    callback: function(r) { if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }    }
            });
        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    item_code:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_vaccine_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom,
                        remark:d.remark
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    date:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_vaccine_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom,
                        remark:d.remark
                    },
                    callback: function(r) { if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }    }
            });
        d.__unsaved=0;
        frm.doc.__unsaved=0;
        
    },
    remark:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_vaccine_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom,
                        remark:d.remark
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        d.__unsaved=0;
        frm.doc.__unsaved=0;
        
    },
    before_rearing_vaccine_remove:function(frm, cdt, cdn) {
        
        let row = frappe.get_doc(cdt, cdn);
        if (row.docstatus==1)
        {
            frappe.throw('cannot delete this data, it have associate entry in stock entry please delete stock entry and delete this data');
        }else{
            if(!row.__islocal)
            {
                frappe.call(
                    { 
                            method: "livestock.poultry.doctype.layer_batch.layer_batch.delete_vaccine_rearing",
                            args: {                               
                                name:row.name,   
                            },
                            callback: function(r) {    }
                    });
            }
        }
 
    },
    before_laying_vaccine_remove:function(frm, cdt, cdn) {
        
        let row = frappe.get_doc(cdt, cdn);
        if (row.docstatus==1)
        {
            frappe.throw('cannot delete this data, it have associate entry in stock entry please delete stock entry and delete this data');
        }else{
            if(!row.__islocal)
            {
                frappe.call(
                    { 
                            method: "livestock.poultry.doctype.layer_batch.layer_batch.delete_vaccine_rearing",
                            args: {                               
                                name:row.name,   
                            },
                            callback: function(r) {    }
                    });
            }
        }
 
    }
});

//--------------------- end Vaccine------------------------------

//------------------ Other items --------------------------------

frappe.ui.form.on('Layer Other Items', {
    refresh: function(frm, cdt, cdn) {
        //console.log("ref");
    },
    qty:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_items_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom,
                        
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    uom:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_items_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom,
                        
                    },
                    callback: function(r) { if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }    }
            });
        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    item_code:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_items_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom,
                        
                    },
                    callback: function(r) { if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }    }
            });
        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    date:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_items_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom,
                        
                    },
                    callback: function(r) { if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }    }
            });
        d.__unsaved=0;
        frm.doc.__unsaved=0;
        
    },
    before_rearing_items_remove:function(frm, cdt, cdn) {
        
        let row = frappe.get_doc(cdt, cdn);
        if (row.docstatus==1)
        {
            frappe.throw('cannot delete this data, it have associate entry in stock entry please delete stock entry and delete this data');
        }else{
            if(!row.__islocal)
            {
                frappe.call(
                    { 
                            method: "livestock.poultry.doctype.layer_batch.layer_batch.delete_items_rearing",
                            args: {                               
                                name:row.name,   
                            },
                            callback: function(r) {    }
                    });
            }
        }
 
    },
    before_laying_items_remove:function(frm, cdt, cdn) {
        
        let row = frappe.get_doc(cdt, cdn);
        if (row.docstatus==1)
        {
            frappe.throw('cannot delete this data, it have associate entry in stock entry please delete stock entry and delete this data');
        }else{
            if(!row.__islocal)
            {
                frappe.call(
                    { 
                            method: "livestock.poultry.doctype.layer_batch.layer_batch.delete_items_rearing",
                            args: {                               
                                name:row.name,   
                            },
                            callback: function(r) {    }
                    });
            }
        }
 
    }
});

//------------------ Mortality --------------------------------

frappe.ui.form.on('Layer Mortality', {
    refresh: function(frm, cdt, cdn) {
        //console.log("ref");
    },
    age:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_mortality_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        age:d.age,
                        evening:d.evening,
                        morning:d.morning,
                        total:d.total,
                        remark:d.remark
                        
                    },
                    callback: function(r) { if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }    }
            });
        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    evening:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        d.total=d.evening+d.morning
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_mortality_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        age:d.age,
                        evening:d.evening,
                        morning:d.morning,
                        total:d.total,
                        remark:d.remark
                        
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
            var totom=0
            $.each (frm.doc.rearing_daily_mortality, function(i, dt){
                totom+=dt.total; 
            });
            frm.doc.total_mortaliy=totom
            frm.refresh_field('total_mortaliy');

            var totom=0
            $.each (frm.doc.laying_mortality, function(i, dt){
                totom+=dt.total; 
            });
            frm.doc.total_laying_mortality=totom
            frm.refresh_field('total_laying_mortality');

        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    morning:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        d.total=d.evening+d.morning
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_mortality_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        age:d.age,
                        evening:d.evening,
                        morning:d.morning,
                        total:d.total,
                        remark:d.remark
                        
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });

            var totom=0
            $.each (frm.doc.rearing_daily_mortality, function(i, dt){
                totom+=dt.total; 
            });
            frm.doc.total_mortaliy=totom
            frm.refresh_field('total_mortaliy');

            var totom=0
            $.each (frm.doc.laying_mortality, function(i, dt){
                totom+=dt.total; 
            });
            frm.doc.total_laying_mortality=totom
            frm.refresh_field('total_laying_mortality');

        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    date:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_mortality_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        age:d.age,
                        evening:d.evening,
                        morning:d.morning,
                        total:d.total,
                        remark:d.remark
                        
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        d.__unsaved=0;
        frm.doc.__unsaved=0;
        
    },
    remark:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_mortality_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        age:d.age,
                        evening:d.evening,
                        morning:d.morning,
                        total:d.total,
                        remark:d.remark
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        d.__unsaved=0;
        frm.doc.__unsaved=0;
        
    },
    before_rearing_daily_mortality_remove:function(frm, cdt, cdn) {
        
        let row = frappe.get_doc(cdt, cdn);
        if (row.docstatus==1)
        {
            frappe.throw('cannot delete this data, it have associate entry in stock entry please delete stock entry and delete this data');
        }else{
            if(!row.__islocal)
            {
                frappe.call(
                    { 
                            method: "livestock.poultry.doctype.layer_batch.layer_batch.delete_mortality_rearing",
                            args: {                               
                                name:row.name,   
                            },
                            callback: function(r) {  

                                frm.doc.total_mortaliy=frm.doc.total_mortaliy-row.total
                                frm.refresh_field('total_mortaliy');
                                frm.doc.current_alive_chicks=frm.doc.current_alive_chicks+row.total
                                frm.refresh_field('current_alive_chicks');
                              }
                    });
            }
        }
 
    },
    before_laying_mortality_remove:function(frm, cdt, cdn) {
        
        let row = frappe.get_doc(cdt, cdn);
        if (row.docstatus==1)
        {
            frappe.throw('cannot delete this data, it have associate entry in stock entry please delete stock entry and delete this data');
        }else{
            if(!row.__islocal)
            {
                frappe.call(
                    { 
                            method: "livestock.poultry.doctype.layer_batch.layer_batch.delete_mortality_rearing",
                            args: {                               
                                name:row.name,   
                            },
                            callback: function(r) {  if(r.message) 
                                { 
                                    frm.doc.total_laying_mortality=frm.doc.total_laying_mortality-row.total
                                    frm.refresh_field('total_laying_mortality');
                                    frm.doc.current_alive_chicks=frm.doc.current_alive_chicks+row.total
                                    frm.refresh_field('current_alive_chicks');

                                    //var doclist = frappe.model.sync(r.message);
                                    //doclist[0].name
                                }   }
                    });
            }
        }
 
    }
});

//------------------ Temperature --------------------------------

frappe.ui.form.on('Layer Temperature', {
    refresh: function(frm, cdt, cdn) {
        //console.log("ref");
    },
    date:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_temperature_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,                        
                        evening:d.evening,
                        morning:d.morning,                        
                        
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    evening:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_temperature_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        evening:d.evening,
                        morning:d.morning,
                        
                    },
                    callback: function(r) { if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }    }
            });
            

        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    morning:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
       
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_temperature_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        evening:d.evening,
                        morning:d.morning,
                    },
                    callback: function(r) { if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }    }
            });

        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    before_rearing_temperature_remove:function(frm, cdt, cdn) {
        
        let row = frappe.get_doc(cdt, cdn);
        if (row.docstatus==1)
        {
            frappe.throw('cannot delete this data, it have associate entry in stock entry please delete stock entry and delete this data');
        }else{
            if(!row.__islocal)
            {
                frappe.call(
                    { 
                            method: "livestock.poultry.doctype.layer_batch.layer_batch.delete_temperature_rearing",
                            args: {                               
                                name:row.name,   
                            },
                            callback: function(r) {    }
                    });
            }
        }
 
    },
    before_laying_temperature_remove:function(frm, cdt, cdn) {
        
        let row = frappe.get_doc(cdt, cdn);
        if (row.docstatus==1)
        {
            frappe.throw('cannot delete this data, it have associate entry in stock entry please delete stock entry and delete this data');
        }else{
            if(!row.__islocal)
            {
                frappe.call(
                    { 
                            method: "livestock.poultry.doctype.layer_batch.layer_batch.delete_temperature_rearing",
                            args: {                               
                                name:row.name,   
                            },
                            callback: function(r) {    }
                    });
            }
        }
 
    }
});

//------------------ Weight --------------------------------

frappe.ui.form.on('Layer Weight', {
    refresh: function(frm, cdt, cdn) {
        //console.log("ref");
    },
    date:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_weight_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,                        
                        week:d.week,
                        weight:d.weight,                        
                        
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    week:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_weight_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        week:d.week,
                        weight:d.weight,
                        
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
            

        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    weight:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_weight_rearing",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        week:d.week,
                        weight:d.weight,
                    },
                    callback: function(r) { if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }    }
            });

        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    before_rearing_weight_remove:function(frm, cdt, cdn) {
        
        let row = frappe.get_doc(cdt, cdn);
        if (row.docstatus==1)
        {
            frappe.throw('cannot delete this data, it have associate entry in stock entry please delete stock entry and delete this data');
        }else{
            if(!row.__islocal)
            {
                frappe.call(
                    { 
                            method: "livestock.poultry.doctype.layer_batch.layer_batch.delete_weight_rearing",
                            args: {                               
                                name:row.name,   
                            },
                            callback: function(r) {    }
                    });
            }
        }
 
    },
    before_laying_weight_remove:function(frm, cdt, cdn) {
        
        let row = frappe.get_doc(cdt, cdn);
        if (row.docstatus==1)
        {
            frappe.throw('cannot delete this data, it have associate entry in stock entry please delete stock entry and delete this data');
        }else{
            if(!row.__islocal)
            {
                frappe.call(
                    { 
                            method: "livestock.poultry.doctype.layer_batch.layer_batch.delete_weight_rearing",
                            args: {                               
                                name:row.name,   
                            },
                            callback: function(r) {    }
                    });
            }
        }
 
    }
});

//-------------------------------------------------------------------------

//-------------------- Feed ---------------------------
frappe.ui.form.on('Egg Production', {
    refresh: function(frm, cdt, cdn) {
        //console.log("ref");
    },
    qty:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_egg_production",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    uom:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_egg_production",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    item_code:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_egg_production",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        frm.doc.__unsaved=0;
        d.__unsaved=0;
        
    },
    date:function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
            frappe.call(
            { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.update_egg_production",
                    args: {
                        idx:d.idx,
                        parent:d.parent,
                        parentfield:d.parentfield,
                        name:d.name,
                        date:d.date,
                        item_code:d.item_code,
                        qty:d.qty,
                        uom:d.uom
                    },
                    callback: function(r) {  if(r.message) 
                        { 
                            //var doclist = frappe.model.sync(r.message);
                            //doclist[0].name
                        }   }
            });
        d.__unsaved=0;
        frm.doc.__unsaved=0;
        
    },
    before_egg_production_remove:function(frm, cdt, cdn) {
        
        let row = frappe.get_doc(cdt, cdn);
        if (row.docstatus==1)
        {
            frappe.throw('cannot delete this data, it have associate entry in stock entry please delete stock entry and delete this data');
        }else{
            if(!row.__islocal)
            {
                frappe.call(
                    { 
                            method: "livestock.poultry.doctype.layer_batch.layer_batch.delete_egg_production",
                            args: {                               
                                name:row.name,   
                            },
                            callback: function(r) {  if(r.message) 
                                { 
                                    //var doclist = frappe.model.sync(r.message);
                                    //doclist[0].name
                                }   }
                    });
            }
        }
 
    }
});

//--------------------- end feed------------------------------