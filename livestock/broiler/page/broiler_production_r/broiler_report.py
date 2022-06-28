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

    for dts in dates:
        for shdg in shedgps:
            for shd in shdg:
                batches=frappe.db.sql("""select * from `tabBroiler Batch` where broiler_shed='{0}' and start_date >='{1}' """.format(shd,from_date),as_dict=1,debug=0)
                #batches.doc_placed
                if batches:
                    batch=batches[0].name
                    frappe.db.sql("""select transfer_qty from `tabBroiler Item Transfer` where  broiler_bach='{0}' and transfer_date ='{1}' """.format(batch,dts),as_dict=1,debug=1)

                    frappe.db.sql("""select item_name,remark from `tabVaccine` where  parent='{0}' and `date` ='{1}' """.format(batch,dts),as_dict=1,debug=1)

                    frappe.db.sql("""select item_name,remark from `tabMedicine` where  parent='{0}' and `date` ='{1}' """.format(batch,dts),as_dict=1,debug=1)

                    frappe.db.sql("""select total from `tabMortality` where  parent='{0}' and `date` ='{1}' """.format(batch,dts),as_dict=1,debug=1)

                    frappe.db.sql("""select sum(total) as totmortality from `tabMortality` where  parent='{0}' and `date` <='{1}' group by parent""".format(batch,dts),as_dict=1,debug=1)

                    frappe.db.sql("""select sum(total) as prevmortality from `tabMortality` where  parent='{0}' and `date` <'{1}' group by parent""".format(batch,dts),as_dict=1,debug=1)


     
    
       
    data['company']=company
    data['from_date']=from_date
    data['to_date']=to_date
    

    return data

def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)
    

    
    