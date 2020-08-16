import flask
import json
import os
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from music_queue.constants import *
from flask import url_for, session, redirect, Blueprint

app = Blueprint('google_auth', __name__)

def is_logged_in():
    return "credentials" in session

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
        **session['credentials'])

@app.route('/google/login')
def login():
    google_config = json.loads(GOOGLE_OAUTH_CONFIG)
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        google_config,
        scopes=AUTHORIZATION_SCOPE)

    flow.redirect_uri = url_for('.google_auth_redirect', _external=True)

    authorization_url, state = flow.authorization_url(
                            access_type='offline',
                            include_granted_scopes='true')

    session['state'] = state

    return redirect(authorization_url, code=302)

@app.route('/google/auth')
def google_auth_redirect():
    google_config = json.loads(GOOGLE_OAUTH_CONFIG)

    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        google_config,
        scopes=AUTHORIZATION_SCOPE,
        state=state)
    flow.redirect_uri = url_for('.google_auth_redirect', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('music_queue.index'), code=302)

@app.route('/google/logout')
def logout():
    if 'credentials' in session:
        del session['credentials']

    return redirect(BASE_URI, code=302)

@app.route('/google/revoke')
def revoke():
  if 'credentials' not in session:
    return redirect(url_for('music_queue.index'), code=302)

  credentials = google.oauth2.credentials.Credentials(
    **session['credentials'])

  revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token },
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')

  del session['credentials']

  if status_code == 200:
    return redirect(url_for('music_queue.index'), code=302)
  else:
    return('An error occurred.')
