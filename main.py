from flask import Flask
import sys
from routes import bp
from api import api
from authentication import login_manager
from flask.ext.triangle import Triangle


from websocket_routes import initApp, get_celery_worker_status

import gevent_ssl_fix
app = Flask(__name__)
celery_error = get_celery_worker_status().get("ERROR",None)
if celery_error:
    print celery_error
    print "Try : `celery -A task_worker worker -l INFO`"
    sys.exit()
socketio = initApp(app)
app.secret_key = "asanajoran!@#!23123"
app.register_blueprint(bp)
app.register_blueprint(api)
Triangle(app)
login_manager.init_app(app)
app.config["debug"] = True
if __name__ == "__main__":

    app.config["SECRET_KEY"] = app.secret_key
    app.debug=True
    app.config["DEBUG"] = True
    #app.run(debug=True)
    socketio.run(app,host="0.0.0.0")
