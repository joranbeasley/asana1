from celery import Celery,group,chord
from flask.ext.login import current_user
from asana_helpers import asana_api
from models import ActiveTasks,TimeLogged
app = Celery('tasks',backend="redis://localhost", broker='redis://localhost//')





def get_tasks_async():
    if asana_api.token is None:
        if current_user:
            asana_api.set_current_user(current_user)
        else:
            return "error"
    job = group(
        get_primary_tasks.s(asana_api,),
        get_secondary_tasks.s(asana_api,)
    )
    return job()


@app.task
def get_primary_tasks(api):
    print "START PRIMARY!!",api.token
    return api.my_current_tasks()

@app.task
def get_secondary_tasks(api):
    return api.get_tasks_with_tag()