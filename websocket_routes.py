from flask.ext.socketio import SocketIO, emit,join_room
from flask_login import current_user
from flask import request
import time
import itertools
from task_worker import get_tasks_async
import functools
import json
import sys
from models import ActiveTasks, TimeLogged, Task, Session

socketio = SocketIO()
def initApp(app):
    socketio.init_app(app)
    return socketio

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated() and (current_user.is_anonymous() or not current_user.reauthenticate()):
            emit("error","authentication error")
            request.namespace.disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

connected_clients = {}
client_map = {}
def get_celery_worker_status():
    ERROR_KEY = "ERROR"
    try:
        from celery.task.control import inspect
        insp = inspect()
        d = insp.stats()
        if not d:
            d = { ERROR_KEY: 'No running Celery workers were found.' }
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the RabbitMQ server is running.'
        d = { ERROR_KEY: msg }
    except ImportError as e:
        d = { ERROR_KEY: str(e)}
    return d

@socketio.on("connect",namespace="/s")
@authenticated_only
def on_connect():
    join_room(current_user.email)
    try:
        connected_clients[current_user.email].append(request.namespace)
    except KeyError:
        connected_clients[current_user.email] = [request.namespace]
    emit('connected', {'user': current_user.email,"count":len(connected_clients[current_user.email])},room=current_user.email)

@socketio.on("disconnect",namespace="/s")
@authenticated_only
def on_disconnect():
    print "%s is leaving"%current_user.email
    connected_clients[current_user.email].remove(request.namespace)
    emit('disconnected', {'user': current_user.email,"count":len(connected_clients[current_user.email])},room=current_user.email)

@socketio.on("register",namespace="/s")
@authenticated_only
def register_client():
    emit("error","register is no longer supported")
@socketio.on("stop_current","/s")
@authenticated_only
def stop_current_task():
    try:
        old_task = ActiveTasks.get(ActiveTasks.user_id == current_user.id)[0]
        old_id = old_task.task_id
        print "OLD ID:",old_id
        start_time = old_task.start_time
    except:
        return None
    tl = TimeLogged.close_active_task(old_task)
    return int(old_id)

@socketio.on("activate_task","/s")
@authenticated_only
def activate_task(task_id):
    if stop_current_task() == task_id:
        emit("active_task","-1",room = current_user.email)
        print "KILLED!"
    else:
        current_task = ActiveTasks(current_user.id,task_id)
        current_task.save()
        emit("active_task",task_id,room = current_user.email)

@socketio.on("get_tasks","/s")
@authenticated_only
def get_tasks(data):
    emit("request_initialized","OK")
    job = get_tasks_async()
    try:
        current_task = ActiveTasks.get(ActiveTasks.user_id == current_user.id)[0]
        print "Active:",current_task
    except:
        current_task = None
    while not job.ready():
        time.sleep(0.5)
    def save_task_return_orig(session,task_data):
        task = Task.from_json(task_data)
        session.merge(task)
        session.commit()

        task_data["time"] = "%0.2fh"%(task.total_seconds()/3600.0)
        return task_data
    s = Session()
    results =[save_task_return_orig(s,e) for d in job.get() for e in d.get("data",[])]
    s.close()

    emit("all_task",results,)
    if current_task:emit("active_task",current_task.task_id)

if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    socketio = initApp(app)
    socketio.run(app,port=5001)