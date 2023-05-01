import pymysql.cursors
import pyodbc
import json
from flask import g, jsonify
from . import main
from ast import literal_eval
import pandas as pd
import threading
import mysql.connector
import faulthandler; faulthandler.enable()

DB_PORT = None
SERVER_URI = None
DB_NAME = None
DB_USER_NAME = None
DB_USER_PASS = None

NULL = 'NULL'


def init_app(app):
    # app.teardown_appcontext(close_db)

    global DB_PORT, SERVER_URI, DB_NAME, DB_USER_NAME, DB_USER_PASS

    DB_PORT = app.config['DB_PORT']
    SERVER_URI = app.config['SERVER_URI']
    DB_NAME = app.config['DB_NAME']
    DB_USER_NAME = app.config['DB_USER_NAME']
    DB_USER_PASS = app.config['DB_USER_PASS']


def param_nameval_to_sql(name, val):
    val = nullify_or_stringify(val)
    # res = "@"+name+"="+val
    res = val
    return res


def nullify_or_stringify(var):
    # res = NULL if var is None else "'"+str(var)+"'"
    res = NULL if var is None else str(var)
    return res
    
def create_connection():
        return pymysql.connect(
            user = '',
            password = '',
            host = '',
            database = '',
            cursorclass=pymysql.cursors.DictCursor
        )  

class Database():
    cnxn = None
    crsr = None

    def __init__(self):
        user = ''
        password = ''
        host = ''
        database = ''
        port = 3306
        self.cnxn = pymysql.connect(host=SERVER_URI, port=3306,
                                    user=DB_USER_NAME, password=DB_USER_PASS, database=DB_NAME)

        self.crsr = self.cnxn.cursor()

        # self.cnxn = pymysql.connect(host=host,
        #                      user=user,
        #                      password=password,
        #                      database=database,
        #                      cursorclass=pymysql.cursors.DictCursor)
        

        # with self.cnxn:
        #     with self.cnxn.cursor() as cursor:
        #         # Create a new record
        #         sql = "INSERT INTO `test` (`email`, `password`) VALUES (%s, %s)"
        #         cursor.execute(sql, ('webmaster@python.org', 'very-secret'))     

    def query(self, proc_name, params, *, is_report=False):

        param_names = ""
        param_values = []
        for name, val in params.items():
            param_names += f"@{name}=?,"
            param_values.append(val)

        sql_declare = 'declare @out nvarchar(max)'
        sql_exec = 'exec [dbo].[' + proc_name + ']'
        sql_out_param = '@out=@out output'
        sql_select_out = 'select @out'

        sql = sql_declare + '; ' + sql_exec + ' ' + param_names + \
            ' ' + sql_out_param + '; ' + sql_select_out + ';'

        # print(sql)
        self.crsr.execute(sql, param_values)
        row = self.crsr.fetchone()
        json_val = row[0]
        if json_val is not None:

            if is_report:
                json_val = json_val.split(']')  # split the str to arr

                dict_val = json.loads(json_val[0] + ']')
                graphs = {}
                if len(json_val) > 1:
                    for i, graph_data in enumerate(json_val[1:-1], start=1):
                        graphs[i] = json.loads(graph_data + ']')

                return dict_val, graphs

            return json.loads(json_val)

    def execute(self, proc_name, params):
        params_arr = []
        for name, val in params.items():
            params_arr.append(param_nameval_to_sql(name, val))

        sql_exec = 'exec [dbo].[' + proc_name + ']'
        sql_in_params = ','.join(params_arr)
        data = sql_in_params.split(",")
        print(data)
        try:
            res = self.crsr.callproc(proc_name, data)
            print(res)
        except:
            self.close()
            raise

    def commit(self):
        return self.cnxn.commit()

    def close(self):
        self.cnxn.close()
        # print("CONNECTION CLOSED!")

    def insert_new_order(self, data):
        proc_name = 'insert_new_order'
        self.execute(proc_name, data)

    def insert_new_order_prod(self, data):
        proc_name = 'insert_new_order_prod'
        self.execute(proc_name, data)

    def num_orders_by_weekday_proc(self, data):
        params_arr = []
        for name, val in data.items():
            params_arr.append(param_nameval_to_sql(name, val))

        sql_in_params = ','.join(params_arr)
        data = sql_in_params
        data = data[:-1]
        data = ["15", "2020-01-01 10:10:10.000", "2020-01-01 10:10:10.000"]
        proc_name = 'get_orders_by_date'

        # res=self.execute(proc_name, data)
        cursorObject = self.cnxn.cursor()
        cursorObject.callproc(proc_name, data)
        # cursorObject.execute(proc_name)
        # this will extract row headers
        keys = [x[0] for x in cursorObject.description]
        keys_number = len(keys)
        proc_results = cursorObject.fetchall()

        print(keys)
        json_data = []

        for result in proc_results:
            item = dict()
            for q in range(keys_number):
                item[keys[q]] = result[q]
            json_data.append(item)
            # json_data.append(dict(zip(row_headers, result)))
        print(json_data)
        return json_data

    def excute_proc(self, proc_name, data):
        params_arr = []
        try:
            for name, val in data.items():
                params_arr.append(param_nameval_to_sql(name, val))
        except:
            params_arr.append(data)
        # params = ','.join(params_arr)
        # data = params
        # data = data[:-1]
        # data = ["15", "2020-01-01 10:10:10.000", "2020-01-01 10:10:10.000"]
        proc_name = proc_name

        # res=self.execute(proc_name, data)
        cursorObject = self.cnxn.cursor()
        cursorObject.callproc(proc_name, params_arr)
        # cursorObject.execute(proc_name)
        # this will extract row headers
        keys = [x[0] for x in cursorObject.description]
        keys_number = len(keys)
        proc_results = cursorObject.fetchall()
        print(keys)
        json_data =  []
        for result in proc_results:
            item = dict()
            for q in range(keys_number):
                item[keys[q]] = result[q]
            json_data.append(item)
            # json_data.append(dict(zip(row_headers, result)))
        return json_data

    def insert_or_update_client(self, store_id, action, client_id, email, first_name, last_name, username, action_date):
        proc_name = 'insert_or_update_client'
        data = {
            'store_id': store_id,
            'client_id': client_id,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'action_date': action_date,
            'action': action
        }
        self.execute(proc_name, data)

    def insert_cart_action(self, store_id, prod_id, prod_name, manufacturer_name, item_price, num_items, cookie,
                           action_code, email, action_date):
        proc_name = 'insert_cart_action'
        data = {
            "store_id": store_id,
            "prod_id": prod_id,
            "prod_name": prod_name,
            "manufacturer_name": manufacturer_name,
            "item_price": item_price,
            "num_items": num_items,
            "cookie": cookie,
            "action_code": action_code,
            "email": email,
            "action_date": action_date
        }
        self.execute(proc_name, data)

    def insert_prod_view(self, store_id, prod_id, prod_name, manufacturer_name, cookie, email, action_date):
        proc_name = 'insert_prod_view'
        data = {
            'store_id': store_id,
            'prod_id': prod_id,
            'prod_name': prod_name,
            'manufacturer_name': manufacturer_name,
            'cookie': cookie,
            'email': email,
            'action_date': action_date
        }
        self.execute(proc_name, data)

    def update_prods(self, data):
        proc_name = 'update_products'
        self.execute(proc_name, data)

    def google_reports(self, store_id):
        proc_name = 'dashboard_reports_google_analytics'
        params = {
            'store_id': store_id
        }
        res = self.query(proc_name, params)

        return res

    def dashboard_db_report_ids(self, store_id):
        proc_name = 'dashboard_db_report_ids'
        params = {
            'store_id': store_id
        }
        # report_ids_json = self.query(proc_name, params)
        # report_ids_list = []
        # for entry in report_ids_json:
        #     report_ids_list.append(entry['report_id'])
        # return report_ids_list
        res = self.query(proc_name, params)

        return res

    def db_report_val(self, report_id, store_id, start_date, end_date, period):

        proc_name = 'get_report_val_proc'
        params = {
            'report_id': report_id,
            'store_id': store_id,
            'start_date': start_date.str_to_db(),
            'end_date': end_date.str_to_db(),
            'period': period
        }

        res = self.query(proc_name, params)

        return res

    def client_details(self, store_id, client_id):
        proc_name = 'client_details_proc'
        params = {
            'store_id': store_id,
            'client_id': client_id
        }
        res = self.query(proc_name, params)
        return res

    def checks_by_age(self, store_id, age):
        proc_name = 'checks_by_age_proc'
        params = {
            'store_id': store_id,
            'age': age
        }
        res = self.query(proc_name, params)
        return res

    def db_report_val_clean(self, report_id, store_id, start_date, end_date, period):
        proc_name = 'get_report_val_clean_proc'
        params = {
            'report_id': report_id,
            'store_id': store_id,
            'start_date': start_date.str_to_db(),
            'end_date': end_date.str_to_db(),
            'period': period
        }
        res = self.query(proc_name, params)

        return res

    def onclick_report_val(self, report_id, store_id, start_date, end_date, period):
        proc_name = 'get_report_data_onclick'
        params = {
            'report_id': report_id,
            'store_id': store_id,
            'start_date': start_date.str_to_db(),
            'end_date': end_date.str_to_db(),
            'period': period
        }
        res = self.query(proc_name, params)

        return res

    def available_dashboard_reports(self, store_id):
        proc_name = 'available_dashboard_reports'
        params = {
            'store_id': store_id
        }
        res = self.query(proc_name, params)

        return res

    def put_dashboard_reports(self, store_id, reports):
        proc_name = 'put_dashboard_reports'
        data = {
            "store_id": store_id,
            "reports": reports
        }
        self.execute(proc_name, data)

    # def __del__(self):
    #     print("CLOSING CONNECTION...")
    #     self.cnxn.close()
    #     print("CONNECTION CLOSED!")


class MultipleReports:
    reports = None
    _lock = None

    def __init__(self):
        self.reports = []
        self._lock = threading.Lock()

    def add(self, report):
        with self._lock:
            self.reports.append(report)

    def to_json(self):
        return self.reports


def db_report_val_thread(report_id, store_id, start_date, end_date, period, report_vals, to_compare, start_date_compar,
                         end_date_compar):
    cnxn = Database()
    report_val = cnxn.db_report_val(
        report_id, store_id, start_date, end_date, period)
    if to_compare == 1:
        report_val['compar_val'] = cnxn.db_report_val(report_id, store_id, start_date_compar, end_date_compar, period)[
            'value']
    report_vals.add(report_val)
