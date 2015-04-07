import calendar
from datetime import datetime,timedelta
from dateutil.parser import parse
import pytz
import time
from dateutil.relativedelta import relativedelta
def last_week():
    return datetime.now() - relativedelta(weeks=1)
def last_month():
    return datetime.now() - relativedelta(months=1)
def first_of_this_month():
    return datetime.now().replace(day=1)

def dt2time(dt):
    return time.mktime(dt.timetuple())

def time2dt(timestamp):
    utc_tz = pytz.timezone('US/Pacific')
    return utc_tz.localize(datetime.utcfromtimestamp(timestamp))

def week_range(date):
    """Find the first/last day of the week for the given day.
    Assuming weeks start on Sunday and end on Saturday.

    Returns a tuple of ``(start_date, end_date)``.

    """
    # isocalendar calculates the year, week of the year, and day of the week.
    # dow is Mon = 1, Sat = 6, Sun = 7
    year, week, dow = date.isocalendar()

    # Find the first day of the week.
    if dow == 0:
        # Since we want to start with Sunday, let's test for that condition.
        start_date = date
    else:
        # Otherwise, subtract `dow` number days to get the first day
        start_date = date - timedelta(days=dow)

    # Now, add 6 for the last day of the week (i.e., count up to Saturday)
    end_date = start_date + timedelta(days=6)

    return (start_date, end_date)

def createDateString(dt,fmt):
    if isinstance(dt,(float,int)):
        dt = time2dt(dt)

    if fmt == "week":
        return "%s-%s"%tuple([d.strftime("%d%b") for d in week_range(dt)])
    formats = {"day":"%d%b","month":"%b","year":"%Y"}
    return dt.strftime(formats[fmt])
