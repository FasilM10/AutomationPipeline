# """Hello Analytics Reporting API V4."""

# #from apiclient.discovery import build #pip install google-api-python-client
# #from oauth2client.service_account import ServiceAccountCredentials

# SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
# KEY_FILE_LOCATION = 'boreal-graph-231415-1cf80638268a.json'
# VIEW_ID = '79485123'

# def initialize_analyticsreporting():
#   """Initializes an Analytics Reporting API V4 service object.

#   Returns:
#     An authorized Analytics Reporting API V4 service object.
#   """
#   credentials = ServiceAccountCredentials.from_json_keyfile_name(
#       KEY_FILE_LOCATION, SCOPES)

#   # Build the service object.
#   analytics = build('analyticsreporting', 'v4', credentials=credentials)

#   return analytics


# def get_report(analytics, start_date, end_date, report_names):
#   """Queries the Analytics Reporting API V4.

#   Args:
#     analytics: An authorized Analytics Reporting API V4 service object.
#   Returns:
#     The Analytics Reporting API V4 response.
#   """

#   metrics = []
#   for name in report_names:
#     metrics.append({'expression' : name})

#   return analytics.reports().batchGet(
#     body = {
#       'reportRequests': [{
#         'viewId': VIEW_ID,
#         'dateRanges': [{
#           'startDate': start_date,
#           'endDate': end_date
#         }],
#         'metrics': metrics
#       }]
#     }
#   ).execute()


# def print_response(response):
#   """Parses and prints the Analytics Reporting API V4 response.

#   Args:
#     response: An Analytics Reporting API V4 response.
#   """
#   for report in response.get('reports', []):
#     columnHeader = report.get('columnHeader', {})
#     dimensionHeaders = columnHeader.get('dimensions', [])
#     metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

#     for row in report.get('data', {}).get('rows', []):
#       dimensions = row.get('dimensions', [])
#       dateRangeValues = row.get('metrics', [])

#       for header, dimension in zip(dimensionHeaders, dimensions):
#         print (header + ': ' + dimension)

#       for i, values in enumerate(dateRangeValues):
#         print ('Date range: ' + str(i))
#         for metricHeader, value in zip(metricHeaders, values.get('values')):
#           print (metricHeader.get('name') + ': ' + value)

# def get_metric(start_date, end_date, report_name):
#   analytics = initialize_analyticsreporting()
#   #report_names = get_report_names_from_json(reports)
#   response = get_report(analytics, start_date, end_date, report_name)
#   metric = response["reports"][0]["data"]["rows"][0]["metrics"][0]["values"]
#   metric = metric[0]
#   return metric
#   # for i in range(len(reports)):
#   #   metric_type = response['reports'][0]['columnHeader']['metricHeader']['metricHeaderEntries'][i]['type']
#   #   metric_val = float(response['reports'][0]['data']['rows'][0]['metrics'][0]['values'][i])
#   #   metric_val = format_val(metric_val, metric_type)
#   #   reports[i]['value'] = metric_val
#   #   del reports[i]['func_name']
#   #   del reports[i]['report_desc']
#   #   reports[i]['name'] = reports[i]['report_name']
#   #   del reports[i]['report_name']

# def get_metrics(start_date, end_date, reports):
#   analytics = initialize_analyticsreporting()
#   report_names = get_report_names_from_json(reports)
#   response = get_report(analytics, start_date, end_date, report_names)
#   metrics = response["reports"][0]["data"]["rows"][0]["metrics"][0]["values"]
#   for i in range(len(reports)):
#     metric_type = response['reports'][0]['columnHeader']['metricHeader']['metricHeaderEntries'][i]['type']
#     metric_val = float(response['reports'][0]['data']['rows'][0]['metrics'][0]['values'][i])
#     metric_val = format_val(metric_val, metric_type)
#     reports[i]['value'] = metric_val
#     del reports[i]['func_name']
#     del reports[i]['report_desc']
#     reports[i]['name'] = reports[i]['report_name']
#     del reports[i]['report_name']

# def get_report_names_from_json(reports):
#   report_names = []
#   for report in reports:
#     report_names.append(report['func_name'])
#   return report_names

# def format_val(val, val_type):
#   if val < 100:
#     res = '{:,.2f}'.format(val)
#   else:
#     res = '{:,.0f}'.format(val)
#   if val_type == 'PERCENT':
#     res = res + '%'
#   return res