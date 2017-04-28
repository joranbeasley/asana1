from flask_login import LoginManager, login_user, current_user, logout_user
import constants
import requests
from models import User

login_manager = LoginManager()
login_manager.login_view = "routes.response"

@login_manager.user_loader
def load_user(userid):
    #print "LOAD USER"
    try:
        return User.get(User.id==userid)[0]
    except IndexError:
        return None

# @login_manager.unauthorized_handler
# def unauthorized():
#     # do stuff
#     return "Not Authorized",403

@login_manager.request_loader
def load_user_from_request(request):

    # first, try to login using the api_key url arg
    api_key = request.args.get('api_key')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # next, try to login using Basic Auth
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        user = User.get(User.api_key==api_key)
        if user:
            return user[0]

    # finally, return None if both methods did not login the user
    return None
