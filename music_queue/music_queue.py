from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)

from music_queue import db
from music_queue.models import YTVideo

bp = Blueprint('music_queue', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        name = request.form['name']
        if not name:
            flash('Task name is required.')
        else:
            db.session.add(YTVideo(name=name))
            db.session.commit()

    tasks = YTVideo.query.all()
    return render_template('task_list/index.html', tasks=tasks)

@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    task = YTVideo.query.get(id)
    if task != None:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('task_list.index'))
