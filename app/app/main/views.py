from . import main
from flask import Flask
from flask import jsonify
from flask import request
from flask import current_app
from flask import session
import pyodbc
import pandas as pd
from numbers import Number
from . import db
# from .google_analytics import get_metrics, get_metric
from ast import literal_eval
from . import dates
from . import reports
import datetime
import copy
import threading
import copy
import simplejson
import json
import faulthandler;

faulthandler.enable()
import csv

# import multiprocessing


from .front_update import get_all_reports, get_dm_org_struct

config = {
    'user': '',
    'password': '',
    'host': '',
    'database': ''
}

period_to_days = {
    'd': 1,
    'w': 7,
    'm': 30,
    'q': 90,
    'y': 365
}

cart_actions_name_to_code = {
    'add': 1,
    'remove': 2
}

text_to_bool = {
    'true': True,
    'false': False
}


#############################################################3
#################TO DELETE###################################
##############################################################
@main.route("/", methods=["GET"])
def hello():
    return 'HELLO_W'


@main.route("/attempt", methods=["POST"])
def hello13():
    connection = db.create_connection()
    print(connection)
    cursor = connection.cursor()
    sql = """select * from global_reports where report_id = 1"""
    cursor.execute(sql)
    driver = cursor.fetchone()
    print(driver)
    return driver

# @main.route("/attempt2", methods=["POST"])
# def hello2():
#     cnxn = db.Database()
#     csv_data = csv.reader(open('/Users/israel/Downloads/Products.csv'))
#     next(csv_data)
#     for row in csv_data:
#         cnxn.crsr.execute("INSERT INTO product_compare_agg(Barcode,Product_Name,Manufacturer,Department,Category,Purchase_Price,Sale_Price,Diff_In_Prectenge,Total_Sum,Total_Quantitiy) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", row)
#         print(row)
#     cnxn.commit()
#     return 'OK'

@main.route('/attempt/<int:report_id>', methods=["POST"])
def report_val_temp(report_id):
    sql = """
        select
            report_id,
            category,
            report_name,
            report_desc,
            type,
            type_additions,
            report_id_onclick,
            options,
            func_name
        from global_reports
        where report_id = ?
    """
    cnxn = db.Database()
    cnxn.crsr.execute(sql, report_id)
    row = cnxn.crsr.fetchone()
    options = json.loads(row.options)
    params = {
        "dates": request.json.get("dates"),
        "start_date": request.json.get("start_date"),
        "end_date": request.json.get("end_date")
    }
    for param_name, param_desc in options.items():
        if param_name == "days":
            values = request.json[param_name]
            values = [str(weekday + 1) for weekday in values]
            values = ",".join(values)
            params[param_name] = values
        elif param_name == "store_ids" or param_name == "pos_ids":
            params[param_name] = ','.join([str(i) for i in request.json[param_name]])

        elif (type(param_desc) is str and param_desc == "array") or type(param_desc) is dict:
            values = request.json[param_name]
            values = [f"'{element}'" for element in values]
            values = ",".join(values)
            params[param_name] = values
        else:
            params[param_name] = request.json[param_name]

    return jsonify(params)


###########################################33

@main.route("/dashboard", methods=["POST"])
def dashboard():
    # get user parameters from request
    store_id = int(request.json.get('storeid'))
    period = request.json.get('period')
    is_accum = text_to_bool[request.json.get('accum')]

    start_date, end_date = dates_by_period(period, is_accum)
    start_date_compar, end_date_compar = dates_by_period_for_comparison(period, is_accum)

    res1 = []
    res2 = []
    t1 = threading.Thread(target=dashboard_db_report_vals,
                          args=(store_id, start_date, end_date, period, res1, start_date_compar, end_date_compar))
    t1.start()
    # t2 = threading.Thread(target=dashboard_google_report_vals, args=(store_id, start_date, end_date, res2))
    # t2.start()
    # res3 = reports.num_orders_by_weekday(store_id, end_date)
    t1.join()
    # t2.join()

    res1 = [[]] if len(res1) == 0 else res1
    res2 = [[]] if len(res2) == 0 else res2

    report_vals = res1[0] + res2[0]
    # report_vals.append(res3)

    # if store_id == 3:
    #     funnel = conversion_funnel(store_id)
    #     report_vals.append(funnel)

    return jsonify(report_vals)


@main.route('/orders', methods=['POST'])
def post_new_order():
    cnxn = db.Database()

    order_data = {
        'store_id': int(request.json['store_id']),
        'order_id': request.json['order_id'],
        'order_date': request.json['order_date'],
        'tot_sum': float(request.json['tot_sum']),
        'client_id': request.json.get('client_id').strip() if request.json.get('client_id') != None else None,
        # remove whitespace from edges
        'email_address': request.json.get('client_email'),
        'first_name': request.json.get('first_name'),
        'last_name': request.json.get('last_name'),
        'town': request.json.get('town'),
        'country': request.json.get('country'),
        'post_code': request.json.get('post'),
        'delivery_cost': request.json.get('delivery_cost'),
        'coupon_code': request.json.get('coupon_code'),
        'device_type': request.json.get('device_type'),
        'order_source': request.json.get('order_source')
    }

    cnxn.insert_new_order(order_data)
    # prods = request.json['products']
    prods = request.json
    prods = prods['products']

    # insert each product into db (products table)
    prod_ids = set()
    for prod in prods:
        prod_data = {
            'store_id': order_data['store_id'],
            'order_id': order_data['order_id'],
            # 'order_date' : order_data['order_date'],
            'prod_id': prod.get('prod_id'),
            'prod_name': prod.get('prod_name'),
            'catalog_num': prod.get('catalog_num'),
            'item_price': float(prod['item_price']),
            'num_items': int(prod['num_items']),
            'manufacturer_name': prod.get('manufacturer_name')
        }

        cnxn.insert_new_order_prod(prod_data)

        # insert product into db TODO:Add to the managment & front when add new product

        # if prod_data['prod_id'] not in prod_ids:
        #     prod_ids.add(prod_data['prod_id'])
        #     del prod_data['catalog_num']
        #     del prod_data['item_price']
        #     del prod_data['num_items']
        #     del prod_data['manufacturer_name']
        #     prod_data['order_date'] = order_data['order_date']

        #     cnxn.update_prods(prod_data)

    cnxn.commit()
    return "Order inserted."


@main.route('/clients', methods=['POST'])
def post_clients():
    store_id = request.json.get('store_id')
    client_id = request.json.get('client_id')
    email = request.json.get('email')
    first_name = str(request.json.get('first_name'))
    last_name = str(request.json.get('last_name'))
    username = request.json.get('username')
    action = request.json.get('action')  # register or update
    action_date = js_date_to_sql_date(request.json.get('action_date'))
    cnxn = db.Database()
    cnxn.insert_or_update_client(store_id, action, client_id, email, first_name, last_name, username, action_date)
    cnxn.commit()
    return "OK"


@main.route('/clients/<id>')
def client_details(id):
    store_id = request.args.get("storeid")
    client_id = id
    cnxn = db.Database()
    client_details = cnxn.client_details(store_id, client_id)
    return jsonify(client_details)


@main.route('/checksbyage/<age>')
def checks_by_age(age):
    store_id = request.args.get("storeid")
    cnxn = db.Database()
    checks = cnxn.checks_by_age(store_id, age)
    return jsonify(checks)


@main.route('/cartactions', methods=['POST'])
def post_cart_action():
    store_id = request.json.get('store_id')
    prod_id = request.json.get('prod_id')
    prod_name = request.json.get('prod_name')
    manufacturer_name = request.json.get('manufacturer_name')
    item_price = request.json.get('item_price')
    num_items = request.json.get('num_items')
    cookie = request.json.get('cookie')
    action_code = cart_actions_name_to_code[request.json.get('action')]  # add/remove
    email = request.json.get('email')
    action_date = js_date_to_sql_date(request.json.get('action_date'))
    cnxn = db.Database()
    cnxn.insert_cart_action(store_id, prod_id, prod_name, manufacturer_name, item_price, num_items, cookie, action_code,
                            email, action_date)
    cnxn.commit()
    return "OK"


@main.route('/prodviews', methods=['POST'])
def post_prod_views():
    store_id = request.json.get('store_id')
    prod_id = request.json.get('prod_id')
    prod_name = request.json.get('prod_name')
    manufacturer_name = request.json.get('manufacturer_name')
    cookie = request.json.get('cookie')
    email = request.json.get('email')
    action_date = js_date_to_sql_date(request.json.get('action_date'))
    cnxn = db.Database()
    cnxn.insert_prod_view(store_id, prod_id, prod_name, manufacturer_name, cookie, email, action_date)
    cnxn.commit()
    return "OK"


@main.route("/dashboard/reports", methods=["GET"])
def get_available_dash_reports():
    try:
        store_id = int(request.args.get("storeid"))
    except TypeError:
        store_id = request.get_json()
        store_id = int(store_id.get('storeid'))

        # store_id = int(request.args.get("storeid"))

    cnxn = db.Database()

    crsr = cnxn.crsr
    sql = """
        select
            pos_id,
            pos_name
        from point_of_sales
        where store_id = ?
    """
    crsr.execute(sql, store_id)
    pos = dict()
    rows = crsr.fetchall()
    for row in rows:
        pos[row.pos_name] = row.pos_id

    sql = """
		select
			avail.report_id,
			reports.category,
			reports.report_name as name, --Changed to "name" for Yossef's request
			reports.report_desc,
            reports.type,
			case when dash.report_id is not null then 1 else 0 end as is_current,
            options,
            is_agg
		from
			available_reports_by_store as avail
			left join global_reports as reports
				on reports.report_id = avail.report_id
			left join dashboards as dash
                on
                    dash.store_id = ?
                    and dash.report_id = avail.report_id
		where avail.store_id = ?
    """
    params = store_id, store_id
    crsr.execute(sql, params)
    rows = crsr.fetchall()
    out = []
    for row in rows:
        temp_dict = {
            "report_id": row.report_id,
            "category": row.category,
            "name": row.name,
            "report_desc": row.report_desc,
            "type": row.type,
            "is_current": row.is_current,
            "options": json.loads(row.options),
            "is_agg": row.is_agg
        }
        if "pos_ids" in temp_dict["options"]:
            temp_dict["options"]["pos_ids"] = pos
        out.append(temp_dict)

    return jsonify(out)


@main.route("/dashboard/reports/current", methods=["PUT"])
def current_reports():
    store_id = request.args.get("storeid")
    cnxn = db.Database()
    reports = request.get_json()
    cnxn.put_dashboard_reports(store_id, reports)
    cnxn.commit()

    return "OK"


@main.route('/reports/<int:report_id>', methods=["POST"])
def report_val(report_id):
    cnxn = db.Database()
    params = {
        "store_id": request.json.get("store_id", 15),
        "start_date": request.json.get("start_date"),
        "end_date": request.json.get("end_date"),
    }
    report=cnxn.excute_proc("get_report_by_id",report_id)[0]
    proc_name=report.get("func_name","")
    data=cnxn.excute_proc(proc_name,params)
    # data.append([report])
    print(data)
    return jsonify(data)

    # options = json.loads(row.options)
    # print(row)
    # params = {
    #     "dates": request.json.get("dates"),
    #     "start_date": request.json.get("start_date"),
    #     "end_date": request.json.get("end_date")
    # }
    # for param_name, param_desc in options.items():
    #     if param_name == "days":
    #         values = request.json[param_name]
    #         values = [str(weekday + 1) for weekday in values]
    #         values = ",".join(values)
    #         params[param_name] = values
    #     elif param_name == "store_ids" or param_name == "pos_ids":  # <=============Rom addition for multiple stores
    #         params[param_name] = ','.join([str(i) for i in request.json[param_name]])
    #     elif (type(param_desc) is str and param_desc == "array") or type(param_desc) is dict:
    #         values = request.json[param_name]
    #         values = [f"'{element}'" for element in values]
    #         values = ",".join(values)
    #         params[param_name] = values
    #     else:
    #         params[param_name] = request.json[param_name]
    #
    # out = {
    #     "report_id": row.report_id,
    #     "category": row.category,
    #     "name": row.report_name,
    #     "report_desc": row.report_desc,
    #     "type": row.type,
    #     "type_additions": row.type_additions,
    #     "has_onclick": 1 if row.report_id_onclick is not None else 0,
    #     'is_agg': row.is_agg,
    #     "value": None,
    #     #  'report_calc':None
    # }
    #
    # proc_name = row.func_name
    # val, graphs = cnxn.query(proc_name, params, is_report=True)
    # out["value"] = val
    # # out['graphs']=graphs
    #
    # graph_info = row.graph_cols
    # '''
    # if graph_info:
    #     graph_all={}
    #
    #     graph_info=json.loads(graph_info)
    #
    #     print(graphs)
    #     print('#'*200)
    #     for keys in graphs:
    #         if type(keys) is int:
    #             print(keys)
    #             graph_tmp={}
    #             graph_tmp['info']=(graph_info.get(str(keys),None))
    #             tmp_df=pd.DataFrame(graphs[keys])
    #             graph_tmp['data']=graphs[keys]
    #             graph_all[keys]=graph_tmp
    #
    #     out['graphs']=graph_all
    # '''
    #
    # cols = row.summarize_cols
    # if cols:
    #     cols = json.loads(cols)
    #     cols = cols.get('cols')
    #     df = pd.DataFrame(val)
    #
    #     if df.shape[0]:
    #         report_stat = df[cols].describe().round(2).fillna(0).to_dict()
    #         report_sum = df[cols].sum().to_dict()
    #         for col_name in cols:
    #             report_stat[col_name]['sum'] = report_sum.get(col_name)
    #         out['descriptive_statistics'] = report_stat
    #
    #         ######### GRAPHS FOR REPORT #############
    #         if graph_info:
    #             graph_info = json.loads(graph_info)
    #             graph_all = {}
    #
    #             trend_2y_axis = graph_info.get('trend_2y_axis', None)
    #             if trend_2y_axis:
    #                 groupby_col, y1, y2 = trend_2y_axis.get('cols', [None] * 3)
    #                 if groupby_col:
    #                     graph_tmp = {}
    #                     df_1 = df.groupby([groupby_col])[y1].agg(['sum']).reset_index()
    #                     df_2 = df.groupby([groupby_col])[y2].agg(['sum']).reset_index().rename(columns={'sum': 'count'})
    #
    #                     graph_tmp['data'] = df_1.merge(df_2, on=groupby_col, how='inner').rename(
    #                         columns={groupby_col: 'x', 'sum': 'y1', 'count': 'y2'}).to_dict('records')
    #
    #                     graph_tmp['data_header'] = {'x': groupby_col, 'y1': y1 + '_sum', 'y2': y2 + '_count'}
    #
    #                     graph_tmp['info'] = trend_2y_axis.get('info', None)
    #
    #                     graph_tmp['two_y_axis'] = True
    #
    #                     graph_all[len(graph_all) + 1] = graph_tmp
    #
    #             percentile_graph = graph_info.get('percentile_graph', None)
    #             if percentile_graph:
    #                 groupby_col, y = percentile_graph.get('cols', [None] * 2)
    #                 if groupby_col:
    #                     graph_tmp = {}
    #                     df_tmp = df.copy()
    #                     num_of_buns = int(percentile_graph.get('num_of_bins', 10))
    #                     agg_func = percentile_graph.get('agg_func', 'count')
    #                     df_tmp[groupby_col] = pd.cut(df_tmp[groupby_col], 10)
    #                     df_tmp[groupby_col] = df_tmp[groupby_col].apply(lambda x: (x.right + x.left) / 2)
    #                     # change to meadin
    #                     graph_tmp['data'] = df_tmp.groupby([groupby_col])[y].agg([agg_func]).reset_index().rename(
    #                         columns={groupby_col: 'x', agg_func: 'y'}).to_dict('records')
    #
    #                     graph_tmp['data_header'] = {'x': groupby_col, 'y': groupby_col + '_' + agg_func}
    #
    #                     graph_tmp['info'] = percentile_graph.get('info', None)
    #
    #                     graph_all[len(graph_all) + 1] = graph_tmp
    #
    #             disrbution = graph_info.get('disrbution', None)
    #             if disrbution:
    #                 for item in disrbution:
    #                     groupby_col, y = item.get('cols', [None] * 2)
    #                     if groupby_col:
    #                         graph_tmp = {}
    #                         agg_func = item.get('agg_func', 'count')
    #                         if item.get('normalize', False):
    #                             tmp_df = df.groupby([groupby_col])[y].agg([agg_func])
    #                             col_sum = tmp_df[[agg_func]].sum().values
    #                             tmp_df[agg_func] = tmp_df[agg_func].div(col_sum[0]).multiply(100)
    #                             graph_tmp['data'] = tmp_df.reset_index().rename(
    #                                 columns={groupby_col: 'x', agg_func: 'y'}).to_dict('records')
    #
    #                         else:
    #                             graph_tmp['data'] = df.groupby([groupby_col])[y].agg([agg_func]).reset_index().rename(
    #                                 columns={groupby_col: 'x', agg_func: 'y'}).to_dict('records')
    #
    #                         graph_tmp['data_header'] = {'x': groupby_col, 'y': groupby_col + '_' + agg_func}
    #                         graph_tmp['info'] = item.get('info', None)
    #
    #                         graph_all[len(graph_all) + 1] = graph_tmp
    #
    #             top_num_trend = graph_info.get('top_num_trend', None)
    #             if top_num_trend:
    #                 cols = top_num_trend.get('cols', None)
    #
    #                 if cols:
    #                     agg_func = top_num_trend.get('agg_func', 'count')
    #                     num_of_top_items = top_num_trend.get('num_top', 2)
    #                     graph_tmp = {}
    #
    #                     df1 = df.copy()
    #                     if len(cols) == 4:
    #                         x_axis, hour, groupby_col, y = cols
    #
    #                         df1['x'] = pd.to_datetime(df1.pop(x_axis)) + pd.to_timedelta(df1.pop(hour), unit='H')
    #                     else:
    #                         x_axis, groupby_col, y = cols
    #                         df1.rename(columns={x_axis: 'x'}, inplace=True)
    #
    #                     top_items = set(df1.groupby([groupby_col])[y].agg(['count']).sort_values('count',
    #                                                                                              ascending=False).reset_index().loc[
    #                                     :(num_of_top_items - 1), groupby_col].values)
    #
    #                     df1 = df1.loc[df1.product_name.isin(top_items)].groupby(['x', groupby_col])[y].agg(
    #                         [agg_func]).reset_index()
    #
    #                     base_df = pd.DataFrame({'x': (df1['x'].unique())})
    #                     for index, item in enumerate(top_items, start=1):
    #                         base_df = base_df.merge(df1.loc[df1.product_name == item, ['x', agg_func]].rename(
    #                             columns={agg_func: 'y' + str(index)}), on='x')
    #
    #                     if len(cols) == 4:
    #                         base_df.loc[:, 'x'] = base_df.x.dt.strftime('%d.%m.%y %H:00')
    #                     # else:
    #                     # base_df.loc[:,'x']=base_df.x.dt.strftime('%d/%m')
    #
    #                     graph_tmp['data'] = base_df.to_dict('records')
    #
    #                     del base_df, df1
    #
    #                     graph_tmp['data_header'] = {'x': x_axis, **{('y' + str(i)): value for i, value in
    #                                                                 enumerate(list(top_items), start=1)}}
    #
    #                     graph_tmp['info'] = top_num_trend.get('info', None)
    #
    #                     print('#' * 100)
    #                     graph_all[len(graph_all) + 1] = graph_tmp
    #
    #             out['graphs'] = graph_all
    #
    # if row.report_id == 1:
    #     df = pd.DataFrame(val)
    #     df['total_refund'] = df[['refund_amount', 'total_count']].apply(lambda x: x.refund_amount * x.total_count,
    #                                                                     axis=1)
    #     agg_res = df.sum().to_dict()
    #     agg_res.pop('date')
    #     agg_res.pop('refund_amount')
    #     agg_res['avg'] = round(agg_res.get('total_refund') / agg_res.get('total_count'), 2)
    #     agg_res['total_refund'] = round(agg_res['total_refund'], 2)
    #     out['report_calc'] = agg_res
    #
    #     # first_g=df.groupby(['comments'])['refund_amount'].sum().to_dict()
    #     # forth_graph=df.groupby('date')['refund_amount'].agg(['sum','count']).to_dict()
    #     # df.refund_amount=pd.cut(df.refund_amount,10)
    #     # second_graph=df.groupby(['refund_amount'])['total_count'].sum().to_frame().reset_index()
    #     # second_graph.refund_amount=second_graph.refund_amount.apply(lambda x: (x.right+x.left)/2)
    #     # second_graph=second_graph.to_dict()
    #     # third_graph=df.groupby('total_count')['comments'].count().to_frame().to_dict()
    #     # out['graphs']={1:first_g,2:second_graph,3:third_graph,4:forth_graph}
    #
    # if row.report_id == 2:
    #     df = pd.DataFrame(val)
    #     agg_res = df[['revenue_amount', 'num_orders']].sum().to_dict()
    #     agg_res['avg'] = round(agg_res.get('revenue_amount') / agg_res.get('num_orders'), 2)
    #     agg_res['revenue_amount'] = round(agg_res['revenue_amount'], 2)
    #
    #     out['report_calc'] = agg_res
    #
    # return simplejson.dumps(out)  # json.dumps(out)


def report_tldr(df, report_info):
    return None


def dashboard_db_report_vals(store_id, start_date, end_date, period, res, start_date_compar, end_date_compar):
    cnxn = db.Database()
    db_report_ids = cnxn.dashboard_db_report_ids(store_id)

    report_vals = db.MultipleReports()
    threads = set()
    for report_meta in db_report_ids:
        t = threading.Thread(target=db.db_report_val_thread, args=(
            report_meta['report_id'], store_id, start_date, end_date, period, report_vals, report_meta['to_compare'],
            start_date_compar, end_date_compar))
        threads.add(t)
        t.start()

    for t in threads:
        t.join()

    res.append(report_vals.to_json())


# def dashboard_google_report_vals(store_id, start_date, end_date, res):
#     cnxn = db.Database()
#     google_reports = cnxn.google_reports(store_id)
#     if google_reports is not None:
#         get_report_data_from_google_analytics(start_date.str_to_google(), end_date.str_to_google(), google_reports)
#         res.append(google_reports)

@main.route('/dashboard/reports/<int:report_id>/onclick')
def dashboard_report_onclick(report_id):
    store_id = request.args.get("storeid")
    accum = request.args.get('accum')
    period = request.args.get('period')

    num_days = period_to_days[period]
    end_date = dates.curr_date()

    cnxn = db.Database()

    if accum == 'false':
        start_date = dates.date_by_days(end_date, -num_days)
    elif accum == 'true':
        if period == 'd':
            start_date = dates.date_start_of_day(end_date)
        elif period == 'w':
            start_date = dates.date_start_of_week(end_date)
        elif period == 'm':
            start_date = dates.date_start_of_month(end_date)
        elif period == 'q':
            start_date = dates.date_start_of_quarter(end_date)

    val = cnxn.onclick_report_val(report_id, store_id, start_date, end_date, period)
    return jsonify(val)


# def get_report_data_from_google_analytics(start_date, end_date, reports):
#     #return get_metrics(num_days, reports)
#     get_metrics(start_date, end_date, reports)

def js_date_to_sql_date(date):
    date = date.replace('T', ' ')
    date = date.replace('Z', '')
    return date


# def conversion_funnel(store_id):
#     period = None
#     start_date = dates.curr_date()
#     start_date.add_days(-30)
#     end_date = dates.curr_date()
#     # num_users = get_metric(start_date.str_to_google(), end_date.str_to_google(), ['ga:users']) #get number of users
#     cnxn = db.Database()
#     num_registers = cnxn.db_report_val(61, store_id, start_date, end_date, period)['value']
#     num_users_added_to_cart = cnxn.db_report_val(62, store_id, start_date, end_date, period)['value']
#     num_clients_ordered = cnxn.db_report_val(5, store_id, start_date, end_date, period)['value']
#     res = {
#         'report_id' : 63,
#         'num_users' : num_users,
#         'num_registers' : num_registers,
#         'num_users_added_to_cart' : num_users_added_to_cart,
#         'num_clients_ordered' : num_clients_ordered
#     }
#     return res

def dates_by_period(period, is_accum):
    end_date = dates.curr_date()
    num_days = period_to_days[period]
    if not is_accum:
        start_date = dates.date_by_days(end_date, -num_days)
    else:
        if period == 'd':
            start_date = dates.date_start_of_day(end_date)
        elif period == 'w':
            start_date = dates.date_start_of_week(end_date)
        elif period == 'm':
            start_date = dates.date_start_of_month(end_date)
        elif period == 'q':
            start_date = dates.date_start_of_quarter(end_date)
        elif period == 'y':
            start_date = dates.date_start_of_year(end_date)
    return start_date, end_date


def dates_by_period_for_comparison(period, is_accum):
    orig_start_date, orig_end_date = dates_by_period(period, is_accum)
    if is_accum:
        return dates.date_start_of_prev_period(orig_end_date, period), dates.date_start_of_period(orig_end_date, period)
    delta = orig_end_date.delta(orig_start_date)
    return dates.date_by_delta(orig_start_date, -delta), dates.date_by_delta(orig_end_date, -delta)


###############################################################
################        API FOR FRONT         #################
###############################################################
###############################################################
################        API FOR FRONT         #################
###############################################################


@main.route("/front_tbl", methods=["POST"])
def get_back_details():
    info = request.get_json()
    print(info)
    cnxn = db.Database()

    res = {
        'OrganizationalStructure': get_dm_org_struct(cnxn.cnxn),
        'Reports': get_all_reports(cnxn.cnxn)
    }

    return res


@main.route("/organizational_structure", methods=["POST"])
def get_org_struct():
    info = request.get_json()
    cnxn = db.Database()
    return get_dm_org_struct(cnxn.cnxn)


@main.route("/reports_info", methods=["POST"])
def get_reports_info():
    cnxn = db.Database()
    cur = cnxn.crsr
    cur.execute(
        'SELECT report_id,category,type,report_desc,report_name,type_additions,report_id_onclick FROM global_reports')
    rows = cur.fetchall()
    keys = [x[0] for x in cur.description]
    json_data = []

    for row in rows:
        item = dict()
        for q in range(len(keys)):
            item[keys[q]] = row[q]
        json_data.append(item)
        # json_data.append(dict(zip(row_headers, result)))

    # return json.dumps(json_data)
    # res = json.loads(get_all_reports(cnxn.cnxn))
    res = get_all_reports(cnxn.cnxn)

    return json.dumps(res)
