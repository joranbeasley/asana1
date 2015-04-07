from collections import defaultdict
import json
import datetime
from flask import Blueprint, Session, request
from flask.ext.login import login_required, current_user
from flask.views import View
import time
import itertools
from asana_helpers import asana_api
from date_util2 import time2dt, week_range, createDateString
from models import TimeLogged
from dateutil.parser import parse as date_parse

api = Blueprint("api",__name__)
def toggle_task(task_id):
    return json.dumps({
        "status":"success",
        "message":"OK"

    })
class HoursDict:
    def sort_items(self,time_instances,granularity=None):
        def item_day(itm):
            tm = time2dt(itm.start_time)
            return tm.year,tm.month,tm.day
        def item_week(itm):
            tm = time2dt(itm.start_time)
            return tm.year,tm.isocalendar()[1]
        def item_month(itm):
            tm = time2dt(itm.start_time)
            return tm.year,tm.month
        def item_year(itm):
            tm = time2dt(itm.start_time)
            return tm.year
        if granularity is None:granularity="day week month year"
        for key in granularity.split():
            print "xxxkeyxxx:",key
            g = itertools.groupby(time_instances,locals().get("item_%s"%key))
            items_sorted = [(k,list(v)) for k,v in g]
            print len(items_sorted),zip(*items_sorted)[0]
            if len(items_sorted) <= 12 or key == granularity:
                print "KEY:",key
                return items_sorted,key
        return items_sorted,key
    def __getitem__(self,item):
        return self.data[item]
    def __setitem__(self,key,value):
        self.data[key]=value
    def to_json(self):
        return json.dumps(self.data)

    def report_data(self,data=None,granularity=None):

        def dump_data(data,format,is_cal=False):
            x=["x"]
            tasks = {}
            for i,(k,v) in enumerate(data):
                if is_cal:
                    tasks[v[0].start_time]=sum([t.duration for t in v])/3600.0
                    continue
                x.append(createDateString(v[0].start_time,format))
                for t in v:
                    if t.task.name not in tasks:
                        tasks[t.task.name] = [t.task.name] + [0] * len(data)
                    try:
                        tasks[t.task.name][i+1] += t.duration
                    except:
                        tasks[t.task.name][i+1] = t.duration
            if is_cal:
                return tasks
            return [x]+tasks.values(),tasks.keys()
        if data is None:
            data = self.sorted_data
        if granularity is None:
            granularity=self.key
        else:
            if granularity.startswith("cal_"):
                return dump_data(data,granularity[4:],True)
        return dump_data(data,granularity)


    def __init__(self,time_instance_list):
        HoursCollection = lambda:defaultdict(HoursCollection)
        self.data = time_instance_list
        self.sorted_data,self.key = self.sort_items(time_instance_list)
        self.calendar_data,days = self.sort_items(time_instance_list,"day")


def getHours():
    session = Session()
    try:
        start = date_parse(request.args.get("start","1979-04-01T07:00:00.000Z"))
    except:
        start = date_parse("1979-04-01T07:00:00.000Z")
    end = request.args.get("stop",None)
    try:
        if end:end = date_parse(end)
    except:
        end = None
    print start
    user_id = current_user.id
    return HoursDict(TimeLogged.times_between(start,end,user_id=user_id))
class HoursAPI:
    @classmethod
    def register(cls,mod,base_partial="/api"):
        def call_api(args):
            args = args.split("/")
            print "ARGS:",args
            return getattr(HoursAPI(),args[0])(*args[1:])
        url = "%s/<path:args>"%base_partial
        mod.add_url_rule(url, view_func=login_required(call_api))

    def tasks(self,id=None):
        if id is None:
            return json.dumps(asana_api.my_current_tasks())
        return toggle_task(id)

    def calendarData(self):
        data = getHours()
        cal_data = data.report_data(data.calendar_data,"cal_day")
        return json.dumps(cal_data)
    def chartData(self):
        data = getHours()
        bar_data,bar_groups = data.report_data()
        return json.dumps({"data":{"columns":bar_data,"groups":[bar_groups],"type":"bar","x":"x"},
                           "axis": {"x": {"type": "categorized"}}})



                    #d = defaultdict()
                    #for v in values:







HoursAPI.register(api)
