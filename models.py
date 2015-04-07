import hashlib
import datetime
import random
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String,Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref, object_session
import time
from date_util2 import last_week, dt2time, time2dt
from dateutil.parser import parse as date_parse

engine = create_engine('sqlite:///db00000.sql', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
from sqlalchemy.inspection import inspect

class Serializer(object):
    def serialize(self):
        def s(v):
            if hasattr(v,"serialize"):
                return v.serialize()
            if isinstance(v,(list,tuple)) and hasattr(v[0],"serialize"):
                return Serializer.serialize_list(v)
            return v

        return {c: s(getattr(self, c)) for c in inspect(self).attrs.keys()}
    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]
class GetterMixin(Serializer):
    @classmethod
    def get(cls,*args,**kwargs):
        if kwargs and not args:
            args = [getattr(cls,kw)==val for kw,val in kwargs.items()]
        session = Session()
        result = session.query(cls).filter(*args)
        #print "RESULT:",result
        return result.all()
    def save(self):
        session = object_session(self)
        session = Session()
        session.merge(self)
        session.commit()
    def delete(self):
        print "DELETE:",self
        session = object_session(self)
        if not session:
            session = Session()
        session.delete(self)
        session.flush()
        session.commit()
        print "DELETED INSTANCE!"

class Task(Base,GetterMixin):
    __tablename__="tasks"
    id = Column(String,primary_key=True)
    name = Column(String)
    parent_id = Column(String,default=None,nullable=True)
    children = relationship("TimeLogged", backref="task",lazy="dynamic")
    def __init__(self,name,task_id,parent_id=None):
        self.name = name
        self.id = task_id
        self.parent_id = parent_id
    @classmethod
    def from_json(cls,data):
        return Task(data["name"],data["id"])

    def total_seconds(self,start=None,end=None):
        start = (start if start else last_week())
        end = (end if end else datetime.datetime.now())
        if isinstance(start,datetime.datetime):
            start=dt2time(start)
        if isinstance(end,datetime.datetime):
            end=dt2time(end)

        try:
            childs = self.children.filter(TimeLogged.start_time >= start,TimeLogged.end_time >= start).all()
        except:
            childs = TimeLogged.times_for_task(self.id,start,end)
        try:
            return sum([c.duration for c in childs])
        except:
            return 0

class User(Base,GetterMixin):
    __tablename__ = "users"
    id = Column(String,primary_key=True)
    email = Column(String)
    token = Column(String)
    refresh_token = Column(String)
    api_key = Column(String)
    api_password = Column(String)
    expires_at = Column(Integer)
    is_active = lambda *a:1
    is_anonymous = lambda *a:0
    tag_id = Column(String,default=None,nullable=True)
    def get_id(self):
        return self.id
    def is_authenticated(self):
        return time.time() < self.expires_at
    def reauthenticate(self):
        from asana_helpers import asana_api
        user_data = asana_api.exchange_token(self.refresh_token,"refresh_token")
        if user_data["data"]["id"] != self.id:
            return False

        u = User.from_json(user_data)
        session = Session()
        session.merge(u)
        session.commit()
        return True
    def __init__(self,id,email,token,refresh_token):
        self.id = id
        self.email = email
        self.token = token
        if refresh_token:
            self.refresh_token = refresh_token
        self.expires_at = int(time.time()+3400)
        self.api_key = hashlib.sha256(self.email+"randomness").hexdigest()[:10]
        self.api_password = hashlib.md5(self.email+"hasher").hexdigest()
    def __repr__(self):
        return '<User "%s">'%(self.email)
    @classmethod
    def from_json(cls,data):
        return User(data["data"]["id"],data["data"]["email"],data["access_token"],data.pop("refresh_token",None))


class TimeLogged(Base,GetterMixin):

    __tablename__ = "logged_time"
    id = Column(Integer,primary_key=True)
    task_id = Column(String,ForeignKey("tasks.id"))
    user_id = Column(String)
    start_time = Column(Integer)
    end_time = Column(Integer)
    duration = Column(Integer)
    def __repr__(self):
        return "<%s %0.2fh @ %s>"%(self.task_id,self.duration/3600.0,time2dt(self.start_time).strftime("%m%dT%H%M"))
    @classmethod
    def times_between(cls,start=None,end=None,*args,**kwargs):
        start = (start if start else last_week())
        end = (end if end else datetime.datetime.now())
        if isinstance(start,datetime.datetime):
            start=dt2time(start)
        if isinstance(end,datetime.datetime):
            end=dt2time(end)

        return cls.get(TimeLogged.start_time>=start,
                       TimeLogged.end_time<=end,
                       *args,**kwargs)

    @classmethod
    def times_for_task(cls,task_id,start=None,end=None):
        return cls.times_between(start,end,task_id=task_id)


    def __init__(self,task_id,user_id,start_time,end_time=None):
        if not end_time:
            end_time = int(time.time())
        self.task_id = task_id
        self.user_id = user_id
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time
    @classmethod
    def close_active_task(cls,active_task):
        tl = TimeLogged(active_task.task_id,active_task.user_id,active_task.start_time)
        tl.save()
        d = ActiveTasks.__table__.delete(ActiveTasks.user_id == active_task.user_id)
        s = Session()
        s.execute(d)
        s.commit()
        return tl

class ActiveTasks(Base,GetterMixin):
    __tablename__="activetasks"
    user_id = Column(String,ForeignKey("users.id"),primary_key=True)
    task_id = Column(String,ForeignKey("tasks.id"))
    start_time = Column(Integer)
    def __init__(self,user_id,task_id,start_time=None):
        self.user_id = user_id
        self.task_id= task_id
        self.start_time = start_time if start_time else int(time.time())


def random_data(start_date="1/1/2014",end_date="4/6/2015 23:59:59",N=8):
    def createTasks(s,n):
        for i in range(n):
            s.add(Task("Task %d"%i,str(i)))

    start_time = dt2time(date_parse(start_date))
    end_time = dt2time(date_parse(end_date))
    s = Session()
    createTasks(s,N)
    random.seed(str(time.time()))
    task_choices = map(str,range(N))
    c_task=random.choice(task_choices)
    c_start = random.randint(0,3600)+start_time
    c_duration = random.randint(1800,10800)
    while c_start + c_duration < end_time:
        s.add(TimeLogged(c_task,"22443127361963",c_start+c_duration))
        c_start = c_start + c_duration + random.randint(30,1800)
        c_duration = c_duration = random.randint(1800,10800)
        c_task = random.choice(task_choices)
    s.commit()

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    random_data()
