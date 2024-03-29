// Copyright (c) 2023, alantechnologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Layer Batch', {
	 refresh: function(frm) {
		$(".grid-add-row").hide();
        //frm.get_field("egg_production").grid.df.cannot_delete_rows = true;
        frm.set_query('from_hatchery_project', function(doc, cdt, cdn) {
		  
			return {
			   "filters": {
			"project_type": "Hatchery",
		}
			};
		});

        frm.set_query('rearing_shed', function(doc, cdt, cdn) {
		  
			return {
			   "filters": {
                "company": frm.doc.company,
		}
			};
		});

        frm.set_query('layer_shed', function(doc, cdt, cdn) {
		  
			return {
			   "filters": {
			"company": frm.doc.company,
		}
			};
		});
        $('body').find('[data-fieldtype="Table"]').find('.control-label').css("font-weight", "Bold");
        $('body').find('[data-fieldtype="Table"]').find('.control-label').css("font-size", "16px");
        $('body').find('[data-fieldname="import_items_from_material_transfer_lay"]').find('[data-fieldtype="Button"]').css("background-color",'green');
        $('body').find('[data-fieldname="import_items_from_material_transfer_lay"]').find('[data-fieldtype="Button"]').css("color",'#fff');
        $('body').find('[data-fieldname="import_items_from_material_transfer"]').find('[data-fieldtype="Button"]').css("background-color",'green');
        $('body').find('[data-fieldname="import_items_from_material_transfer"]').find('[data-fieldtype="Button"]').css("color",'#fff');
        
        $('body').find('[data-fieldname="add_egg_production"]').find('[data-fieldtype="Button"]').css("background-color",'#f1ed83');
        $('body').find('[data-fieldname="add_laying_weight"]').find('[data-fieldtype="Button"]').css("background-color",'#f1ed83');
        $('body').find('[data-fieldname="add_laying_temperature"]').find('[data-fieldtype="Button"]').css("background-color",'#f1ed83');
        $('body').find('[data-fieldname="add_laying_mortality"]').find('[data-fieldtype="Button"]').css("background-color",'#f1ed83');
        $('body').find('[data-fieldname="add_laying_items"]').find('[data-fieldtype="Button"]').css("background-color",'#f1ed83');
       // $('body').find('[data-fieldname="add_laying_vaccine"]').find('[data-fieldtype="Button"]').css("background-color",'#f1ed83');
        $('body').find('[data-fieldname="add_laying_medicine"]').find('[data-fieldtype="Button"]').css("background-color",'#f1ed83');
        $('body').find('[data-fieldname="add_laying_feed"]').find('[data-fieldtype="Button"]').css("background-color",'#f1ed83');
        $('body').find('[data-fieldname="add_rearing_weight"]').find('[data-fieldtype="Button"]').css("background-color",'#f1ed83');
        $('body').find('[data-fieldname="add_rearing_temperature"]').find('[data-fieldtype="Button"]').css("background-color",'#f1ed83');
        $('body').find('[data-fieldname="add_rearing_mortality"]').find('[data-fieldtype="Button"]').css("background-color",'#f1ed83');
        $('body').find('[data-fieldname="add_rearing_items"]').find('[data-fieldtype="Button"]').css("background-color",'#f1ed83');
       // $('body').find('[data-fieldname="add_rearing_vaccine"]').find('[data-fieldtype="Button"]').css("background-color",'#f1ed83');
        $('body').find('[data-fieldname="add_rearing_medicine"]').find('[data-fieldtype="Button"]').css("background-color",'#f1ed83');
        $('body').find('[data-fieldname="add_rearing_feed"]').find('[data-fieldtype="Button"]').css("background-color",'#f1ed83');
        
                
        $('body').find('[data-fieldname="issue_laying_items"]').find('[data-fieldtype="Button"]').css("background-color",'#98cafd');
       // $('body').find('[data-fieldname="issue_laying_vaccine"]').find('[data-fieldtype="Button"]').css("background-color",'#98cafd');
        $('body').find('[data-fieldname="issue_laying_medicine"]').find('[data-fieldtype="Button"]').css("background-color",'#98cafd');
        $('body').find('[data-fieldname="issue_laying_feed"]').find('[data-fieldtype="Button"]').css("background-color",'#98cafd');
        //frm.fields_dict["rearing_feed"].grid.wrapper.find(".btn-open-row").hide();

        $('body').find('[data-fieldname="issue_rearing_items"]').find('[data-fieldtype="Button"]').css("background-color",'#98cafd');
        $('body').find('[data-fieldname="issue_rearing_medicine"]').find('[data-fieldtype="Button"]').css("background-color",'#98cafd');
        $('body').find('[data-fieldname="issue_rearing_feed"]').find('[data-fieldtype="Button"]').css("background-color",'#98cafd');
        $('body').find('[data-fieldname="issue_rearing_mortality"]').find('[data-fieldtype="Button"]').css("background-color",'#98cafd');

        if(frm.doc.item_processed > 0 )
        {
            
            frm.get_field("rearing_feed").grid.df.cannot_delete_rows = true;
            frm.get_field("rearing_items").grid.df.cannot_delete_rows = true;
            //frm.get_field("rearing_vaccine").grid.df.cannot_delete_rows = true;
            frm.get_field("rearing_medicine").grid.df.cannot_delete_rows = true;
            frm.get_field("rearing_temperature").grid.df.cannot_delete_rows = true;
            frm.get_field("rearing_weight").grid.df.cannot_delete_rows = true;
            frm.get_field("rearing_daily_mortality").grid.df.cannot_delete_rows = true;
        }else{
            frm.fields_dict['rearing_feed'].grid.wrapper.on('change', 'input[type="checkbox"]', function(e) {
                $(".grid-add-row").hide();
                $(".grid-remove-rows").hide();
            });
    
            frm.fields_dict['rearing_medicine'].grid.wrapper.on('change', 'input[type="checkbox"]', function(e) {
                $(".grid-add-row").hide();
                $(".grid-remove-rows").hide();
            });
    
            /*frm.fields_dict['rearing_vaccine'].grid.wrapper.on('change', 'input[type="checkbox"]', function(e) {
                $(".grid-add-row").hide();
                $(".grid-remove-rows").hide();
            });*/
    
            frm.fields_dict['rearing_items'].grid.wrapper.on('change', 'input[type="checkbox"]', function(e) {
                $(".grid-add-row").hide();
                $(".grid-remove-rows").hide();
            });
    
            frm.fields_dict['rearing_daily_mortality'].grid.wrapper.on('change', 'input[type="checkbox"]', function(e) {
                $(".grid-add-row").hide();
                $(".grid-remove-rows").hide();
            });
    
            frm.fields_dict['rearing_temperature'].grid.wrapper.on('change', 'input[type="checkbox"]', function(e) {
                $(".grid-add-row").hide();
                $(".grid-remove-rows").hide();
            });
    
            frm.fields_dict['rearing_weight'].grid.wrapper.on('change', 'input[type="checkbox"]', function(e) {
                $(".grid-add-row").hide();
                $(".grid-remove-rows").hide();
            });
        }
        frm.fields_dict['egg_production'].grid.wrapper.on('change', 'input[type="checkbox"]', function(e) {
            $(".grid-add-row").hide();
			$(".grid-remove-rows").hide();
        });

        frm.fields_dict['laying_feed'].grid.wrapper.on('change', 'input[type="checkbox"]', function(e) {
            $(".grid-add-row").hide();
			$(".grid-remove-rows").hide();
        });

        frm.fields_dict['laying_medicine'].grid.wrapper.on('change', 'input[type="checkbox"]', function(e) {
            $(".grid-add-row").hide();
			$(".grid-remove-rows").hide();
        });

       /* frm.fields_dict['laying_vaccine'].grid.wrapper.on('change', 'input[type="checkbox"]', function(e) {
            $(".grid-add-row").hide();
			$(".grid-remove-rows").hide();
        }); */

        frm.fields_dict['laying_items'].grid.wrapper.on('change', 'input[type="checkbox"]', function(e) {
            $(".grid-add-row").hide();
			$(".grid-remove-rows").hide();
        });

        frm.fields_dict['laying_mortality'].grid.wrapper.on('change', 'input[type="checkbox"]', function(e) {
            $(".grid-add-row").hide();
			$(".grid-remove-rows").hide();
        });

        frm.fields_dict['laying_temperature'].grid.wrapper.on('change', 'input[type="checkbox"]', function(e) {
            $(".grid-add-row").hide();
			$(".grid-remove-rows").hide();
        });

        frm.fields_dict['laying_weight'].grid.wrapper.on('change', 'input[type="checkbox"]', function(e) {
            $(".grid-add-row").hide();
			$(".grid-remove-rows").hide();
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


        frm.doc.current_alive_chicks=frm.doc.doc_placed-frm.doc.total_laying_mortality-frm.doc.total_mortaliy-frm.doc.sales_qty
        frm.refresh_field('current_alive_chicks');

        //====================================================
        //frm.doc.egg_category
        if (frm.doc.item_processed==0)
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
                                                   // var doclist = frappe.model.sync(r.message);
                                                    frm.doc.item_processed=1;
                                                    frm.refresh_field('item_processed');                                                    
                                                    frm.reload_doc(); 
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

              
				frm.add_custom_button(__('Create Sales Invoice'), function(){
            
                    
                        
                        frappe.prompt(
                            [
                            {  fieldtype: "Link",
                                label: __("Item"),
                                fieldname: "item",
                                options:"Item",
                                reqd:'1',
                                get_query() {
                                    return {
                                        filters: { item_code:['in',['LY00001','LY00002','MAN001']] }
                                    }
                                },                                
                            },
                            {  fieldtype: "Int",
                                label: __("Sales Quantity"),
                                fieldname: "transfer_qty",
                                reqd:'1'                                
                            },                            
                            {  fieldtype: "Date",
                            label: __("Invoice Date"),
                            fieldname: "transfer_date",
                            reqd:'1'                                
                            }
                            ],
                            function(data) {
                                
                                frappe.call(
                                    { 
                                        method: "livestock.poultry.doctype.layer_batch.layer_batch.sales_entry",
                                        args: {
                                            batch:frm.doc.name,
                                            item:data.item,                                            
                                            transfer_qty:data.transfer_qty,
                                            transfer_date:data.transfer_date,                                            
                                        },
                                        callback: function(r) 
                                            { 
                                                if(r.message) 
                                                    { 
                                                        var doclist = frappe.model.sync(r.message);
                                                        frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
                                                    } 
                                            }
                                    });
                            },
                            __("Create Sales Invoice"),
                            __("Confirm")
                        );       
                //console.log(frm.doc);  
                    
               
                    }).removeClass("btn-default").addClass("btn-success");
			
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
        //frm.doc.current_alive_chicks=frm.doc.doc_placed-frm.doc.total_laying_mortality
        //frm.refresh_field('current_alive_chicks');
        //console.log("mortalil");
     },
     total_mortaliy:function(frm)
     {
        //frm.doc.current_alive_chicks=frm.doc.doc_placed-frm.doc.total_mortaliy
        //frm.refresh_field('current_alive_chicks');
        //console.log("mortali");
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
                     fieldtype: 'Float',
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
                                        let rw=frm.add_child("rearing_feed");
                                        rw.date=values.date;
                                        rw.item_code=values.item_code;
                                        rw.qty=values.qty;
                                        rw.uom=values.uom;                                                
                                        rw.rate=r.message.rate;
                                        rw.conversion_factor=r.message.conversion_factor;
                                        rw.item_name=r.message.item_name;
                                        rw.issue='Yes';
                                        rw.docstatus=1; 
                                        frm.refresh_field('rearing_feed');
                                        frm.doc.__unsaved=0;
                                        d.hide();
                                        $(".grid-add-row").hide();
                                     } 
                             }
                     });

             }
         });
         
         d.show();
         d.$wrapper.find("[data-fieldname='item_code']").on('focusout',function(e) {
            let v=$(this).val();                                            
             if (v){
             frappe.db.get_value('Item', v, 'stock_uom')
                     .then(r => {
                         
                         d.$wrapper.find("[data-fieldname='uom']").val(r.message.stock_uom); 
                         
                     });
                 }
         });
         
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
                            fieldtype: 'Float',
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
                                                let rw=frm.add_child("laying_feed");
                                                rw.date=values.date;
                                                rw.item_code=values.item_code;
                                                rw.qty=values.qty;
                                                rw.uom=values.uom;                                                
                                                rw.rate=r.message.rate;
                                                rw.conversion_factor=r.message.conversion_factor;
                                                rw.item_name=r.message.item_name;
                                                rw.issue='Yes';
                                                rw.docstatus=1;
                                                frm.refresh_field('laying_feed');
                                                frm.doc.__unsaved=0;
                                                d.hide();
                                                $(".grid-add-row").hide();
                                                //frm.reload_doc();
                                            }
                                    }
                            });

                    }
                });
                
                d.show();
                d.$wrapper.find("[data-fieldname='item_code']").on('focusout',function(e) {
                    let v=$(this).val();                                            
                     if (v){
                     frappe.db.get_value('Item', v, 'stock_uom')
                             .then(r => {
                                 
                                 d.$wrapper.find("[data-fieldname='uom']").val(r.message.stock_uom); 
                                 
                             });
                         }
                 });
                
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
                            fieldtype: 'Float',
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
                                                let rw=frm.add_child("rearing_medicine");
                                                rw.date=values.date;
                                                rw.item_code=values.item_code;
                                                rw.qty=values.qty;
                                                rw.uom=values.uom;
                                                rw.remark=values.remark;                                                
                                                rw.rate=r.message.rate;
                                                rw.conversion_factor=r.message.conversion_factor;
                                                rw.item_name=r.message.item_name;
                                                rw.issue='Yes';
                                                rw.docstatus=1; 
                                                frm.refresh_field('rearing_medicine');
                                                d.hide();
                                                $(".grid-add-row").hide();
                                                frm.doc.__unsaved=0;
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                d.$wrapper.find("[data-fieldname='item_code']").on('focusout',function(e) {
                    let v=$(this).val();                                            
                     if (v){
                     frappe.db.get_value('Item', v, 'stock_uom')
                             .then(r => {
                                 
                                 d.$wrapper.find("[data-fieldname='uom']").val(r.message.stock_uom); 
                                 
                             });
                         }
                 });
                
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
                            fieldtype: 'Float',
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

                                                let rw=frm.add_child("laying_medicine");
                                                rw.date=values.date;
                                                rw.item_code=values.item_code;
                                                rw.qty=values.qty;
                                                rw.uom=values.uom;
                                                rw.remark=values.remark;                                                
                                                rw.rate=r.message.rate;
                                                rw.conversion_factor=r.message.conversion_factor;
                                                rw.item_name=r.message.item_name;
                                                rw.issue='Yes';
                                                rw.docstatus=1; 
                                                frm.refresh_field('laying_medicine');
                                                d.hide();
                                                $(".grid-add-row").hide();
                                                frm.doc.__unsaved=0;
                                                //frm.reload_doc();
                                                
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                d.$wrapper.find("[data-fieldname='item_code']").on('focusout',function(e) {
                    let v=$(this).val();                                            
                     if (v){
                     frappe.db.get_value('Item', v, 'stock_uom')
                             .then(r => {
                                 
                                 d.$wrapper.find("[data-fieldname='uom']").val(r.message.stock_uom); 
                                 
                             });
                         }
                 });
                
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
                            fieldtype: 'Float',
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
                                                let rw=frm.add_child("rearing_items");
                                                rw.date=values.date;
                                                rw.item_code=values.item_code;
                                                rw.qty=values.qty;
                                                rw.uom=values.uom;				
                                               
                                                rw.rate=r.message.rate;
                                                rw.conversion_factor=r.message.conversion_factor;
                                                rw.item_name=r.message.item_name;
                                                rw.issue='Yes';
                                                rw.docstatus=1; 
                                                frm.refresh_field('rearing_items');
                                                d.hide();
                                                $(".grid-add-row").hide();
                                                frm.doc.__unsaved=0;
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                d.$wrapper.find("[data-fieldname='item_code']").on('focusout',function(e) {
                    let v=$(this).val();                                            
                     if (v){
                     frappe.db.get_value('Item', v, 'stock_uom')
                             .then(r => {
                                 
                                 d.$wrapper.find("[data-fieldname='uom']").val(r.message.stock_uom); 
                                 
                             });
                         }
                 });
                
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
                            fieldtype: 'Float',
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
                                                let rw=frm.add_child("laying_items");
                                                rw.date=values.date;
                                                rw.item_code=values.item_code;
                                                rw.qty=values.qty;
                                                rw.uom=values.uom;				
                                               
                                                rw.rate=r.message.rate;
                                                rw.conversion_factor=r.message.conversion_factor;
                                                rw.item_name=r.message.item_name;
                                                rw.issue='Yes';
                                                rw.docstatus=1; 
                                                frm.refresh_field('laying_items');
                                                d.hide();
                                                $(".grid-add-row").hide();
                                                frm.doc.__unsaved=0;
                                                //frm.reload_doc();
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                d.$wrapper.find("[data-fieldname='item_code']").on('focusout',function(e) {
                    let v=$(this).val();                                            
                     if (v){
                     frappe.db.get_value('Item', v, 'stock_uom')
                             .then(r => {
                                 
                                 d.$wrapper.find("[data-fieldname='uom']").val(r.message.stock_uom); 
                                 
                             });
                         }
                 });
                
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
                                                let rw=frm.add_child("rearing_daily_mortality");
                                                rw.date=values.date;
                                                rw.age=values.age;
                                                rw.evening=values.evening;
                                                rw.morning=values.morning;
                                                rw.total=values.evening+values.morning;
                                                rw.remark=values.remark;
                                                rw.issue='Yes';
                                                rw.docstatus=1;
                                                frm.refresh_field('rearing_daily_mortality');
                                                d.hide();
                                                $(".grid-add-row").hide();
                                                frm.doc.__unsaved=0;
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                d.$wrapper.find("[data-fieldname='date']").on('change',function() {
                    let v=$(this).val();
                    if(v && frm.doc.doc_placed_date)
                    {
                        var dtar=v.split('-');
                        var dt=dtar[2]+'-'+dtar[1]+'-'+dtar[0]
                        var date1, date2;  
                        date1 = new Date(frm.doc.doc_placed_date);  
                        date2 = new Date(dt);
                        var time_difference = date2.getTime() - date1.getTime();  
                        var days_difference = Math.ceil(time_difference / (1000 * 60 * 60 * 24))+1;
                        d.$wrapper.find("[data-fieldname='age']").val(days_difference);
                    }
                    
                    
                });

                
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
                                                let rw=frm.add_child("laying_mortality");
                                                rw.date=values.date;
                                                rw.age=values.age;
                                                rw.evening=values.evening;
                                                rw.morning=values.morning;
                                                rw.total=values.evening+values.morning;
                                                rw.remark=values.remark;
                                                rw.issue='Yes';
                                                rw.docstatus=1;
                                                frm.refresh_field('laying_mortality');
                                                d.hide();
                                                $(".grid-add-row").hide();
                                                frm.doc.__unsaved=0;
                                                //frm.reload_doc()
                                            } 
                                    }
                            });

                    }
                });
                
                d.show();
                d.$wrapper.find("[data-fieldname='date']").on('change',function() {
                    let v=$(this).val();
                    if(v && frm.doc.doc_placed_date)
                    {
                        var dtar=v.split('-');
                        var dt=dtar[2]+'-'+dtar[1]+'-'+dtar[0]
                        var date1, date2;  
                        date1 = new Date(frm.doc.doc_placed_date);  
                        date2 = new Date(dt);
                        var time_difference = date2.getTime() - date1.getTime();  
                        var days_difference = Math.ceil(time_difference / (1000 * 60 * 60 * 24))+1;
                        d.$wrapper.find("[data-fieldname='age']").val(days_difference);
                    }
                    
                    
                });
                
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
                d.$wrapper.find("[data-fieldname='date']").on('change',function() {
                    let v=$(this).val();
                    if(v && frm.doc.doc_placed_date)
                    {
                        var dtar=v.split('-');
                        var dt=dtar[2]+'-'+dtar[1]+'-'+dtar[0]
                        var date1, date2;  
                        date1 = new Date(frm.doc.doc_placed_date);  
                        date2 = new Date(dt);
                        var time_difference = date2.getTime() - date1.getTime();  
                        var week_difference = Math.floor((Math.ceil(time_difference / (1000 * 60 * 60 * 24))+1)/7);
                        d.$wrapper.find("[data-fieldname='week']").val(week_difference);
                    }
                    
                    
                });
                
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
                d.$wrapper.find("[data-fieldname='date']").on('change',function() {
                    let v=$(this).val();
                    if(v && frm.doc.doc_placed_date)
                    {
                        var dtar=v.split('-');
                        var dt=dtar[2]+'-'+dtar[1]+'-'+dtar[0]
                        var date1, date2;  
                        date1 = new Date(frm.doc.doc_placed_date);  
                        date2 = new Date(dt);
                        var time_difference = date2.getTime() - date1.getTime();  
                        var week_difference = Math.floor((Math.ceil(time_difference / (1000 * 60 * 60 * 24))+1)/7);
                        d.$wrapper.find("[data-fieldname='week']").val(week_difference);
                    }
                    
                    
                });
                
            },
            add_egg_production:function(frm)
            {

            var prompt_fields=[{  fieldtype: "Date",
            label: __("Date"),
            fieldname: "date",
            reqd:'1',
            default:frappe.datetime.get_today(),                                
            },
            {  fieldtype: "Column Break",
                fieldname: "lblcolbk_00",                                                               
            },
            {  fieldtype: "Time",
            label: __("Time"),
            fieldname: "time",
            reqd:'1',
            default:frappe.datetime.get_today(),                                
            },
            {'fieldname': 'sec_top', 'fieldtype': 'Section Break'},
            //{'fieldname': 'ht', 'fieldtype': 'HTML'},Column Break Section Break
            
            ];

            frappe.call(
                { 
                    method: "livestock.poultry.doctype.layer_batch.layer_batch.get_egg_products",
                    args: {
                        cat:frm.doc.batch_type
                    },
                    callback: function(r) 
                        { 
                            if(r.message) 
                                { 
                                    
                                   var res=r.message
                                    for(var i=0;i<res.length;i++)
                                    {
                                        let itm=res[i];
                                        
                                        prompt_fields.push({  fieldtype: "HTML",
                                        fieldname:itm.item_code+'_'+i,                                                         
                                        });

                                        
                                        prompt_fields.push({  fieldtype: "Column Break",
                                        fieldname: "colbku_"+itm.item_code+"_"+i,                                                               
                                        });

                                        if(itm.default_bom){
                                            prompt_fields.push({  fieldtype: "Link",
                                            label: 'Finished Item BOM',
                                            fieldname: "bom_"+itm.item_code+"_"+i,
                                            default:itm.default_bom,
                                            options:'Finished Product BOM',                                
                                            });
                                        }else{

                                            prompt_fields.push({  fieldtype: "Link",
                                            label: 'Finished Item BOM',
                                            fieldname: "bom_"+itm.item_code+"_"+i,                                            
                                            options:'Finished Product BOM',                                
                                            });
                                        }

                                        prompt_fields.push({  fieldtype: "Column Break",
                                        fieldname: "colbk_"+itm.item_code+"_"+i,                                                               
                                        });

                                        prompt_fields.push({
                                        fetch_from:"bom_"+itm.item_code+"_"+i+".uom",  
                                        fieldtype: "Data",
                                        label: ' Uom',
                                        fieldname: "uom_"+itm.item_code+"_"+i,
                                        default:itm.default_uom,                                      
                                                                      
                                        });
                                            
                                        prompt_fields.push({  fieldtype: "Column Break",
                                        fieldname: "lblcolbk_"+itm.item_code+"_"+i,                                                               
                                        });

                                        prompt_fields.push({  fieldtype: "Float",
                                        label:'Qty',
                                        fieldname: "qty_"+itm.item_code+"_"+i,
                                        default:'0',                                
                                        });

                                        prompt_fields.push({  fieldtype: "Section Break",
                                        fieldname: "secbk_"+itm.item_code+"_"+i,                                                                     
                                        });
                                       

                                    }

                                    let d = new frappe.ui.Dialog({
                                        title: 'Add Egg',
                                        fields: prompt_fields,
                                        primary_action_label: 'Add Egg',
                                        columns: 2, 
                                        primary_action(values) {
                                            
                                            let item_post=[];
                                            for (const [key, value] of Object.entries(values)) {
                                                if(key!='date')
                                                {
                                                    //console.log(key, value);
                                                    const item_ar = key.split("_");
                                                    if (item_ar[0]=='qty' && value > 0 )
                                                    {                                                   
                                                        let rw=frm.add_child("egg_production");
                                                        rw.date=values.date;
                                                        rw.item_code=item_ar[1];
                                                        rw.qty=value;
                                                        rw.uom=values['uom_'+item_ar[1]+'_'+item_ar[2]];
                                                        rw.bom=values['bom_'+item_ar[1]+'_'+item_ar[2]];
                                                        frm.refresh_field('egg_production');
                                                        d.hide();
                                                        $(".grid-add-row").hide();
                                                        frm.doc.__unsaved=0; 
                                                        item_post.push({'date':values.date,'item_code':item_ar[1],'qty':value,'uom':rw.uom,'bom':rw.bom});
                                                    }
                                                            
                                                }
                                                
                                              }
                                            
                                             //---------------------------------------
                                             let itemss=JSON.stringify(item_post);
                                             frappe.call(
                                                { 
                                                    method: "livestock.poultry.doctype.layer_batch.layer_batch.add_eggs_production",
                                                    args: {
                                                        batch:frm.doc.name,
                                                        parentfield:'egg_production',
                                                        items:itemss,
                                                        production_date:values.date,
                                                        production_time:values.time,                                                                
                                                    },
                                                    callback: function(rs) 
                                                        { 
                                                            if(rs.message) 
                                                                { 
                                                                    //rw.rate=rs.message.rate;
                                                                    //rw.conversion_factor=rs.message.conversion_factor;
                                                                    //rw.item_name=rs.message.item_name;
                                                                    //frm.refresh_field('egg_production');
                                                                    //var doclist = frappe.model.sync(r.message);
                                                                    //doclist[0].name
                                                                    //var doclist = frappe.model.sync(rs.message);
                                                                    //frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
                                                                    //frm.reload_doc();
                                                                } 
                                                        }
                                                }); 
                                             //---------------------------------------   
                                        }
                                    });
                                    
                                    
                                    for(var i=0;i< res.length;i++)
                                    {
                                        let itm=res[i];
                                        let nm=itm.item_code+'_'+i;
                                        d.fields_dict[nm].$wrapper.html('<b>'+itm.item_code+': '+itm.item_name+'</b>');

                                        let bomfield="bom_"+itm.item_code+"_"+i
                                        d.fields_dict[bomfield].get_query = function(){
                                            return {
                                                    filters:{
                                                            "item": itm.item_code
                                                    }
                                            }
                                        }
                                       
                                    }
                                    
                                    d.show();
                                    d.$wrapper.find('.modal-content').css("width", "800px");
                                    d.$wrapper.find('.row').css("padding-bottom", "0px");
                                    d.$wrapper.find("[data-fieldname='date']").css("width", "150px");
                                    d.$wrapper.find("[data-fieldname='time']").css("width", "150px");
                                    for(var i=0;i< res.length;i++)
                                    {
                                        let itm=res[i];                                        
                                        let bomfield="bom_"+itm.item_code+"_"+i;
                                        var uomfield="uom_"+itm.item_code+"_"+i;
                                        
                                        d.$wrapper.find("[data-fieldname='"+bomfield+"']").on('focusout',function(e) {
                                           let v=$(this).val();
                                            //console.log("hai"+v);
                                            if (v){
                                            frappe.db.get_value('Finished Product BOM', v, 'uom')
                                                    .then(r => {
                                                        //console.log(r.message.uom);
                                                        d.$wrapper.find("[data-fieldname='"+uomfield+"']").val(r.message.uom); 
                                                        
                                                    });
                                                }
                                        });

                                       
                                    }
                                } 
                        }
                });

                
                
            },
            import_items_from_material_transfer:function(frm)
            {
                let d = new frappe.ui.Dialog({
                    title: 'Import Items From Material Transfer',
                    fields: [                        
                        {
                            label: 'Material Transfer',
                            fieldname: 'stock_entry',
                            fieldtype: 'Link',
                            options:'Stock Entry',
                            reqd:'1'
                        }
                    ],
                    primary_action_label: 'Import Items',
                    primary_action(values) {                        
                        
                        frappe.call(
                            { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.get_material_transfer",
                                args: {
                                    material_transfer:values.stock_entry,
                                    project:frm.doc.project,
                                    shed:frm.doc.rearing_shed,
                                },
                                callback: function(r) 
                                    { 
                                        var flg=0;
                                        if(r.message.length > 0 ) 
                                            { 
                                                d.hide();
                                                $.each (r.message,function(i, dt){
                                                   /* if(dt.tbl=='vaccine')
                                                    {
                                                        let rw=frm.add_child("rearing_vaccine");
                                                        rw.date=dt.date;
                                                        rw.item_code=dt.item_code;
                                                        rw.qty=dt.qty;
                                                        rw.uom=dt.uom;
                                                        rw.rate=dt.basic_rate;
                                                        rw.conversion_factor=dt.conversion_factor;
                                                        rw.item_name=dt.item_name;
                                                        rw.material_transfer=dt.material_transfer;
                                                        frm.refresh_field('rearing_vaccine');                                                
                                                        $(".grid-add-row").hide();
                                                        frm.doc.__unsaved=0;
                                                        flg=1;
                                                    }*/
                                                    if(dt.tbl=='medicine')
                                                    {
                                                        let rw=frm.add_child("rearing_medicine");
                                                        rw.date=dt.date;
                                                        rw.item_code=dt.item_code;
                                                        rw.qty=dt.qty;
                                                        rw.uom=dt.uom;
                                                        rw.rate=dt.basic_rate;
                                                        rw.conversion_factor=dt.conversion_factor;
                                                        rw.item_name=dt.item_name;
                                                        rw.material_transfer=dt.material_transfer;
                                                        frm.refresh_field('rearing_medicine');                                                
                                                        $(".grid-add-row").hide();
                                                        frm.doc.__unsaved=0;
                                                        flg=1;
                                                    }
                                                    if(dt.tbl=='item')
                                                    {
                                                        let rw=frm.add_child("rearing_items");
                                                        rw.date=dt.date;
                                                        rw.item_code=dt.item_code;
                                                        rw.qty=dt.qty;
                                                        rw.uom=dt.uom;
                                                        rw.rate=dt.basic_rate;
                                                        rw.conversion_factor=dt.conversion_factor;
                                                        rw.item_name=dt.item_name;
                                                        rw.material_transfer=dt.material_transfer;
                                                        frm.refresh_field('rearing_items');                                                
                                                        $(".grid-add-row").hide();
                                                        frm.doc.__unsaved=0;
                                                        flg=1;
                                                    }
                                                    if(dt.tbl=='feed')
                                                    {
                                                        let rw=frm.add_child("rearing_feed");
                                                        rw.date=dt.date;
                                                        rw.item_code=dt.item_code;
                                                        rw.qty=dt.qty;
                                                        rw.uom=dt.uom;
                                                        rw.rate=dt.basic_rate;
                                                        rw.conversion_factor=dt.conversion_factor;
                                                        rw.item_name=dt.item_name;
                                                        rw.material_transfer=dt.material_transfer;
                                                        frm.refresh_field('rearing_feed');                                                
                                                        $(".grid-add-row").hide();
                                                        frm.doc.__unsaved=0;
                                                        flg=1;
                                                    } 
                                                });

                                                if(flg==0)
                                                {
                                                   
                                                    frappe.throw('Items are not in corresponding warehouses or it is already added');
                                                }
                                                
                                            } else{
                                                d.hide();
                                                frappe.throw('Items are not in corresponding warehouses or it is already added');
                                            }
                                    }
                            });
       
                    }
                });
                d.fields_dict['stock_entry'].get_query = function(){
                    return {
                            filters:{
                                    "stock_entry_type": 'Material Transfer',
                                    "docstatus":'1',
                                    "company":frm.doc.company
                            }
                    }
                }
                d.show();
            },
            import_items_from_material_transfer_lay:function(frm)
            {
                let d = new frappe.ui.Dialog({
                    title: 'Import Items From Material Transfer',
                    fields: [                        
                        {
                            label: 'Material Transfer',
                            fieldname: 'stock_entry',
                            fieldtype: 'Link',
                            options:'Stock Entry',
                            reqd:'1'
                        }
                    ],
                    primary_action_label: 'Import Items',
                    primary_action(values) {                        
                        
                        frappe.call(
                            { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.get_material_transfer_lay",
                                args: {
                                    material_transfer:values.stock_entry,
                                    project:frm.doc.project,
                                    shed:frm.doc.layer_shed,
                                },
                                callback: function(r) 
                                    { 
                                        var flg=0;
                                        if(r.message.length > 0 ) 
                                            { 
                                                d.hide();
                                                $.each (r.message,function(i, dt){
                                                   
                                                    if(dt.tbl=='medicine')
                                                    {
                                                        let rw=frm.add_child("laying_medicine");
                                                        rw.date=dt.date;
                                                        rw.item_code=dt.item_code;
                                                        rw.qty=dt.qty;
                                                        rw.uom=dt.uom;
                                                        rw.rate=dt.basic_rate;
                                                        rw.conversion_factor=dt.conversion_factor;
                                                        rw.item_name=dt.item_name;
                                                        rw.material_transfer=dt.material_transfer;
                                                        frm.refresh_field('laying_medicine');                                                
                                                        $(".grid-add-row").hide();
                                                        frm.doc.__unsaved=0;
                                                        flg=1;
                                                    }
                                                    if(dt.tbl=='item')
                                                    {
                                                        let rw=frm.add_child("laying_items");
                                                        rw.date=dt.date;
                                                        rw.item_code=dt.item_code;
                                                        rw.qty=dt.qty;
                                                        rw.uom=dt.uom;
                                                        rw.rate=dt.basic_rate;
                                                        rw.conversion_factor=dt.conversion_factor;
                                                        rw.item_name=dt.item_name;
                                                        rw.material_transfer=dt.material_transfer;
                                                        frm.refresh_field('laying_items');                                                
                                                        $(".grid-add-row").hide();
                                                        frm.doc.__unsaved=0;
                                                        flg=1;
                                                    }
                                                    if(dt.tbl=='feed')
                                                    {
                                                        let rw=frm.add_child("laying_feed");
                                                        rw.date=dt.date;
                                                        rw.item_code=dt.item_code;
                                                        rw.qty=dt.qty;
                                                        rw.uom=dt.uom;
                                                        rw.rate=dt.basic_rate;
                                                        rw.conversion_factor=dt.conversion_factor;
                                                        rw.item_name=dt.item_name;
                                                        rw.material_transfer=dt.material_transfer;
                                                        frm.refresh_field('laying_feed');                                                
                                                        $(".grid-add-row").hide();
                                                        frm.doc.__unsaved=0;
                                                        flg=1;
                                                    } 
                                                });

                                                if(flg==0)
                                                {
                                                   
                                                    frappe.throw('Items are not in corresponding warehouses or it is already added');
                                                }
                                                
                                            } else{
                                                d.hide();
                                                frappe.throw('Items are not in corresponding warehouses or it is already added');
                                            }
                                    }
                            });
       
                    }
                });
                d.fields_dict['stock_entry'].get_query = function(){
                    return {
                            filters:{
                                    "stock_entry_type": 'Material Transfer',
                                    "docstatus":'1',
                                    "company":frm.doc.company
                            }
                    }
                }
                d.show();
            },
            issue_laying_feed:function(frm){
                let items=[]
                let selected = frm.get_selected();
                    if(selected.laying_feed){
                        selected.laying_feed.forEach(function(item, index, array) {
                            let row = locals['Layer Feed'][item];
                            if(row.issue!='Yes' && row.docstatus==0){
                                items.push(row);
                            }
                        });
                    }else{
                        frappe.throw("Please select items to Issue");
                    }
                    
               
                if(items.length>0){
                    let itemss=JSON.stringify(items);

                    frappe.call(
                        { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.laying_material_issue",
                                args: {
                                    batch:frm.doc.batch_name,
                                    parentfield:'laying_feed',
                                    items:itemss
                                },
                                callback: function(r) {  
                                    if(r.message) 
                                    {  
                                        $.each(r.message, function(i, rows) {                                            
                                            let row = locals[rows.doctype][rows.name];
                                            row.docstatus=1;
                                            row.issue='Yes';
                                            row.stock_entry=rows.stock_entry
                                        });
                                        //frm.reload_doc();
                                        frm.refresh_field('laying_feed');
                                    }   
                                }
                        });

                }else{
                    frappe.throw("Please select not issued items for Issuing");
                }
                
            },
            issue_laying_medicine:function(frm){
                let items=[]
                let selected = frm.get_selected();
                    if(selected.laying_medicine){
                        selected.laying_medicine.forEach(function(item, index, array) {
                            let row = locals['Layer Medicine'][item];
                            if(row.issue!='Yes' && row.docstatus==0){
                                items.push(row);
                            }
                        });
                    }else{
                        frappe.throw("Please select items to Issue");
                    }
                    
               
                if(items.length>0){
                    let itemss=JSON.stringify(items);

                    frappe.call(
                        { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.laying_material_issue",
                                args: {
                                    batch:frm.doc.batch_name,
                                    parentfield:'laying_medicine',
                                    items:itemss
                                },
                                callback: function(r) {  
                                    if(r.message) 
                                    {  
                                        $.each(r.message, function(i, rows) {                                            
                                            let row = locals[rows.doctype][rows.name];
                                            row.docstatus=1;
                                            row.issue='Yes';
                                            row.stock_entry=rows.stock_entry
                                        });
                                        //frm.reload_doc();
                                        frm.refresh_field('laying_medicine');
                                    }   
                                }
                        });

                }else{
                    frappe.throw("Please select not issued items for Issuing");
                }
            },
	       
	        issue_laying_items:function(frm){
                let items=[]
                let selected = frm.get_selected();
                    if(selected.laying_items){
                        selected.laying_items.forEach(function(item, index, array) {
                            let row = locals['Layer Other Items'][item];
                            if(row.issue!='Yes' && row.docstatus==0){
                                items.push(row);
                            }
                        });
                    }else{
                        frappe.throw("Please select items to Issue");
                    }
                    
               
                if(items.length>0){
                    let itemss=JSON.stringify(items);

                    frappe.call(
                        { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.laying_material_issue",
                                args: {
                                    batch:frm.doc.batch_name,
                                    parentfield:'laying_items',
                                    items:itemss
                                },
                                callback: function(r) {  
                                    if(r.message) 
                                    {  
                                        $.each(r.message, function(i, rows) {                                            
                                            let row = locals[rows.doctype][rows.name];
                                            row.docstatus=1;
                                            row.issue='Yes';
                                            row.stock_entry=rows.stock_entry
                                        });
                                        //frm.reload_doc();
                                        frm.refresh_field('laying_items');
                                    }   
                                }
                        });

                }else{
                    frappe.throw("Please select not issued items for Issuing");
                }
            },
            issue_rearing_feed:function(frm){
                let items=[]
                let selected = frm.get_selected();
                    if(selected.rearing_feed){
                        selected.rearing_feed.forEach(function(item, index, array) {
                            let row = locals['Layer Feed'][item];
                            if(row.issue!='Yes' && row.docstatus==0){
                                items.push(row);
                            }
                        });
                    }else{
                        frappe.throw("Please select items to Issue");
                    }
                    
               
                if(items.length>0){
                    let itemss=JSON.stringify(items);

                    frappe.call(
                        { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.laying_material_issue",
                                args: {
                                    batch:frm.doc.batch_name,
                                    parentfield:'rearing_feed',
                                    items:itemss
                                },
                                callback: function(r) {  
                                    if(r.message) 
                                    {  
                                        $.each(r.message, function(i, rows) {                                            
                                            let row = locals[rows.doctype][rows.name];
                                            row.docstatus=1;
                                            row.issue='Yes';
                                            row.stock_entry=rows.stock_entry
                                        });
                                        //frm.reload_doc();
                                        frm.refresh_field('rearing_feed');
                                    }   
                                }
                        });

                }else{
                    frappe.throw("Please select not issued items for Issuing");
                }
                
            },
            issue_rearing_medicine:function(frm){
                let items=[]
                let selected = frm.get_selected();
                    if(selected.rearing_medicine){
                        selected.rearing_medicine.forEach(function(item, index, array) {
                            let row = locals['Layer Medicine'][item];
                            if(row.issue!='Yes' && row.docstatus==0){
                                items.push(row);
                            }
                        });
                    }else{
                        frappe.throw("Please select items to Issue");
                    }
                    
               
                if(items.length>0){
                    let itemss=JSON.stringify(items);

                    frappe.call(
                        { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.laying_material_issue",
                                args: {
                                    batch:frm.doc.batch_name,
                                    parentfield:'rearing_medicine',
                                    items:itemss
                                },
                                callback: function(r) {  
                                    if(r.message) 
                                    {  
                                        $.each(r.message, function(i, rows) {                                            
                                            let row = locals[rows.doctype][rows.name];
                                            row.docstatus=1;
                                            row.issue='Yes';
                                            row.stock_entry=rows.stock_entry
                                        });
                                        //frm.reload_doc();
                                        frm.refresh_field('rearing_medicine');
                                    }   
                                }
                        });

                }else{
                    frappe.throw("Please select not issued items for Issuing");
                }
            },
	       
	        issue_rearing_items:function(frm){
                let items=[]
                let selected = frm.get_selected();
                    if(selected.rearing_items){
                        selected.rearing_items.forEach(function(item, index, array) {
                            let row = locals['Layer Other Items'][item];
                            if(row.issue!='Yes' && row.docstatus==0){
                                items.push(row);
                            }
                        });
                    }else{
                        frappe.throw("Please select items to Issue");
                    }
                    
               
                if(items.length>0){
                    let itemss=JSON.stringify(items);

                    frappe.call(
                        { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.laying_material_issue",
                                args: {
                                    batch:frm.doc.batch_name,
                                    parentfield:'rearing_items',
                                    items:itemss
                                },
                                callback: function(r) {  
                                    if(r.message) 
                                    {  
                                        $.each(r.message, function(i, rows) {                                            
                                            let row = locals[rows.doctype][rows.name];
                                            row.docstatus=1;
                                            row.issue='Yes';
                                            row.stock_entry=rows.stock_entry
                                        });
                                        //frm.reload_doc();
                                        frm.refresh_field('rearing_items');
                                    }   
                                }
                        });

                }else{
                    frappe.throw("Please select not issued items for Issuing");
                }
            },
            issue_rearing_mortality:function(frm){
                let items=[]
                let selected = frm.get_selected();
                    if(selected.rearing_daily_mortality){
                        selected.rearing_daily_mortality.forEach(function(item, index, array) {
                            let row = locals['Layer Mortality'][item];
                            if(row.issue!='Yes' && row.docstatus==0){
                                items.push(row);
                            }
                        });
                    }else{
                        frappe.throw("Please select items to Issue");
                    }
                    
               
                if(items.length>0){
                    let itemss=JSON.stringify(items);

                    frappe.call(
                        { 
                                method: "livestock.poultry.doctype.layer_batch.layer_batch.mortality_material_issue",
                                args: {
                                    batch:frm.doc.batch_name,
                                    parentfield:'rearing_daily_mortality',
                                    items:itemss
                                },
                                callback: function(r) {  
                                    if(r.message) 
                                    {  
                                        $.each(r.message, function(i, rows) {                                            
                                            let row = locals[rows.doctype][rows.name];
                                            row.docstatus=1;
                                            row.issue='Yes';
                                            row.stock_entry=rows.stock_entry
                                        });
                                        //frm.reload_doc();
                                        frm.refresh_field('rearing_daily_mortality');
                                    }   
                                }
                        });

                }else{
                    frappe.throw("Please select not issued items for Issuing");
                }
                
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

            frm.doc.current_alive_chicks=frm.doc.doc_placed-frm.doc.total_laying_mortality-frm.doc.total_mortaliy-frm.doc.sales_qty
            frm.refresh_field('current_alive_chicks');

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
            
            frm.doc.current_alive_chicks=frm.doc.doc_placed-frm.doc.total_laying_mortality-frm.doc.total_mortaliy-frm.doc.sales_qty
            frm.refresh_field('current_alive_chicks');

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
        //$(".grid-add-row").hide();
        //$(".grid-remove-rows").hide();
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
 
    },
    egg_production_on_form_rendered:function(frm, cdt, cdn) {
        frm.fields_dict["egg_production"].grid.wrapper.find('.grid-remove-rows').hide();
        //frm.get_field("egg_production").grid.df.cannot_delete_rows = true;
    }
});

//--------------------- end feed------------------------------