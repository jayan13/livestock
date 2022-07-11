import frappe

@frappe.whitelist()
def get_company_list():
    data = {}
    data["companys"] = frappe.get_list("Company", fields=['name'],limit_page_length=0, order_by="name",debug=0)
    return data
    
@frappe.whitelist()
def get_egg_report(company=None,posted_on=None):
    data = {}
    if not company:
        company="ABU DHABI POULTRY FARM - SOLE PROPRIETORSHIP L.L.C.";
        
    data['company']=company
    data['posted_on']=posted_on
   
    data['items']=items= frappe.db.sql("""select  item_code,item_name from tabItem where item_group='EGGS' """,as_dict=1)
    warehouses= frappe.db.sql("""select  name from tabWarehouse where company='{0}' and warehouse_type='Store' """.format(company),as_dict=1)
    oppeingstockqr=frappe.db.sql("""select  name from tabWarehouse where company='{0}' and warehouse_type='Layer' """.format(company),as_dict=1)
    

    warehouse=[]
    eggitems=[]
    for egit in items:
        eggitems.append(egit.item_code)

    for w in warehouses:
        warehouse.append(w.name)

    data['warehouse']=warehouse
    
    
#============================================================
    storeitems=[]
    daily_load_tot=[0,0,0,0]
    for item in items:
        wareitems=[]
        wareitems.append(item.item_name)
        i=0
        for wer in warehouse:
            sl_entrys= frappe.db.sql("""
                SELECT
                    sum(actual_qty) as qty
                FROM
                    `tabStock Ledger Entry` 
                WHERE
                    company = '{0}' 
                    AND is_cancelled = 0 
                    AND posting_date = '{1}'
                    AND item_code='{2}'
                    AND warehouse='{3}'
                GROUP BY
                    item_code
                """.format(company,posted_on,item.item_code,wer),as_dict=1,debug=0)
            itmqty=0         
            for sl_entry in sl_entrys:
                itmqty=get_item_ctn_qty(item.item_code,sl_entry.qty)

            wareitems.append(str(itmqty))
            daily_load_tot[i]=daily_load_tot[i]+itmqty
            i=i+1
        #frappe.msgprint(str(wareitems))
        storeitems.append(wareitems)

    data['store_items']=storeitems
    data['daily_load_tot']=daily_load_tot
    data['daily_load_gtot']=sum(daily_load_tot)
    #frappe.throw(str(daily_load_tot))
#===========================================================
    oppeingstockwh=[]
    daily_stock_tot=[0,0,0,0,0]
    stritems=[]    
    for oppeingstoc in oppeingstockqr:
        oppeingstockwh.append(oppeingstoc.name)
     
    warehouse_conditions_sql = ''
    if oppeingstockwh:
        warehouse_conditions_sql = """ and warehouse in ('{}')""".format( "' ,'".join([str(elem) for elem in oppeingstockwh]))

    stwarehouses= frappe.db.sql("""select  name from tabWarehouse where company='{0}' and warehouse_type='Store' """.format(company),as_dict=1,debug=0)
    
    for item in items:
        i=0

        stritem=[]
        stritem.append(item.item_name)
        sl_entrys= frappe.db.sql("""
                SELECT
                    sum(actual_qty) as qty
                FROM
                    `tabStock Ledger Entry` 
                WHERE
                    company = '{0}' 
                    AND is_cancelled = 0 
                    AND posting_date <= '{1}'
                    AND item_code='{2}'
                    {3}
                GROUP BY
                    item_code
                """.format(company,posted_on,item.item_code,warehouse_conditions_sql),as_dict=1,debug=0)
        itmqty=0         
        for sl_entry in sl_entrys:
            itmqty=get_item_ctn_qty(item.item_code,sl_entry.qty)

        stritem.append(itmqty)
        
        daily_stock_tot[i]=daily_stock_tot[i]+itmqty
        

        for st in stwarehouses:
            i=i+1
            sl_entrys= frappe.db.sql("""
                SELECT
                    sum(actual_qty) as qty
                FROM
                    `tabStock Ledger Entry` 
                WHERE
                    company = '{0}' 
                    AND is_cancelled = 0 
                    AND posting_date <= '{1}'
                    AND item_code='{2}'
                    AND warehouse='{3}'
                GROUP BY
                    item_code
                """.format(company,posted_on,item.item_code,st.name),as_dict=1,debug=0)
            itmqty=0         
            for sl_entry in sl_entrys:
                itmqty=get_item_ctn_qty(item.item_code,sl_entry.qty)
            stritem.append(itmqty)
            daily_stock_tot[i]=daily_stock_tot[i]+itmqty
        stritems.append(stritem)
    #frappe.throw(str(daily_stock_tot))
    data['stwarehouses']=stwarehouses
    data['daily_stock']=stritems
    data['daily_stock_tot']=daily_stock_tot

    return data

def get_item_ctn_qty(item_code,stock_qty):
    ctnqty=0   
    cv=frappe.db.get_value('UOM Conversion Detail', {'parent': item_code,'uom':'Ctn'}, 'conversion_factor', as_dict=1,debug=0)
    if stock_qty>0:
        ctnqty=round(stock_qty/cv.conversion_factor,2)
        
    return ctnqty
       
    

    
    