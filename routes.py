import base64
from flask import Blueprint,request,redirect, render_template
from flask_login import login_required, current_user, login_user
import time
import sys
from authentication import login_manager
from asana_helpers import asana_api
import constants
from models import User,Session

bp = Blueprint('routes',__name__)


@bp.route("/")
@login_required
def index():
    print "LOGGED IN:",current_user,current_user.expires_at,time.time()
    return render_template("index.html")


@bp.route("/tasks")
@login_required
def tasks():
    return render_template("tasks.html")


@bp.route("/chart")
@login_required
def show_chart():
    return render_template("charts.html")


@bp.route("/result",methods=["GET"])
def response():
    if not current_user.is_anonymous():
        user_data = asana_api.exchange_token(current_user.refresh_token,"refresh_token")
        next = request.args.get("next","/")
    elif not request.args.get("code"):
        return redirect(constants.AUTH_ENDPOINT+"&state=%s"%request.args.get("next","/"))
    else:
        user_data = asana_api.exchange_token(request.args.get("code"),"code")
        print 'user data:',user_data
        next = request.args.get("state","/")
    s = Session()
    user = User.from_json(user_data)
    s.merge(user)
    login_user(user)
    s.commit()
    return redirect(next)

def on_callback(*args,**kwargs):
    print "GOT CALLBACK!!!"
    print "ARGS:",args
    print "KWARGS:",kwargs
@bp.route("/test")
def test():
    from task_worker import get_tasks_async
    print "OK START JOB"
    t = time.time()
    get_tasks_async(on_callback)
    return "OK JOB STARTED %0.2fs"%(time.time()-t)

@bp.route("/g/<task_id>")
def goto(task_id):
    return redirect("https://app.asana.com/0/{0}/{0}".format(task_id))
