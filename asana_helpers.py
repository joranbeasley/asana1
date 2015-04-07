import json
import time
import urllib
import constants
import requests
from flask_login import current_user
from models import Session



class AsanaAPI:
    token_url = constants.TOKEN_ENDPOINT
    redirect_uri = constants.REDIRECT_URI
    def __init__(self,api_key,secret):
        self.api_key = api_key
        self.secret = secret
        if  current_user:
            self.token = current_user.token
            self.tag_name="repeated-%s"%current_user.email.split("@")[0]
            self.tag_id = self.get_tag(self.tag_name) if current_user.tag_id is None else current_user.tag_id
            try:
                current_user.tag_id = self.tag_id
                session = Session()
                session.merge(current_user)
                session.commit()
            except:
                print "xUnable to save Tag ID %rx"%(current_user,)
        else:
            self.token = None

    def __getstate__(self):
        if self.token is None and current_user:
            self.set_current_user(current_user)

        return {
            "api_key":self.api_key,
            "secret":self.secret,
            "token":self.token,
            "tag_name":self.tag_name,
            "tag_id":self.tag_id,

        }

    def set_current_user(self,user):
        self.update_user_data(user.token,"repeated-%s"%user.email.split("@")[0],user.tag_id)
        try:
            user.tag_id = self.tag_id
            session = Session()
            session.merge(current_user)
            session.commit()
        except:
            print "Unable to save Tag ID"
    def update_user_data(self,token,tag_name,tag_id=None):
        self.token = token
        self.tag_name=tag_name
        self.tag_id = self.get_tag(self.tag_name) if tag_id is None else tag_id
    def exchange_token(self,code,code_name):
        data = {"grant_type":"authorization_code" if code_name == "code" else code_name,
                "client_id":self.api_key,
                "client_secret":self.secret,
                "redirect_uri": AsanaAPI.redirect_uri,
                code_name:code}
        result = requests.post(AsanaAPI.token_url,data=data)
        if isinstance(result.json,dict):
            return result.json
        return result.json()
    def post(self,endpoint,**data):
        if self.token is None:
            if current_user:
                self.set_current_user(current_user)
            else:
                return json.dumps({"error":"no user data"})

        if not endpoint.startswith("https://app.asana"):
            endpoint = "https://app.asana.com/api/1.0/%s"%endpoint
        headers = {"Authorization": "Bearer "+self.token}
        if data:
            result =requests.post(endpoint,data=json.dumps(data),headers=headers)
            if isinstance(result.json,dict):
                return result.json
            return result.json()##,data=data_filter).json
    def get(self,endpoint,**data):
        if self.token is None:
            if current_user:
                self.set_current_user(current_user)
            else:
                return json.dumps({"error":"no user data"})
        if not endpoint.startswith("https://app.asana"):
            endpoint = "https://app.asana.com/api/1.0/%s"%endpoint
        token = self.token
        if data:
            endpoint = endpoint + "?" + urllib.urlencode(data)
        headers = {"Authorization": "Bearer "+token}
        print "HEADERS:",headers
        result = requests.get(endpoint,headers = headers)
        if isinstance(result.json,dict):
            return result.json
        return result.json()
    # def __getattr__(self,item):
    #     if item.startswith("get_"):

    def get_tasks(self,**data):
        data["opt_fields"]=data.get("opt_fields","id,completed,assignee,name")
        include_user_hours = data.pop("include_user_hours",False)
        return self.get("tasks",**data)
    def get_tag(self,tag_name):
        if not hasattr(self,"tag_id") or self.tag_id is None:
            tag = self.find_tag_named(tag_name)
            if not tag:
                return None
            self.tag_id = tag["id"]

        return self.tag_id

    def get_tasks_with_tag(self,**data):
        tag = self.get_tag(self.tag_name)
        if not tag:
            return {"data":[]}

        endpoint = "tags/%s/tasks"%(tag,)
        data = {}
        data["opt_fields"]=data.get("opt_fields","id,completed,assignee,name")
        include_user_hours = data.pop("include_user_hours",False)
        return self.get(endpoint,**data)
    def my_workspaces(self):
        return self.get("workspaces")
    def my_current_tasks(self):
        return self.get_tasks(assignee="me",completed_since="now",assignee_status="today",workspace=11847647266616)
    def get_tags(self):
        return self.get("tags")
    def find_tag_named(self,name):
        tags = self.get_tags().pop("data",[])
        for tag in tags:

            result =tag["name"].lower() == name.lower()
            print "CHECK TAG:",tag["name"].lower() ,"=?=",name.lower(),result
            if result:
                return tag



asana_api = AsanaAPI(constants.API_KEY,constants.SECRET)