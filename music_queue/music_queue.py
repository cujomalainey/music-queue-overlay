from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, session
)

from music_queue import db
from music_queue.constants import *
from music_queue.models import YTVideo
from music_queue.oauth import build_credentials, is_logged_in

bp = Blueprint('music_queue', __name__)

def validate_queue():
    length = request.form['length']
    sheet = request.form['sheet']
    if not length:
        flash('Queue length is required.')
        return False
    if not is_logged_in():
        flash('Google sheets access required')
        return False
    if sheet:
        return validate_sheet(sheet)
    flash('Sheet URL is required.')
    return False

def validate_sheet(url):
    pass

def register_queue():
    pass

@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST' and validate_queue():
        register_queue()
        return flask.redirect(url_for(".music_queue"), CODE=302)

    login_state = is_logged_in()
    return render_template('music_queue/index.html', login_state=login_state)

@bp.route('/queue', methods=('GET', 'POST'))
def music_queue():
    if not session['active']:
        return redirect()
    if request.method == "POST":
        pass
        # handle JSON request
    return render_template('music_queue/queue.html', show_total=session['show_total'], length=session['length'])


    # task = YTVideo.query.get(id)
    # if task != None:
    #     db.session.delete(task)
    #     db.session.commit()
    # return redirect(url_for('music_queue.index'))
