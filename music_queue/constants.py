import os

AUTHORIZATION_SCOPE = ['https://www.googleapis.com/auth/spreadsheets.readonly']

GOOGLE_OAUTH_CONFIG = os.environ.get("GOOGLE_OAUTH_CONFIG", default=False)
