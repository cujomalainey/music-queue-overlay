from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, session
)

from music_queue import db
from music_queue.constants import *
from music_queue.models import YTVideo

bp = Blueprint('music_queue', __name__)

def validate_queue():
    length = request.form['length']
    sheet = request.form['sheet']
    if not length:
        flash('Queue length is required.')
        return False
    if not session.get(AUTH_TOKEN_KEY):
        flash('Google sheets access required')
        return False
    if sheet:
        return validate_sheet(sheet)
    flash('Sheet URL is required.')
    return False

def validate_sheet(url):
    


def handle_queue_request():
    if session.get(AUTH_TOKEN_KEY):
    else:
        return flask.redirect("/google/login", CODE=302)

@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST' and validate_queue():
        return flask.redirect("/queue", CODE=302)

    login_state = bool(session.get(AUTH_TOKEN_KEY))
    return render_template('music_queue/index.html', login_state=login_state)

@bp.route('/queue', methods=('GET', 'POST'))
def music_queue():
    if request.method == "POST"
        # handle JSON request
    return render_template('music_queue/queue.html', show_total=session['show_total'], length=session['length'])


    # task = YTVideo.query.get(id)
    # if task != None:
    #     db.session.delete(task)
    #     db.session.commit()
    # return redirect(url_for('music_queue.index'))
