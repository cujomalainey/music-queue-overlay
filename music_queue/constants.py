import os

ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'

AUTHORIZATION_SCOPE ='https://www.googleapis.com/auth/spreadsheets.readonly'

AUTH_REDIRECT_URI = os.environ.get("GOOGLE_AUTH_REDIRECT_URI", default=False)
BASE_URI = os.environ.get("BASE_URI", default=False)
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", default=False)
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", default=False)

AUTH_TOKEN_KEY = 'auth_token'
AUTH_STATE_KEY = 'auth_state'
