import datetime
import dateutil
import copy
import math

class Datetime:
    def __init__(self):
        self.year = 1900
        self.month = 1
        self.day = 1
        self.hours = 0
        self.mins = 0
        self.secs = 0
        self.ms = 0

    def set_from_values(self, year, month, day, hours, mins, secs, ms):
        self.year = year
        self.month = month
        self.day = day
        self.hours = hours
        self.mins = mins
        self.secs = secs
        self.ms = ms
        
    # def set_from_str(self, string):
    #     parts = string.split(" ")
    #     date_parts = parts[0].split("-")
    #     year = int(date_parts[0])
    #     month = int(date_parts[1])
    #     day = int(date_parts[2])
    #     time_parts = parts[1].split(":")
    #     hours = int(time_parts[0])
    #     mins = int(time_parts[1])
    #     sec_parts = time_parts[2].split(".")
    #     secs = int(sec_parts[0])
    #     ms = int(sec_parts[1])
    #     offset_parts = parts[2].split(":")
    #     offset = int(offset_parts[0])

    #     self.set_from_values(year, month, day, hours, mins, secs, ms, offset)

    # def set_from_datetime_obj(self, dtobj):
    #     self.year = dtobj.year
    #     self.month = dtobj.month
    #     self.day = dtobj.day
    #     self.hours = dtobj.hour
    #     self.mins = dtobj.minute
    #     self.secs = dtobj.second
    #     self.ms = microsecond

    # def __str__(self):
    #     year = str(self.year)
    #     month = self.str_month()
    #     day = self.str_day()
    #     hours = self.str_hours()
    #     mins = self.str_mins()
    #     secs = self.str_secs()
    #     ms = str(self.ms)
        
    #     res = year + "-" + month + "-" + day + " " + hours + ":" + mins + ":" + secs + "." + ms

    #     return res

    def str_to_db(self):
        n = len(str(self.ms))
        
        year = str(self.year)
        month = self.str_month()
        day = self.str_day()
        hours = self.str_hours()
        mins = self.str_mins()
        secs = self.str_secs()
        ms = str(int(round(self.ms/math.pow(10, n), 3)*math.pow(10, 3)))
        res = year + "-" + month + "-" + day + " " + hours + ":" + mins + ":" + secs + "." + ms

        return res

    def str_to_db_date(self):
        year = str(self.year)
        month = self.str_month()
        day = self.str_day()

        res = year + "-" + month + "-" + day

        return res

    def str_to_google(self):
        year = str(self.year)
        month = self.str_month()
        day = self.str_day()
        
        res = year + '-' + month + '-' + day
        
        return res

    def add_days(self, num_days):
        orig_date = datetime.datetime(self.year, self.month, self.day)
        orig_date = orig_date + datetime.timedelta(days=num_days)
        self.year = orig_date.year
        self.month = orig_date.month
        self.day = orig_date.day

    def add_weeks(self, num_weeks):
        num_days = num_weeks * 7
        self.add_days(num_days)

    def add_months(self, num_months):
        pythondt = self.pythondt()
        pythondt = pythondt + dateutil.relativedelta.relativedelta(months=+num_months)
        self.set_by_pythondt(pythondt)

    def add_quarters(self, num_quarters):
        num_months = num_quarters * 3
        pythondt = self.pythondt()
        pythondt = pythondt + dateutil.relativedelta.relativedelta(months=+num_months)
        self.set_by_pythondt(pythondt)

    def add_years(self, num_years):
        num_months = num_years * 12
        pythondt = self.pythondt()
        pythondt = pythondt + dateutil.relativedelta.relativedelta(months=+num_months)
        self.set_by_pythondt(pythondt)

    def pythondt(self):
        year = self.year
        month = self.month
        day = self.day
        hours = self.hours
        mins = self.mins
        secs = self.secs
        ms = self.ms
        
        date = datetime.datetime(year, month, day, hours, mins, secs, ms)

        return date

    def weekday(self):
        pythondt = self.pythondt()
        isoweekday = pythondt.isoweekday()
        weekday = 1 if isoweekday==7 else isoweekday+1

        return weekday

    def set_start_of_day(self):
        self.hours = self.mins = self.secs = self.ms = 0

    def set_start_of_week(self):
        weekday = self.weekday()
        days_to_substract = weekday - 1
        self.add_days(-days_to_substract)
        self.set_start_of_day()

    def set_start_of_month(self):
        self.day = 1
        self.set_start_of_day()

    def set_start_of_quarter(self):
        month = self.month

        if month in (1,2,3):
            new_month = 1
        elif month in (4,5,6):
            new_month = 4
        elif month in (7,8,9):
            new_month = 7
        else:
            new_month = 10
        
        self.month = new_month
        self.set_start_of_month()

    def set_start_of_year(self):
        self.month = 1
        self.set_start_of_month()

    def set_start_of_prev_day(self):
        self.add_days(-1)
        self.set_start_of_day()

    def set_start_of_prev_week(self):
        self.add_weeks(-1)
        self.set_start_of_week()

    def set_start_of_prev_month(self):
        self.add_months(-1)
        self.set_start_of_month()

    def set_start_of_prev_quarter(self):
        self.add_quarters(-1)
        self.set_start_of_quarter()

    def set_start_of_prev_year(self):
        self.add_years(-1)
        self.set_start_of_year()

    def quarter(self):
        month = self.month

        if month in (1,2,3):
            return 1
        if month in (4,5,6):
            return 2
        if month in (7,8,9):
            return 3
        return 4

    def set_current_date(self):
        pythondt = datetime.datetime.utcnow()
        self.set_by_pythondt(pythondt)

    def set_by_pythondt(self, dt):
        self.year = dt.year
        self.month = dt.month
        self.day = dt.day
        self.hours = dt.hour
        self.mins = dt.minute
        self.secs = dt.second
        self.ms = dt.microsecond

    def set_by_date_str(self, dt):
        year = int(dt[:4])
        month = int(dt[4:6])
        day = int(dt[6:])

        self.year = year
        self.month = month
        self.day = day
        self.hours = 0
        self.mins = 0
        self.secs = 0
        self.ms = 0

    def delta(self, start_date):
        start_date = start_date.pythondt()
        end_date = self.pythondt()
        return end_date - start_date

    def add_delta(self, delta):
        pythondt = self.pythondt()
        pythondt = pythondt + delta
        self.set_by_pythondt(pythondt)

    def str_month(self):
        if len(str(self.month)) == 1:
            return "0" + str(self.month)
        return str(self.month)

    def str_day(self):
        if len(str(self.day)) == 1:
            return "0" + str(self.day)
        return str(self.day)

    def str_hours(self):
        if len(str(self.hours)) == 1:
            return "0" + str(self.hours)
        return str(self.hours)

    def str_mins(self):
        if len(str(self.mins)) == 1:
            return "0" + str(self.mins)
        return str(self.mins)

    def str_secs(self):
        if len(str(self.secs)) == 1:
            return "0" + str(self.secs)
        return str(self.secs)

def date_by_days(orig_date, num_days):
    new_date = copy.deepcopy(orig_date)
    new_date.add_days(num_days)

    return new_date

def date_by_pythondt(dtobj):
    new_date = Datetime()
    new_date.set_by_pythondt(dtobj)
    
    return new_date

def date_start_of_day(orig_date):
    new_date = copy.deepcopy(orig_date)
    new_date.set_start_of_day()

    return new_date

def date_start_of_week(orig_date):
    new_date = copy.deepcopy(orig_date)
    new_date.set_start_of_week()

    return new_date

def date_start_of_month(orig_date):
    new_date = copy.deepcopy(orig_date)
    new_date.set_start_of_month()

    return new_date

def date_start_of_quarter(orig_date):
    new_date = copy.deepcopy(orig_date)
    new_date.set_start_of_quarter()

    return new_date

def date_start_of_year(orig_date):
    new_date = copy.deepcopy(orig_date)
    new_date.set_start_of_year()

    return new_date

def curr_date():
    new_date = Datetime()
    new_date.set_current_date()

    return new_date

def date_by_delta(orig_date, delta):
    new_date = copy.deepcopy(orig_date)
    new_date.add_delta(delta)
    return new_date

def date_by_date_str(dt):
    new_date = Datetime()
    new_date.set_by_date_str(dt)
    return new_date

def date_start_of_prev_period(orig_date, period):
    date = copy.deepcopy(orig_date)
    if period == 'd':
        date.set_start_of_prev_day()
        return date
    if period == 'w':
        date.set_start_of_prev_week()
        return date
    if period == 'm':
        date.set_start_of_prev_month()
        return date
    if period == 'q':
        date.set_start_of_prev_quarter()
        return date
    if period == 'y':
        date.set_start_of_prev_year()
        return date

def date_start_of_period(orig_date, period):
    date = copy.deepcopy(orig_date)
    if period == 'd':
        date.set_start_of_day()
        return date
    if period == 'w':
        date.set_start_of_week()
        return date
    if period == 'm':
        date.set_start_of_month()
        return date
    if period == 'q':
        date.set_start_of_quarter()
        return date
    if period == 'y':
        date.set_start_of_year()
        return date