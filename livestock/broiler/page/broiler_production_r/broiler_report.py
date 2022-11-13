import frappe
from frappe.utils import getdate
from datetime import datetime, timedelta, date

@frappe.whitelist()
def get_company_list():
    data = {}
    data["companys"] = frappe.get_list("Company", fields=['name'],limit_page_length=0, order_by="name",debug=0)
    return data
    
@frappe.whitelist()
def get_report(company=None,from_date=None,to_date=None):
    data = {}
    if not company:
        company="ABU DHABI MODERNE POULTRY FARM L.L.C.";
    #.......................... creating shed group .................
    shedgps=[]
    
    shedgp=frappe.db.sql("""select gp.shedgp from (select SUBSTRING_INDEX(name, '-', 1) as shedgp from `tabBroiler Shed` where company='{0}'  order by name) as gp group by gp.shedgp""".format(company),as_dict=1,debug=0)

    for she in shedgp:
        sheds=[]
        shed=frappe.db.sql("""select name from `tabBroiler Shed` where SUBSTRING_INDEX(name, '-', 1)='{0}'  order by name""".format(she.shedgp),as_dict=1,debug=0)
        for sh in shed:
            sheds.append(sh.name)

        shedgps.append(sheds)
    #...................................... broiler shed groups are created...................................................
    #............................. creating dates between from and to for creating report ...................................
    dates=[]
    start_date=getdate(from_date)
    end_date=getdate(to_date)
    
    for dt in daterange(start_date, end_date):
        dates.append(dt.strftime("%Y-%m-%d"))
    
    #.......................... report date range created....................................................................
    #.......................... creating report by looping date for creating report on that date ............................
    report=[]

    for dts in dates:
        datesection=[dts]
        grandtot=['Birds Total',0,'',0,0,0,'',0,0,'',0,'']
        sections=[]
        for shdg in shedgps:            
            sectiontot=['Total',0,'',0,0,0,'',0,0,'',0,'']       
            for shd in shdg:
                batches=frappe.db.sql("""select * from `tabBroiler Batch` where broiler_shed='{0}' and ('{1}' between start_date and end_date) """.format(shd,dts),as_dict=1,debug=0)
                row=[shd,0,0,0,0,0,0,0,0,0,0,0]                
                if batches:
                    batch=batches[0].name                    
                    row[1]=batches[0].doc_placed
                    delta =  getdate(dts)- getdate(batches[0].start_date)
                    days=delta.days
                    row[2]=days
                    today_mortality=0
                    prev_mor=0
                    tran_cnt=0
                    tran_cnt_today=0
                    tmor=frappe.db.sql("""select total from `tabMortality` where  parent='{0}' and `date` ='{1}' """.format(batch,dts),as_dict=1,debug=0)
                    if tmor:
                        today_mortality=tmor[0].total
                    pmor=frappe.db.sql("""select sum(total) as prevmor from `tabMortality` where  parent='{0}' and `date` <'{1}' group by parent""".format(batch,dts),as_dict=1,debug=0)
                    if pmor:
                        prev_mor=pmor[0].prevmor
                    totmor=prev_mor+today_mortality

                    totrantoday=frappe.db.sql("""select sum(transfer_qty) as tottrn from `tabBroiler Item Transfer` where  broiler_bach='{0}' and transfer_date ='{1}' group by broiler_bach """.format(batch,dts),as_dict=1,debug=0)
                    if totrantoday:
                        tran_cnt_today=totrantoday[0].tottrn

                    totran=frappe.db.sql("""select sum(transfer_qty) as tottrn from `tabBroiler Item Transfer` where  broiler_bach='{0}' and transfer_date <='{1}' group by broiler_bach """.format(batch,dts),as_dict=1,debug=0)
                    if totran:
                        tran_cnt=totran[0].tottrn

                    vc_med=''
                    vccqr=frappe.db.sql("""select item_name,remark from `tabVaccine` where  parent='{0}' and `date` ='{1}' """.format(batch,dts),as_dict=1,debug=0)
                    if vccqr:
                        vc_med+=str(vccqr[0].item_name)
                    medqr=frappe.db.sql("""select item_name,remark from `tabMedicine` where  parent='{0}' and `date` ='{1}' """.format(batch,dts),as_dict=1,debug=0)
                    if medqr:
                        vc_med+=' - '+str(medqr[0].item_name)
                    
                    row[3]=batches[0].doc_placed-prev_mor
                    row[4]=today_mortality
                    row[5]=tran_cnt_today
                    if today_mortality:
                        row[6]=round(((100*today_mortality)/row[3]),2)
                    row[7]=totmor
                    row[8]=tran_cnt
                    if totmor:
                        row[9]=round(((100*totmor)/batches[0].doc_placed),2)
                    row[10]=batches[0].doc_placed-totmor
                    row[11]=vc_med

                    sectiontot[1]=sectiontot[1]+row[1]                    
                    sectiontot[3]=sectiontot[3]+row[3]
                    sectiontot[4]=sectiontot[4]+row[4]
                    sectiontot[5]=sectiontot[5]+row[5]                    
                    sectiontot[7]=sectiontot[7]+row[7]
                    sectiontot[8]=sectiontot[8]+row[8]                    
                    sectiontot[10]=sectiontot[10]+row[10]

                    grandtot[1]=grandtot[1]+row[1]                    
                    grandtot[3]=grandtot[3]+row[3]
                    grandtot[4]=grandtot[4]+row[4]
                    grandtot[5]=grandtot[5]+row[5]                    
                    grandtot[7]=grandtot[7]+row[7]
                    grandtot[8]=grandtot[8]+row[8]                    
                    grandtot[10]=grandtot[10]+row[10]
                    

                sections.append(row)
            sections.append(sectiontot)
        sections.append(grandtot)
        datesection.append(sections)
        #datesection.append(grandtot)    
        report.append(datesection)

    #........................ html data creation ........................................
    datahtml=''
    for rep in report:
        datahtml+='<table>	<tr><th colspan="10">'+company+'</th><th colspan="2">'+str(rep[0])+'</th></tr>'        
        datahtml+='<tr><td colspan="4"><td colspan="3">Daily Depletion</td><td colspan="3">Cumulative Depletion</td><td colspan="2"></td></tr>'
        datahtml+='<tr><td>Fram Shed</td>	<td>Placed Chick</td><td>Age</td><td>Open Balance</td><td>Mortality</td><td>Transfer</td><td>%</td><td>Mortality</td><td>Transfer</td><td>%</td><td>Closing Balance</td><td>Med/Vacc Details</td></tr>'
        
        for re in rep[1]:
            datahtml+='<tr>'
            for r in re:
                datahtml+='<td>'+str(r)+'</td>'
            datahtml+='</tr>'
        
        datahtml+='</tr></table><br><br>'
    #........................ html data creation end ....................................
    data['datahtml']=datahtml
    #data['report']=report   
    data['company']=company
    data['from_date']=from_date
    data['to_date']=to_date
    

    return data

def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)
    

    
    