from . import db
from . import dates
import copy
import threading

def report_val_clean(store_id, report_id, start_date, end_date, res):
    cnxn = db.Database()
    report_val = cnxn.db_report_val(report_id, store_id, start_date, end_date, None)
    report_val = report_val["value"]
    res.append(report_val)
    return res

def num_orders_by_weekday(store_id, dashboard_date):
    start_date = copy.deepcopy(dashboard_date)
    start_date.set_start_of_day()
    res1 = []
    t1 = threading.Thread(target=report_val_clean, args=(store_id, 9, start_date, dashboard_date, res1))
    t1.start()

    end_date = copy.deepcopy(start_date)
    start_date.add_years(-1)
    res2 = []
    t2 = threading.Thread(target=report_val_clean, args=(store_id, 63, start_date, end_date, res2))
    t2.start()

    t1.join()
    t2.join()
    return {
        "report_id" : 24,
        "by_weekday" : res2[0],
        "comparison_day" : res1[0]
    }
