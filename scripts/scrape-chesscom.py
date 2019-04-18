# https://www.chess.com/news/view/published-data-api#pubapi-endpoint-player

import json
import http
import os
import requests
import shutil
import sys
import time
import urllib.request

from socket import timeout
from urllib.error import HTTPError
from urllib.error import URLError

SEED_USERS = [
    'Cofytea',
    'hikaru',
    'penguingm1',
    'mikeyslice',
    'dawidczerw',
    'bikfoot',
    'sirplinko',
    'ajedrez',
    'wsk',
    'samcopeland',
]

SLEEP_TIME_MS = 500
START_YEAR = 2017
START_MONTH = 4
DEFAULT_TIMEOUT = 60

URL_BASE = 'https://api.chess.com/pub/player/'

# Pathing information
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chess_com")
PLAYER_DIR = os.path.join(CACHE_DIR, "https", "api.chess.com", "pub", "player")
CACHE_DATA_FILENAME = 'response.data'
CACHE_USER_OPPONENTS = '__opponents.json'

# HACK(eriq): Using a global for timing.
last_fetch = 0
start_log = 0

def log(message):
    global start_log
    curr_time = int(time.time() * 1000)
    if start_log != 0:
        program_time = curr_time - start_log
    else:
        program_time = 0

    print("%7d: %s" % (program_time, message))
    sys.stdout.flush()
    start_log = curr_time

def make_cache_path(url, filename = CACHE_DATA_FILENAME):
    # HACK(eriq): If we wanted to be robust, we would use a url lib.
    url = url.replace('://', '/')

    cache_dir = os.path.join(CACHE_DIR, *url.split('/'))

    os.makedirs(cache_dir, exist_ok = True)

    return os.path.join(cache_dir, filename)

def clean_name(username):
    return username.lower()

def fetch_json(url, default_timeout = DEFAULT_TIMEOUT):
    global last_fetch

    # TODO(connor): Handle error codes: https://www.chess.com/news/view/published-data-api#pubapi-endpoint-player

    cache_path = make_cache_path(url)
    if (os.path.isfile(cache_path)):
        with open(cache_path, 'r') as file:
            return json.load(file)

    log("Fetching: " + url)

    now = int(time.time() * 1000)
    sleep_time_sec = (SLEEP_TIME_MS - (now - last_fetch)) / 1000.0
    if (sleep_time_sec > 0):
        time.sleep(sleep_time_sec)

    #response = urllib.request.urlopen(url)
    #last_fetch = int(time.time() * 1000)
    #data = json.loads(response.read().decode('utf-8'))
    
    try:
        response = urllib.request.urlopen(url, timeout=default_timeout).read().decode('utf-8')
    except (HTTPError, URLError) as error:
        log('Data not retrieved because %s\nURL: %s' % (error, url))
        return None
    except timeout:
        log('Socket timed out - URL %s' % (url))
        return None
    except http.client.IncompleteRead as icread:
        log('Incomplete Read %s - URL %s' % (icread, url))
        return None
    except Exception as error:
        log('Other error - %s' % (error))
        return None

    last_fetch = int(time.time() * 1000)
    data = json.loads(response)

    with open(cache_path, 'w') as file:
        json.dump(data, file, indent = 4)

    log("Finished Fetching: " + url)
    return data

def collect_users(games, context_user = None):
    users = set()

    for game in games['games']:
        for side in ['white', 'black']:
            name = clean_name(game[side]['username'])
            if (name != context_user):
                users.add(name)

    return users

def fetch_user(username):
    username = clean_name(username)
    opponents_path = make_cache_path(URL_BASE + username, filename = CACHE_USER_OPPONENTS)

    if os.path.isfile(opponents_path):
        with open(opponents_path, 'r') as file:
            return set(json.load(file))

    # Fetch archive
    url = URL_BASE + username + '/games/archives'
    archive = fetch_json(url)

    # If there is an error loading the data
    if archive == None:
        return None

    found_users = {username}

    for link in archive['archives']:
        parts = link.rstrip('/').split('/')
        year, month = int(parts[-2]), int(parts[-1])

        if (year < START_YEAR or (year == START_YEAR and month < START_MONTH)):
            continue

        games = fetch_json(link)
        # If there is an error loading the data
        if games == None:
            return None
        
        found_users |= collect_users(games, username)
        log("Currently found %d users for %s." % (len(found_users), username))

    with open(opponents_path, 'w') as file:
        json.dump(list(found_users), file, indent=4)

    return found_users

def main():
    unexplored_users = set()
    explored_users = set()

    unexplored_users |= set(SEED_USERS)

    while (len(unexplored_users) > 0):
        user = unexplored_users.pop()
        user = clean_name(user)

        explored_users.add(user)
        
        log('Current User: %s' % (user))
        log('Explored %d / %d users.' % (len(explored_users), len(unexplored_users) + len(explored_users)))

        new_users = fetch_user(user)

        # If there are any issues with getting the data remove the user from explored
        if new_users == None:
            explored_users.remove(user)
            shutil.rmtree(PLAYER_DIR + user)
            log("Deleting User: %s" % (user))
            continue

        for new_user in new_users:
            new_user = clean_name(new_user)

            if (new_user not in explored_users):
                unexplored_users.add(new_user)

if (__name__ == '__main__'):
    main()
