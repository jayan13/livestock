import frappe
from frappe.utils import getdate,add_days,get_first_day,get_last_day,nowdate,flt,date_diff
@frappe.whitelist()
def get_company_list():
    data = {}
    data["companys"] = frappe.get_list("Company", fields=['name'],limit_page_length=0, order_by="name",debug=0)
    return data

@frappe.whitelist()
def get_batch_list(company=None):
    data = {}
    data["batchs"] = frappe.get_list("Layer Batch",filters={'docstatus':['!=','2'],'company':company,'status':'Open'},fields=['name'],limit_page_length=0, order_by="name",debug=0)
    return data


@frappe.whitelist()
def get_report(company,batch,period=None):
    layer=frappe.get_doc('Layer Batch',batch)
     
    period=period or 'Start Date Of Project'
    pjt=frappe.db.get_value('Project',layer.project,['expected_start_date','expected_end_date'], as_dict=1)
    project_end=''
    if pjt:
        if pjt.expected_end_date:
            project_end=getdate(pjt.expected_end_date)
        project_start=getdate(pjt.expected_start_date)
        
    breakeven=frappe.db.get_value('Batch Type',layer.batch_type,'break_even_period')
    rear_perid=[]
    lay_perod=[]
    if layer.doc_placed_date:
        doc_placed_date=getdate(layer.doc_placed_date)

    flock_transfer_date=''
    if layer.flock_transfer_date:
        flock_transfer_date=getdate(layer.flock_transfer_date)

    if period=='Start Date Of Project':
        rear_start_date=doc_placed_date
        lay_start_date=flock_transfer_date
        rear_end_date=flock_transfer_date or getdate(nowdate())
        lay_end_date=project_end or getdate(nowdate())
    else:
        
        rear_start_date=get_first_day(getdate(layer.doc_placed_date))
        lay_start_date=get_first_day(getdate(layer.flock_transfer_date))
        rear_end_date=get_last_day(flock_transfer_date) or get_last_day(nowdate())
        lay_end_date=get_last_day(project_end) or get_last_day(nowdate())

    rstart=rear_start_date
    rend=''
    dept=[]
    depts=frappe.get_doc('Layer Wage Expense Departments',layer.company)
    if depts:
        for dep in depts.department:
            dept.append(dep.name)
    #lay_days=date_diff(lay_end_date,lay_start_date)+1
    
    while rstart < rear_end_date:
        rear={}
        if period=='Start Date Of Project':
            rend=add_days(rstart,30)
            rear.update({'start':rstart,'end':rend})
            rstart=add_days(rend,1)
        else:
            rend=get_last_day(rstart)
            rear.update({'start':rstart,'end':rend})
            rstart=add_days(rend,1)

        rear_perid.append(rear)

    lstart=lay_start_date
    while getdate(lstart) < getdate(lay_end_date):
        rear={}
        if period=='Start Date Of Project':
            rend=add_days(lstart,30)
            rear.update({'start':lstart,'end':rend})
            lstart=add_days(rend,1)
        else:
            rend=get_last_day(lstart)
            rear.update({'start':lstart,'end':rend})
            lstart=add_days(rend,1)

        lay_perod.append(rear)

    rear_data=[]
    lay_data=[]

    #----- rearing 
    rear_lbl=['Expense']
    rear_doc=['Doc']
    rear_feed=['Feed']
    rear_vaccine=['Vaccine']
    rear_medicine=['Medicine-Disinfectants']
    #rear_bio=['Biosecurity Requirements']
    #rear_miscel=['Miscellaneous Production Req.']
    rear_other=['Others']
    rear_wages=['Wages']
    reat_tot=['Total']
    rear_doc_tot=0
    rear_feed_tot=0
    rear_vaccine_tot=0
    rear_medicine_tot=0
    rear_bio_tot=0
    rear_miscel_tot=0
    rear_other_tot=0
    rear_wages_tot=0
    reat_tot_tot=0
    
    rear_html=''
    vaccine_list=frappe.db.get_list('Vaccine Items List',pluck='name')
#=========================================================================
    for rear in rear_perid:
        if period=='Accounting Period':
            date_lbl=rear.get('start').strftime("%b - %y")
        else:
            date_lbl=rear.get('start').strftime("%d/%m/%y")+'-'+rear.get('end').strftime("%d/%m/%y")
        rear_lbl.append(date_lbl)
        col_tot=0
        
    #---------------------------------
        base_row_material=''
        finished_product=''
        if layer.rearing_shed:
            rearing_shed=frappe.db.get_value('Rearing Shed',layer.rearing_shed,['base_row_material','finished_product'],as_dict=1)
            if rearing_shed:
                base_row_material=rearing_shed.base_row_material
                finished_product=rearing_shed.finished_product
        if base_row_material:
            itemamt=frappe.db.sql("""select IFNULL(sum(i.net_amount), 0) as amount from `tabPurchase Invoice Item` i left join `tabPurchase Invoice` p on p.name=i.parent 
where p.posting_date between '{0}' and '{1}' and i.item_code in('{2}','{3}') and p.project='{4}' """.format(rear.get('start'),rear.get('end'),base_row_material,finished_product,layer.name),as_dict=1,debug=0)
            if itemamt:
                rear_doc.append(itemamt[0].amount)
                col_tot+=float(itemamt[0].amount)
                rear_doc_tot+=float(itemamt[0].amount)
            else:
                rear_doc.append('0')
        else:
            rear_doc.append('0')
       
    #----------------------------------
        
        if layer.item_processed=='0':
            
            if layer.rearing_feed:
                amt=0
                for itm in layer.rearing_feed:
                    if getdate(rear.get('start')) <= getdate(itm.date) <= getdate(rear.get('end')):
                        amt+=itm.qty*itm.rate
                rear_feed.append(amt)
                rear_feed_tot+=amt
                col_tot+=amt
            else:
                rear_feed.append(0)

   #---------------------------------------         
            if layer.rearing_medicine:
                
                amt=0
                for itm in layer.rearing_medicine:
                    
                    if itm.item_code in vaccine_list and getdate(rear.get('start')) <= getdate(itm.date) <= getdate(rear.get('end')):
                        amt+=itm.qty*itm.rate
                rear_vaccine.append(amt)
                rear_vaccine_tot+=amt
                col_tot+=amt
    
                amt=0
                for itm in layer.rearing_medicine:
                    if itm.item_code not in vaccine_list and getdate(rear.get('start')) <= getdate(itm.date) <= getdate(rear.get('end')):
                        amt+=itm.qty*itm.rate
                
                rear_medicine.append(amt)
                rear_medicine_tot+=amt
                col_tot+=amt
            else:
                rear_vaccine.append(0)
                rear_medicine.append(0)
#------------------------------------------
            if layer.rearing_items:
                amt=0
                for itm in layer.rearing_items:
                    if getdate(rear.get('start')) <= getdate(itm.date) <= getdate(rear.get('end')):
                        amt+=itm.qty*itm.rate
                rear_other.append(amt)
                rear_other_tot+=amt
                col_tot+=amt
            else:
                rear_other.append(0)
            
        else:
            #item_group            
            
            if layer.rearing_feed:
                amt=0
                feed=[]
                for itm in layer.rearing_feed:
                    feed.append(itm.item_code)
                    
                feeds="','".join(feed)
                feedsql=frappe.db.sql(""" select  IFNULL(sum(d.amount), 0) as amount from `tabStock Entry Detail` d left join `tabStock Entry` s 
                on d.parent=s.name where s.stock_entry_type='Manufacture' and s.posting_date 
                between '{0}' and '{1}' and  s.docstatus=1 and d.item_code in ('{2}') and s.project='{3}' 
                """.format(rear.get('start'),rear.get('end'),feeds,layer.name),as_dict=1,debug=0)
                if feedsql:
                    amt=feedsql[0].amount
                rear_feed.append(amt)
                rear_feed_tot+=amt
                col_tot+=amt
            else:
                rear_feed.append(0)

   #---------------------------------------         
            if layer.rearing_medicine:                
                amt=0
                vacc=[]
                for itm in layer.rearing_medicine:
                    if itm.item_code in vaccine_list:
                        vacc.append(itm.item_code)
                
                vaccs="','".join(vacc)
                vaccsql=frappe.db.sql(""" select IFNULL(sum(d.amount), 0) as amount from `tabStock Entry Detail` d left join `tabStock Entry` s 
                on d.parent=s.name where s.stock_entry_type='Manufacture' and s.posting_date 
                between '{0}' and '{1}' and  s.docstatus=1 and d.item_code in ('{2}') and s.project='{3}' 
                """.format(rear.get('start'),rear.get('end'),vaccs,layer.name),as_dict=1,debug=0)
                if vaccsql:
                    amt=float(vaccsql[0].amount)
                rear_vaccine.append(amt)
                rear_vaccine_tot+=amt
                col_tot+=amt
    
                amt=0
                med=[]
                for itm in layer.rearing_medicine:
                    if itm.item_code not in vaccine_list:
                        med.append(itm.item_code)
                meds="','".join(med)
                medsql=frappe.db.sql(""" select IFNULL(sum(d.amount), 0) as amount from `tabStock Entry Detail` d left join `tabStock Entry` s 
                on d.parent=s.name where s.stock_entry_type='Manufacture' and s.posting_date 
                between '{0}' and '{1}' and  s.docstatus=1 and d.item_code in ('{2}') and s.project='{3}' 
                """.format(rear.get('start'),rear.get('end'),meds,layer.name),as_dict=1,debug=0)
                if medsql:
                    amt=float(medsql[0].amount)
                rear_medicine.append(amt)
                rear_medicine_tot+=amt
                col_tot+=amt
            else:
                rear_vaccine.append(0)
                rear_medicine.append(0)
#------------------------------------------
            if layer.rearing_items:
                amt=0
                oth=[]
                for itm in layer.rearing_items:
                    oth.append(itm.item_code)
                oths="','".join(oth)
                othsql=frappe.db.sql(""" select IFNULL(sum(d.amount), 0) as amount from `tabStock Entry Detail` d left join `tabStock Entry` s 
                on d.parent=s.name where s.stock_entry_type='Manufacture' and s.posting_date 
                between '{0}' and '{1}' and  s.docstatus=1 and d.item_code in ('{2}') and s.project='{3}' 
                """.format(rear.get('start'),rear.get('end'),oths,layer.name),as_dict=1,debug=0)
                if othsql:
                    amt=othsql[0].amount
                rear_other.append(amt)
                rear_other_tot+=amt
                col_tot+=amt
            else:
                rear_other.append(0)

            #rear_feed.append(0)
            #rear_vaccine.append(0)
            #rear_medicine.append(0)
            #rear_other.append(0)
        #-----------------------------------------
        start=rear.get('start')
        end=rear.get('end')
        sal=frappe.db.get_list('Salary Slip',filters={'status':'Submitted','company':layer.company,'end_date':['between',[start,end]]},fields=['net_pay'],pluck='net_pay')
        salary=0
        salary_expanse=0
        if sal:
            salary+=sum(c for c in sal)

        if salary:
            #wage rear_end_date layer.doc_placed rearing_daily_mortality
            mtotsrt=0
            mtotend=0
            mortmonthavg=0
            live=0
            if layer.rearing_daily_mortality:
                for mor in layer.rearing_daily_mortality:
                    if getdate(mor.date)< getdate(start):
                        mtotsrt+=float(mor.total)
                    if getdate(start) <= getdate(mor.date)<=getdate(end):
                        mtotend+=float(mor.total)

                if mtotend:
                    mortmonthavg=float(mtotend)/2
            live=float(layer.doc_placed)-float(mtotsrt)-float(mortmonthavg)
            mort_to=add_days(getdate(start),15)
            totbfor=frappe.db.sql("""select IFNULL(sum(m.total), 0) as tot,b.doc_placed,b.name from `tabLayer Batch` b 
            left join  `tabLayer Mortality` m on b.name=m.parent and m.date < '{1}'
            left join `tabProject` p on p.name=b.name 
            where b.company='{0}' 
            and ((b.doc_placed_date < '{2}' and (p.expected_end_date is NULL or p.expected_end_date='')) 
            or (b.doc_placed_date < '{2}' and p.expected_end_date >'{1}')) and b.name<>'{3}'
            group by b.name""".format(layer.company,start,end,layer.name),as_dict=1,debug=0)
            
            totcurrent=frappe.db.sql("""select IFNULL(sum(m.total), 0) as tot,b.name from `tabLayer Batch` b left join `tabLayer Mortality` m on b.name=m.parent and m.date between '{1}' and '{2}' where
            b.company='{0}' and b.name<>'{3}' group by b.name""".format(layer.company,start,end,layer.name),as_dict=1,debug=0)
            crr={}
            if totcurrent:
                for cr in totcurrent:
                    crr.update({cr.name:cr.tot})
            totlive=0
            if totbfor:
                for bf in totbfor:
                    totavg=0
                    if crr.get(bf.name):
                        totavg=float(crr.get(bf.name))/2

                    totlive+=bf.doc_placed-bf.tot-totavg
            
            wageper=(float(live)*100)/float(totlive)
           
            if wageper:
                salary_expanse=(float(salary)/100)*float(wageper)                
            else:
                batchcount=frappe.db.sql(""" select count(name) as cnt from `tabLayer Batch` where  status='Open' """,as_dict=1,debug=0)
                if batchcount:
                    salary_expanse=float(salary)/float(batchcount[0].cnt)

            rear_wages.append(salary_expanse)
            rear_wages_tot+=salary_expanse
            col_tot+=salary_expanse
        else:
            rear_wages.append(0)
        #frappe.msgprint(str(salary))
        #rear_vaccine.append(0)
        #rear_medicine.append(0)
        #rear_bio.append(0)
        #rear_miscel.append(0)
        #rear_other.append(0)
        #rear_wages.append(0)
    #----------------------------------
        reat_tot.append(col_tot)
    #------------------------------
    reat_tot_tot=float(rear_doc_tot)+float(rear_feed_tot)+float(rear_vaccine_tot)+float(rear_medicine_tot)+float(rear_bio_tot)+float(rear_miscel_tot)+float(rear_other_tot)+float(rear_wages_tot)
    rear_lbl.append('Total')
    rear_doc.append(rear_doc_tot)
    rear_feed.append(rear_feed_tot)
    rear_vaccine.append(rear_vaccine_tot)
    rear_medicine.append(rear_medicine_tot)
    #rear_bio.append(rear_bio_tot)
    #rear_miscel.append(rear_miscel_tot)
    rear_other.append(rear_other_tot)
    rear_wages.append(rear_wages_tot)
    reat_tot.append(reat_tot_tot)
    rear_graph=[]
    if rear_doc_tot:
        rear_graph.append({"label":"Doc","data":flt(rear_doc_tot,2)})
    if rear_feed_tot:
        rear_graph.append({"label":"Feed","data":flt(rear_feed_tot,2)})
    if rear_vaccine_tot:
        rear_graph.append({"label":"Vaccine","data":flt(rear_vaccine_tot,2)})
    if rear_medicine_tot:
        rear_graph.append({"label":"Medicine","data":flt(rear_medicine_tot,2)})
    if rear_other_tot:
        rear_graph.append({"label":"Other","data":flt(rear_other_tot,2)})
    if rear_wages_tot:
        rear_graph.append({"label":"Wages","data":flt(rear_wages_tot,2)})

#======================================

    #rear_data.append(rear_lbl)
    #rear_data.append(rear_doc)

    rear_html+='<tr>'
    for lbl in rear_lbl:
        rear_html+='<th scope="col">'+lbl+'</th>'
    rear_html+='</tr>'

    rear_html+='<tr>'
    
    #--------------------------------------
    rear_html+='<tr>'
    i=0
    for doc in rear_doc:
        if i==0:
            rear_html+='<th scope="row">'+str(doc)+'</th>'
        else:
            rear_html+='<td class="text-right">'+str(flt(doc,2))+'</td>'
        i+=1

    rear_html+='</tr>'
    #-----------------------------------
    rear_html+='<tr>'
    i=0
    for doc in rear_feed:
        if i==0:
            rear_html+='<th scope="row">'+str(doc)+'</th>'
        else:
            rear_html+='<td class="text-right">'+str(flt(doc,2))+'</td>'
        i+=1

    rear_html+='</tr>'
    #-----------------------------------
    rear_html+='<tr>'
    i=0
    for doc in rear_vaccine:
        if i==0:
            rear_html+='<th scope="row">'+str(doc)+'</th>'
        else:
            rear_html+='<td class="text-right">'+str(flt(doc,2))+'</td>'
        i+=1

    rear_html+='</tr>'
    #---------------------------------------------------
    rear_html+='<tr>'
    i=0
    for doc in rear_medicine:
        if i==0:
            rear_html+='<th scope="row">'+str(doc)+'</th>'
        else:
            rear_html+='<td class="text-right">'+str(flt(doc,2))+'</td>'
        i+=1

    rear_html+='</tr>'
    #---------------------------------------------------
    '''
    rear_html+='<tr>'
    i=0
    for doc in rear_bio:
        if i==0:
            rear_html+='<th scope="row">'+str(doc)+'</th>'
        else:
            rear_html+='<td class="text-right">'+str(flt(doc,2))+'</td>'
        i+=1

    rear_html+='</tr>'
    #---------------------------------------------------
    rear_html+='<tr>'
    i=0
    for doc in rear_miscel:
        if i==0:
            rear_html+='<th scope="row">'+str(doc)+'</th>'
        else:
            rear_html+='<td class="text-right">'+str(flt(doc,2))+'</td>'
        i+=1

    rear_html+='</tr>' '''
    #---------------------------------------------------
    rear_html+='<tr>'
    i=0
    for doc in rear_other:
        if i==0:
            rear_html+='<th scope="row">'+str(doc)+'</th>'
        else:
            rear_html+='<td class="text-right">'+str(flt(doc,2))+'</td>'
        i+=1

    rear_html+='</tr>'
    #---------------------------------------------------
    rear_html+='<tr>'
    i=0
    for doc in rear_wages:
        if i==0:
            rear_html+='<th scope="row">'+str(doc)+'</th>'
        else:
            rear_html+='<td class="text-right">'+str(flt(doc,2))+'</td>'
        i+=1

    rear_html+='</tr>'
    #---------------------------------------------------
    rear_html+='<tr>'
    i=0
    for doc in reat_tot:
        if i==0:
            rear_html+='<th scope="row">'+str(doc)+'</th>'
        else:
            rear_html+='<td class="text-right">'+str(flt(doc,2))+'</td>'
        i+=1

    rear_html+='</tr>'
    #---------------------------------------------------
    #Batch Type
    #break_even_period

    #----- Laying 
    lay_lbl=['Expense']
    lay_doc=['Doc']
    lay_feed=['Feed']
    lay_vaccine=['Vaccine']
    lay_medicine=['Medicine-Disinfectants']
    lay_other=['Others']
    lay_wages=['Wages']
    lay_tot=['Total']
    lay_rear=['Rearing Cost']
    lay_oper=['Operational Cost']
    lay_doc_tot=0
    lay_feed_tot=0
    lay_vaccine_tot=0
    lay_medicine_tot=0
    lay_other_tot=0
    lay_wages_tot=0
    lay_tot_tot=0
    lay_rear_tot=0
    lay_oper_tot=0
    
    lay_html=''
    for layin in lay_perod:
        
        #date_lbl=layin.get('start').strftime("%d/%m/%y")+'-'+layin.get('end').strftime("%d/%m/%y")
        if period=='Accounting Period':
            date_lbl=layin.get('start').strftime("%b - %y")
        else:
            date_lbl=layin.get('start').strftime("%d/%m/%y")+'-'+layin.get('end').strftime("%d/%m/%y")

        lay_lbl.append(date_lbl)
        col_tot=0
#----------------------------------------------
        if layer.laying_feed:
            amt=0
            feed=[]
            for itm in layer.laying_feed:
                feed.append(itm.item_code)
                    
            feeds="','".join(feed)
            feedsql=frappe.db.sql(""" select IFNULL(sum(d.amount), 0) as amount from `tabStock Entry Detail` d left join `tabStock Entry` s 
                on d.parent=s.name where s.stock_entry_type='Material Issue' and s.posting_date 
                between '{0}' and '{1}' and  s.docstatus=1 and d.item_code in ('{2}') and s.project='{3}' 
                """.format(layin.get('start'),layin.get('end'),feeds,layer.name),as_dict=1,debug=0)
            if feedsql:
                amt=feedsql[0].amount
            lay_feed.append(amt)
            lay_feed_tot+=amt
            col_tot+=amt
        else:
            lay_feed.append(0)
        #---------------------------------------         
        if layer.laying_medicine:                
            amt=0
            vacc=[]
            for itm in layer.laying_medicine:
                if itm.item_code in vaccine_list:
                    vacc.append(itm.item_code)
                
            vaccs="','".join(vacc)
            vaccsql=frappe.db.sql(""" select IFNULL(sum(d.amount), 0) as amount from `tabStock Entry Detail` d left join `tabStock Entry` s 
                on d.parent=s.name where s.stock_entry_type='Material Issue' and s.posting_date 
                between '{0}' and '{1}' and  s.docstatus=1 and d.item_code in ('{2}') and s.project='{3}' 
                """.format(layin.get('start'),layin.get('end'),vaccs,layer.name),as_dict=1,debug=0)
            if vaccsql:
                amt=float(vaccsql[0].amount)
            lay_vaccine.append(amt)
            lay_vaccine_tot+=amt
            col_tot+=amt
    
            amt=0
            med=[]
            for itm in layer.laying_medicine:                
                if itm.item_code not in vaccine_list:
                    med.append(itm.item_code)
            meds="','".join(med)
            medsql=frappe.db.sql(""" select IFNULL(sum(d.amount), 0) as amount from `tabStock Entry Detail` d left join `tabStock Entry` s 
                on d.parent=s.name where s.stock_entry_type='Material Issue' and s.posting_date 
                between '{0}' and '{1}' and  s.docstatus=1 and d.item_code in ('{2}') and s.project='{3}' 
                """.format(layin.get('start'),layin.get('end'),meds,layer.name),as_dict=1,debug=0)
            if medsql:
                amt=float(medsql[0].amount)
            
            #frappe.msgprint(str(amt))
            lay_medicine.append(amt)
            lay_medicine_tot+=amt
            col_tot+=amt
        else:
            lay_vaccine.append(0)
            lay_medicine.append(0)
        #------------------------------------------
        if layer.laying_items:
            amt=0
            oth=[]
            for itm in layer.laying_items:
                oth.append(itm.item_code)
            oths="','".join(oth)
            othsql=frappe.db.sql(""" select IFNULL(sum(d.amount), 0) as amount from `tabStock Entry Detail` d left join `tabStock Entry` s 
                on d.parent=s.name where s.stock_entry_type='Material Issue' and s.posting_date 
                between '{0}' and '{1}' and  s.docstatus=1 and d.item_code in ('{2}') and s.project='{3}' 
                """.format(layin.get('start'),layin.get('end'),oths,layer.name),as_dict=1,debug=0)
            if othsql:
                amt=othsql[0].amount
            lay_other.append(amt)
            lay_other_tot+=amt
            col_tot+=amt
        else:
            lay_other.append(0)

#-----------------------------------------
        
        #frappe.msgprint(str(dept))
        start=layin.get('start')
        end=layin.get('end')
        sal=frappe.db.get_list('Salary Slip',filters={'status':'Submitted','company':layer.company,'end_date':['between',[start,end]],'department':['in',dept]},fields=['net_pay'],pluck='net_pay')
        salary=0
        salary_expanse=0
        if sal:
            salary+=sum(c for c in sal)

        if salary:
            #wage lay_end_date layer.doc_placed laying_mortality
            mtotsrt=0
            mtotend=0
            mortmonthavg=0
            live=0
            mtotsrt=0
            mtotend=0
            mortmonthavg=0
            live=0
            if layer.rearing_daily_mortality:
                for mor in layer.rearing_daily_mortality:
                    mtotsrt+=float(mor.total)
                    

            if layer.laying_mortality:
                for mor in layer.laying_mortality:
                    if getdate(mor.date)< getdate(start):
                        mtotsrt+=float(mor.total)
                    if getdate(start) <= getdate(mor.date)<=getdate(end):
                        mtotend+=float(mor.total)

                if mtotend:
                    mortmonthavg=float(mtotend)/2
            live=float(layer.doc_placed)-float(mtotsrt)-float(mortmonthavg)
            mort_to=add_days(getdate(start),15)
            #totbfor=frappe.db.sql("""select IFNULL(sum(m.total), 0) as tot,b.doc_placed,b.name from `tabLayer Batch` b left join  `tabLayer Mortality` m on b.name=m.parent and m.date < '{1}' where
            #b.company='{0}'  group by b.name""".format(layer.company,start),as_dict=1,debug=1)

            totbfor=frappe.db.sql("""select IFNULL(sum(m.total), 0) as tot,b.doc_placed,b.name from `tabLayer Batch` b 
            left join  `tabLayer Mortality` m on b.name=m.parent and m.date < '{1}'
            left join `tabProject` p on p.name=b.name 
            where b.company='{0}' 
            and ((b.doc_placed_date < '{2}' and (p.expected_end_date is NULL or p.expected_end_date='')) 
            or (b.doc_placed_date < '{2}' and p.expected_end_date >'{1}')) and b.name<>'{3}'
            group by b.name""".format(layer.company,start,end,layer.name),as_dict=1,debug=0)

            totcurrent=frappe.db.sql("""select IFNULL(sum(m.total), 0) as tot,b.name from `tabLayer Batch` b left join `tabLayer Mortality` m on b.name=m.parent and m.date between '{1}' and '{2}' where
            b.company='{0}' and b.name<>'{3}' group by b.name""".format(layer.company,start,end,layer.name),as_dict=1,debug=0)
            crr={}
            if totcurrent:
                for cr in totcurrent:
                    crr.update({cr.name:cr.tot})
            totlive=0
            if totbfor:
                for bf in totbfor:
                    totavg=0
                    if crr.get(bf.name):
                        totavg=float(crr.get(bf.name))/2

                    totlive+=bf.doc_placed-bf.tot-totavg
            
            wageper=(float(live)*100)/float(totlive)
           
            if wageper:
                salary_expanse=(float(salary)/100)*float(wageper)                
            else:
                batchcount=frappe.db.sql(""" select count(name) as cnt from `tabLayer Batch` where  status='Open' """,as_dict=1,debug=0)
                if batchcount:
                    salary_expanse=float(salary)/float(batchcount[0].cnt)

            lay_wages.append(salary_expanse)
            lay_wages_tot+=salary_expanse
            col_tot+=salary_expanse
        else:
            lay_wages.append(0)
#----------------------------------
        lay_tot.append(col_tot)
    
    #-----------------------------
    lay_tot_tot=float(lay_doc_tot)+float(lay_feed_tot)+float(lay_vaccine_tot)+float(lay_medicine_tot)+float(lay_other_tot)+float(lay_wages_tot)
    lay_lbl.append('Total')
    lay_doc.append(lay_doc_tot)
    lay_feed.append(lay_feed_tot)
    lay_vaccine.append(lay_vaccine_tot)
    lay_medicine.append(lay_medicine_tot)
    #rear_bio.append(rear_bio_tot)
    #rear_miscel.append(rear_miscel_tot)
    lay_other.append(lay_other_tot)
    lay_wages.append(lay_wages_tot)
    lay_tot.append(lay_tot_tot)

    lay_graph=[]

    if lay_feed_tot:
        lay_graph.append({"label":"Feed","data":flt(lay_feed_tot,2)})
    if lay_vaccine_tot:
        lay_graph.append({"label":"Vaccine","data":flt(lay_vaccine_tot,2)})
    if lay_medicine_tot:
        lay_graph.append({"label":"Medicine","data":flt(lay_medicine_tot,2)})
    if lay_other_tot:
        lay_graph.append({"label":"Other","data":flt(lay_other_tot,2)})
    if lay_wages_tot:
        lay_graph.append({"label":"Wages","data":flt(lay_wages_tot,2)})
    
    col_cnt=1
    eggp_lbl=[]
    egg_prod_item=[]
    egg_prod=[]
    egg_prod_data=[]
    egg_tot_prod=[]
    egg_tot_prod_col=0
    egg_tot=0
    egg_col_tot=0
    sale_col_tot=0
    sale_tot=0
    sales=[]
    sales_data=[]
    for layin in lay_perod:
        egg_col_tot=0
        sale_col_tot=0
        egg_tot_prod_col=0
        ly_lbl=layin.get('start').strftime("%d-%m-%y")+'-'+layin.get('end').strftime("%d-%m-%y")
        eggp_lbl.append(ly_lbl)
        #------------------------------
        rear_cost=0
        oper_cost=0
        if col_cnt <= breakeven:
            rear_cost=float(reat_tot_tot)/float(breakeven)
            
        lay_rear.append(rear_cost)
        lay_rear_tot+=rear_cost

        oper_cost=float(lay_tot[col_cnt])+float(rear_cost)
        lay_oper.append(oper_cost)
        lay_oper_tot+=oper_cost
        col_cnt+=1
        #----------------------------------------------
        egg_manu_sql=frappe.db.sql(""" select sum(d.transfer_qty) as qty,d.item_code from `tabStock Entry Detail` d left join `tabStock Entry` s 
                on d.parent=s.name where s.stock_entry_type='Manufacture' and d.is_finished_item=1 and 
                s.docstatus=1 and s.manufacturing_type='Egg' and s.posting_date between '{0}' and '{1}' and  s.project='{2}'
                 group by d.item_code""".format(layin.get('start'),layin.get('end'),layer.name),as_dict=1,debug=0)
        
        if egg_manu_sql:
            egg_prod_data.append(egg_manu_sql)
            for p in egg_manu_sql:
                egg_prod_item.append(p.item_code)
                egg_tot+=p.qty
                egg_col_tot+=p.qty
            egg_prod.append(egg_col_tot)
        else:
            egg_prod_data.append('')
            egg_prod.append(0)
            
        #-----------------------------------------------------------------
        egg_tot_manu_sql=frappe.db.sql(""" select sum(d.transfer_qty) as qty,d.item_code from `tabStock Entry Detail` d left join `tabStock Entry` s 
                on d.parent=s.name where s.stock_entry_type='Manufacture' and d.is_finished_item=1 and 
                s.docstatus=1 and s.manufacturing_type='Egg' and s.posting_date between '{0}' and '{1}' 
                 group by d.item_code""".format(layin.get('start'),layin.get('end')),as_dict=1,debug=0)

        if egg_tot_manu_sql:
            for totp in egg_tot_manu_sql:
                egg_tot_prod_col+=totp.qty
            egg_tot_prod.append(egg_tot_prod_col)
        else:
            egg_tot_prod.append(0)

        egg_sale_sql=frappe.db.sql("""select i.item_code,sum(i.amount) as amount,sum(i.stock_qty) as qty from `tabSales Invoice Item` i left join `tabSales Invoice` s on i.parent=s.name where s.docstatus=1 and i.item_group='EGGS'
        and s.company='{0}' and s.posting_date between '{1}' and '{2}' group by i.item_code """.format(layer.company,layin.get('start'),layin.get('end')),as_dict=1,debug=0)
        if egg_sale_sql:
            sales_data.append(egg_sale_sql)
            for s in egg_sale_sql:
                sale_col_tot+=s.amount
                sale_tot+=s.amount
            sales.append(sale_col_tot)
        else:
            sales_data.append('')
            sales.append(0)

    #-----------------------------
    egg_prod.append(egg_tot)
    #sales.append(sale_tot)
    lay_rear.append(lay_rear_tot)
    lay_oper.append(lay_oper_tot)
    
    #-----------------------------------------
    lay_html+='<tr>'
    for lbl in lay_lbl:
        lay_html+='<th scope="col">'+lbl+'</th>'
    lay_html+='</tr>'

    #-----------------------------------
    lay_html+='<tr>'
    i=0
    for doc in lay_feed:
        if i==0:
            lay_html+='<th scope="row">'+str(doc)+'</th>'
        else:
            lay_html+='<td class="text-right">'+str(flt(doc,2))+'</td>'
        i+=1

    lay_html+='</tr>'
    #-----------------------------------
    lay_html+='<tr>'
    i=0
    for doc in lay_vaccine:
        if i==0:
            lay_html+='<th scope="row">'+str(doc)+'</th>'
        else:
            lay_html+='<td class="text-right">'+str(flt(doc,2))+'</td>'
        i+=1

    lay_html+='</tr>'
    #---------------------------------------------------
    lay_html+='<tr>'
    i=0
    for doc in lay_medicine:
        if i==0:
            lay_html+='<th scope="row">'+str(doc)+'</th>'
        else:
            lay_html+='<td class="text-right">'+str(flt(doc,2))+'</td>'
        i+=1

    lay_html+='</tr>'
    #---------------------------------------------------
    lay_html+='<tr>'
    i=0
    for doc in lay_other:
        if i==0:
            lay_html+='<th scope="row">'+str(doc)+'</th>'
        else:
            lay_html+='<td class="text-right">'+str(flt(doc,2))+'</td>'
        i+=1

    lay_html+='</tr>'
    #---------------------------------------------------
    lay_html+='<tr>'
    i=0
    for doc in lay_wages:
        if i==0:
            lay_html+='<th scope="row">'+str(doc)+'</th>'
        else:
            lay_html+='<td class="text-right">'+str(flt(doc,2))+'</td>'
        i+=1

    lay_html+='</tr>'

     #---------------------------------------------------
    lay_html+='<tr>'
    i=0
    for doc in lay_tot:
        if i==0:
            lay_html+='<th scope="row">'+str(doc)+'</th>'
        else:
            lay_html+='<td class="text-right">'+str(flt(doc,2))+'</td>'
        i+=1

    lay_html+='</tr>'
    #------------------------- blank row --------------------------
    lay_html+='<tr>'
    i=0
    for doc in lay_tot:
        if i==0:
            lay_html+='<th scope="row"></th>'
        else:
            lay_html+='<td class="text-right"></td>'
        i+=1

    lay_html+='</tr>'
    #---------------------------------------------------
    lay_html+='<tr>'
    i=0
    for doc in lay_rear:
        if i==0:
            lay_html+='<th scope="row">'+str(doc)+'</th>'
        else:
            lay_html+='<td class="text-right">'+str(flt(doc,2))+'</td>'
        i+=1

    lay_html+='</tr>'
    #---------------------------------------------------
    lay_html+='<tr>'
    i=0
    for doc in lay_oper:
        if i==0:
            lay_html+='<th scope="row">'+str(doc)+'</th>'
        else:
            lay_html+='<td class="text-right">'+str(flt(doc,2))+'</td>'
        i+=1

    lay_html+='</tr>'
    #------------------------blank ---------------------------
    lay_html+='<tr>'
    i=0
    for doc in lay_tot:
        if i==0:
            lay_html+='<th scope="row"></th>'
        else:
            lay_html+='<td class="text-right"></td>'
        i+=1

    lay_html+='</tr>'
    
    #-------------------------egg production -------------------
    
    if egg_prod_data:
        egg_prod_item=list(dict.fromkeys(egg_prod_item))
        
        for item in egg_prod_item:
            row_sum=0
            lay_html+='<tr>'
            lay_html+='<th scope="row">'+str(getitem_name(item))+'</th>'
            for egg_dt in egg_prod_data:
                if egg_dt:
                    for egg_dta in egg_dt:
                        #frappe.msgprint(str(egg_dta))
                        if item==egg_dta.item_code:
                            row_sum+=egg_dta.qty
                            lay_html+='<td class="text-right">'+str(flt(egg_dta.qty,2))+'</td>'
                else:
                    lay_html+='<td class="text-right">0</td>'

            lay_html+='<td class="text-right">'+str(row_sum)+'</td>'        
            lay_html+='</tr>'
   #------------------------------------
   
    lay_html+='<tr><th> </th>'
    i=0
    for doc in egg_prod:
        lay_html+='<td class="text-right">'+str(flt(doc,2))+'</td>'

    lay_html+='</tr>'
#---------------------------------------------------
#------------------------blank ---------------------------
    lay_html+='<tr>'
    i=0
    for doc in lay_tot:
        if i==0:
            lay_html+='<th scope="row"></th>'
        else:
            lay_html+='<td class="text-right"></td>'
        i+=1

    lay_html+='</tr>'
  #------------------------ sale ------------------------
    
    if sales:
        sale_totol=0
        lay_html+='<tr><th>Sales </th>'
        j=0
        for s in sales:
            #frappe.msgprint(str(egg_prod[j]))
            if egg_prod[j] and j < len(egg_prod):
                p=(float(egg_prod[j])*100)/float(egg_tot_prod[j])
                a=(float(s)/100)*float(p)
                sale_totol+=a
                lay_html+='<td class="text-right">'+str(flt(a,2))+'</td>'
            else:
                lay_html+='<td class="text-right">0</td>'
            j+=1
        lay_html+='<td class="text-right">'+str(flt(sale_totol,2))+'</td>'
        lay_html+='</tr>'

   
    return {'rear':rear_html,'lay':lay_html,'budget':'','lay_graph':lay_graph,'rear_graph':rear_graph}

def getitem_name(item_code):
    return frappe.db.get_value('Item',item_code,'item_name')


