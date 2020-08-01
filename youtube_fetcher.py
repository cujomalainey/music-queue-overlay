#!/usr/bin/python

# This sample executes a search request for the specified search term.
# Sample usage:
#   python search.py --q=surfing --max-results=10
# NOTE: To use the sample, you must provide a developer key obtained
#       in the Google APIs Console. Search for "REPLACE_ME" in this code
#       to find the correct place to provide that key..

import argparse
import os

from urllib.parse import parse_qs
from urllib.parse import urlparse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
YOUTUBE_DEVELOPER_KEY = os.environ['YOUTUBE_DEVELOPER_KEY']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

YOUTUBE_DOMAINS = ['youtu.be', 'www.youtube.com', 'youtube.com']

class videoInfo():
  def __init__(self, title, thumbnail=None):
    self.title = title
    self.thumbnail = thumbnail

def get_video_data(url, db, app):
  video_id = None

  # if not youtube then return domain
  domain = get_domain(url)
  if domain not in YOUTUBE_DOMAINS:
    return videoInfo(domain)

  # parse out id
  if domain == 'youtu.be':
    # parse out last segment
    video_id = get_last_segment(url)
  else:
    # parse out get var
    video_id = get_var_from_url(url)
  if not video_id:
    return videoInfo(domain)

  # check DB cache
  result = get_video_from_db_cache(video_id, db)
  if result:
    return result

  try:
    result = youtube_search(video_id)
  except HttpError as e:
    app.logger.error('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))

  if not result:
    return videoInfo(domain)
  cache_result(video_id, result)
  return result


def get_video_from_db_cache(video_id, db):
  return None


def cache_result(video_id, result):
  pass


def get_domain(url):
  return urlparse(url).netloc


def get_last_segment(url):
  p = urlparse(url)
  return p.path.rsplit("/", 1)[-1]


def get_var_from_url(url):
  parsed = urlparse(url)
  result = parse_qs(parsed.query)
  if 'v' in result:
    return result['v']
  else:
    return None


def youtube_search(id):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=YOUTUBE_DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=options.q,
    part='id,snippet',
    type="video",
    maxResults=20,
  ).execute()

  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get('items', []):
    if search_result['id']['videoId'] == options.q:
      return videoId(search_result['snippet']['title'], search_result['snippet']['thumbnails']['default']['url'])
