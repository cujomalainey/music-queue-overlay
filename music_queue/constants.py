import os

ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'

AUTHORIZATION_SCOPE = ['https://www.googleapis.com/auth/spreadsheets.readonly']

AUTH_REDIRECT_URI = os.environ.get("GOOGLE_AUTH_CONFIG", default=False)
