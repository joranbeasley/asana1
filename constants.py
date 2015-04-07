import urllib
TOKEN_ENDPOINT = "https://app.asana.com/-/oauth_token"
REDIRECT_URI = "http://104.131.6.197:5000/result"

API_KEY = "22445063095264"
SECRET = "32358d92e9ee3755dc1133cf1bfe72d4"
AUTH_ENDPOINT = "https://app.asana.com/-/oauth_authorize?redirect_uri=%s&response_type=code&client_id=%s"%(urllib.quote(REDIRECT_URI),API_KEY)
