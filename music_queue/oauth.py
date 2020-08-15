import os
import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from music_queue.constants import *

API_SERVICE_NAME = 'sheets'
API_VERSION = 'v2'


  drive = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

app = flask.Blueprint('google_auth', __name__)

def is_logged_in():
    return "credentials" in flask.session

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

def build_credentials():
    if not is_logged_in():
        raise Exception('User must be logged in')

    return google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

@app.route('/google/login')
def login():
    google_config = json.loads(GOOGLE_CONFIG)
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        google_config,
        scopes=AUTHORIZATION_SCOPE)
    authorization_url, state = flow.authorization_url(
                            access_type='offline',
                            include_granted_scopes='true')

    flow.redirect_uri = flask.url_for('/google/auth', _external=True)

    flask.session['state'] = state

    return flask.redirect(authorization_url, code=302)

@app.route('/google/auth')
def google_auth_redirect():
    google_config = json.loads(GOOGLE_CONFIG)
    state = flask.session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        google_config,
        scopes=AUTHORIZATION_SCOPE,
        state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect("/", code=302)

@app.route('/google/logout')
def logout():
    if 'credentials' in flask.session:
        del flask.session['credentials']

    return flask.redirect(BASE_URI, code=302)

@app.route('/google/revoke')
def revoke():
  if 'credentials' not in flask.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **flask.session['credentials'])

  revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token },
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.' + print_index_table())
  else:
    return('An error occurred.' + print_index_table())
