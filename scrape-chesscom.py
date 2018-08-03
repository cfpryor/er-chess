# https://www.chess.com/news/view/published-data-api#pubapi-endpoint-player

import json
import os
import time
import urllib.request

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

URL_BASE = 'https://api.chess.com/pub/player/'

CACHE_DIR = 'cache'
CACHE_DATA_FILENAME = 'response.data'

# HACK(eriq): Using a global for timing.
last_fetch = 0

def make_cache_path(url):
    # HACK(eriq): If we wanted to be robust, we would use a url lib.
    url = url.replace('://', '/')

    cache_dir = os.path.join(CACHE_DIR, *url.split('/'))

    os.makedirs(cache_dir, exist_ok = True)

    return os.path.join(cache_dir, CACHE_DATA_FILENAME)

def clean_name(username):
    return username.lower()

def fetch_json(url):
    global last_fetch

    # TODO(connor): Handle error codes: https://www.chess.com/news/view/published-data-api#pubapi-endpoint-player

    cache_path = make_cache_path(url)
    if (os.path.isfile(cache_path)):
        with open(cache_path, 'r') as file:
            return json.load(file)

    print("Fetching: " + url)

    now = int(time.time() * 1000)
    sleep_time_sec = (SLEEP_TIME_MS - (now - last_fetch)) / 1000.0
    if (sleep_time_sec > 0):
        time.sleep(sleep_time_sec)

    response = urllib.request.urlopen(url)
    last_fetch = int(time.time() * 1000)
    data = json.loads(response.read().decode('utf-8'))

    with open(cache_path, 'w') as file:
        json.dump(data, file, indent = 4)

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

    # Fetch archive
    url = URL_BASE + username + '/games/archives'
    archive = fetch_json(url)

    found_users = {username}

    for link in archive['archives']:
        parts = link.rstrip('/').split('/')
        year, month = int(parts[-2]), int(parts[-1])

        if (year < START_YEAR or (year == START_YEAR and month < START_MONTH)):
            continue

        games = fetch_json(link)
        found_users |= collect_users(games, username)

    return found_users

def main():
    unexplored_users = set()
    explored_users = set()

    unexplored_users |= set(SEED_USERS)

    while (len(unexplored_users) > 0):
        user = unexplored_users.pop()
        user = clean_name(user)

        explored_users.add(user)

        new_users = fetch_user(user)
        for new_user in new_users:
            new_user = clean_name(new_user)

            if (new_user not in explored_users):
                unexplored_users.add(new_user)

if (__name__ == '__main__'):
    main()
