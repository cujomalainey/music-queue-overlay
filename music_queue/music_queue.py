from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, session, jsonify
)
from urllib.parse import urlparse

from music_queue import db
from music_queue.constants import *
from music_queue.models import YTVideo
from music_queue.oauth import build_credentials, is_logged_in

API_SERVICE_NAME = 'sheets'
API_VERSION = 'v2'

# drive = googleapiclient.discovery.build(
#     API_SERVICE_NAME, API_VERSION, credentials=credentials)

bp = Blueprint('music_queue', __name__)

def validate_queue():
    length = request.form['length']
    sheet = request.form['sheet']
    if not is_logged_in():
        flash('Google sheets access required')
        return False
    if sheet:
        return validate_sheet(sheet)
    flash('Sheet URL is required.')
    return False

def validate_sheet(url):
    o = urlparse(url)
    if o.hostname != "docs.google.com":
        flash('Not a google drive url')
        return False
    s = o.path.strip("/").split("/")
    if len(s) < 3:
        flash('Not a link to a sheet')
        return False
    if s[0] != "spreadsheets":
        flash('Not a sheets link')
        return False
    # TODO perform API test
    return True

def register_queue():
    o = urlparse(request.form['sheet'])
    s = o.path.strip("/").split("/")
    session['sheet'] = s[2]
    session['length'] = int(request.form['length']) if request.form['length'] else 0
    session['show_total'] = 'show_total' in request.form

@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST' and validate_queue():
        register_queue()
        return redirect(url_for(".music_queue"), code=302)

    login_state = is_logged_in()
    return render_template('music_queue/index.html', login_state=login_state)

@bp.route('/queue', methods=('GET',))
def music_queue():
    if 'sheet' not in session:
        return redirect(url_for('.index'))

    return render_template('music_queue/queue.html', show_total=session['show_total'], length=session['length'])

@bp.route('/data', methods=('GET',))
def queue_data():
    if 'sheet' not in session:
        return redirect(url_for('.index'))

    return jsonify({"name":"test"})

    # task = YTVideo.query.get(id)
    # if task != None:
    #     db.session.delete(task)
    #     db.session.commit()
    # return redirect(url_for('music_queue.index'))
