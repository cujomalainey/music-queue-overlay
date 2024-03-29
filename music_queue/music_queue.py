from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, session, jsonify, current_app, make_response
)

from googleapiclient.errors import HttpError
from urllib.parse import urlparse, parse_qs
from random import random
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from time import time
import hashlib
import json

from music_queue import db
from music_queue.constants import *
from music_queue.models import YTVideo, ResultCache
from music_queue.oauth import build_credentials, is_logged_in

import json

API_SERVICE_NAME = 'sheets'
API_VERSION = 'v4'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

YOUTUBE_DOMAINS = ['youtu.be', 'www.youtube.com', 'youtube.com']

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
    sheet_id = s[2]
    session['sheet'] = sheet_id
    session['length'] = int(request.form['length']) if request.form['length'] else 0
    session['show_total'] = 'show_total' in request.form
    # TODO trim db cache

    cache = ResultCache.query.get(sheet_id)
    if (cache):
        db.session.delete(cache)

    cache = ResultCache()
    cache.id = session['sheet']
    cache.pickle = "[]"
    cache.cache_time = datetime.now() - timedelta(hours=1)
    db.session.add(cache)
    db.session.commit()

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
    cache = ResultCache.query.get(session['sheet'])
    if cache and datetime.now() - cache.cache_time <= timedelta(seconds=5):
        full_queue = json.loads(cache.pickle)
        queue = full_queue
        if session['length'] > 0:
            queue = full_queue[:session['length']]
        return jsonify({"queue":queue,
                        "total_queue_size":len(full_queue)})

    service = build(API_SERVICE_NAME, API_VERSION, credentials=build_credentials())
    sheets = service.spreadsheets()
    result = sheets.values().get(spreadsheetId=session['sheet'],
                                 range='B2:B').execute()
    values = result.get('values', [])

    # truncate at display limit
    if session["length"] > 0:
        values = values[:session['length']]

    values = parse_links(values)
    data = jsonify({"total_queue_size":len(values),
                    "queue":values})
    cache.pickle = json.dumps(values)
    cache.cache_time = datetime.now()
    db.session.commit()
    return data

@bp.route('/length', methods=('GET',))
def queue_length():
    if 'sheet' not in session:
        return redirect(url_for('.index'))
    return render_template('music_queue/length.html')

def parse_links(values):
    results = []
    print(values)
    for val in values:
        if not val:
            continue
        # parse url to get id
        val = val[0]
        print(val)
        vid_id = parse_url(val)
        print(vid_id)
        if vid_id is None:
            print("bad parse")
            # return placeholder continue
            results.append(bad_placeholder(val))
            continue

        # check db for cache
        video = YTVideo.query.get(vid_id)
        yesterday_this_time = datetime.now() - timedelta(days=1)
        if video is not None:
            # found in cache, add to list and continue
            if video.pickle:
                print("cache hit")
                results.append(video.pickle)
                continue
            elif video.found_at >= yesterday_this_time:
                print("empty hit")
                results.append(bad_placeholder(val))
            print("cache stale")

        # not found in cache, query api
        vid_info = fetch_video_api(vid_id)
        if vid_info:
            print("api hit")
        else:
            print("api miss")
            vid_info = bad_placeholder(val)
            results.append(vid_info)

        cache_result(vid_id, vid_info)
        results.append(vid_info)

    return results

def bad_placeholder(val):
    h = hashlib.new("md5")
    h.update(val.encode("utf-8"))
    img_url = [
        url_for("static", filename="VectorBRUH.png"),
        url_for("static", filename="VectorLUL.png"),
        url_for("static", filename="VectorNANI.png"),
        url_for("static", filename="VectorRIP.png"),
    ]
    img_index = int(h.hexdigest(), 16) % len(img_url)
    return {"title": "this is not the video you are looking for",
            "channelTitle":"not Vector's",
            "thumbnails": {
                "high":{
                    "url":img_url[img_index]
                }
            }
            }

def parse_url(url):
    # if not youtube then return domain
    domain = get_domain(url)
    if domain not in YOUTUBE_DOMAINS:
        return None

    # parse out id
    if domain == 'youtu.be':
        # parse out last segment
        video_id = get_last_segment(url)
    else:
        # parse out get var
        video_id = get_var_from_url(url)
    return video_id


def fetch_video_api(vid_id):
    try:
        return youtube_search(vid_id)
    except HttpError as e:
        print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
        return None


def cache_result(video_id, result):
    entry = YTVideo()
    entry.id = video_id
    entry.found_at = datetime.now()
    entry.pickle = result
    db.session.add(entry)
    db.session.commit()


def get_domain(url):
    return urlparse(url).netloc


def get_last_segment(url):
    p = urlparse(url)
    return p.path.rsplit("/", 1)[-1]


def get_var_from_url(url):
    parsed = urlparse(url)
    result = parse_qs(parsed.query)
    if 'v' in result:
        return result['v'][0]
    else:
        return None


def youtube_search(vid_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=build_credentials())

    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.videos().list(
        id=vid_id,
        part='id,snippet',
    ).execute()

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get('items', []):
        if search_result['id'] == vid_id:
            return search_result['snippet']
    return None
