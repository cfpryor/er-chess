import gzip
import json
import os
import socket
import sys
import tarfile
import time
import urllib.request

from urllib.request import HTTPError, URLError

# Request Constants
RATE_LIMITING_CODE = 429
RATE_LIMIT_SLEEP = 61

# Constants
SLEEP_TIME_MS = 100
DEFAULT_TIMEOUT = 60
START_YEAR = 2017
START_MONTH = 4
MAX_EXPIRE_ATTEMPTS = 10
MAX_ATTEMPTS = 3

GAMEMODE_FRIEND_LISTS = ['bullet', 'blitz', 'rapid']
FRIENDS_PREFIX = '?friendsOfId='
FRIENDS_SUFFIX = '&page='
PLAYER_ID = 'player_id'
TAR_SUFFIX = '.tar'

# Website Variables
WEBSITE_BASE = 'https://www.chess.com'
MEMBER_BASE = os.path.join(WEBSITE_BASE, 'member')
STATS_BASE = os.path.join(WEBSITE_BASE, 'stats', 'live')
CALLBACK_BASE = os.path.join(WEBSITE_BASE, 'callback')
CALLBACK_STATS_BASE = os.path.join(CALLBACK_BASE, 'member', 'stats')
CALLBACK_LEADERBOARD_BASE = os.path.join(CALLBACK_BASE, 'leaderboard', 'live')

# API Variables
API_BASE = 'https://api.chess.com/pub/player/'
GAMES_BASE = 'games'
ARCHIVE_BASE = os.path.join(GAMES_BASE, 'archives')

# Outupt Filenames
OUTPUT_API_PROFILE = 'api_profile.json.gz'
OUTPUT_ARCHIVE = 'archive.json.gz'
OUTPUT_CALLBACK_STATS = 'callback_stats.json.gz'
OUTPUT_GAMES = '.json.gz'
OUTPUT_OPPONENTS = 'opponents.json.gz'
OUTPUT_PROFILE = 'profile.html.gz'
OUTPUT_STATS = 'stats.json'

# Global variables
last_fetch = 0
start_log = int(time.time() * 1000)

# Name to lowercase
def clean_name(username):
    return username.lower()

# Used to collect users in a json file
def collect_users(game_response, context_user = None):
    users = set()

    # Look through all games and find the users opponent
    for game in game_response['games']:
        for side in ['white', 'black']:
            name = clean_name(game[side]['username'])
            if (name != context_user):
                users.add(name)

    return users

# Logging output
def log(message, level = 'INFO'):
    global start_log

    program_time = int(time.time() * 1000) - start_log

    # Prints log containing time since start of program, message level, and the message
    print("%7d %8s: %s" % (program_time, level, message))
    sys.stdout.flush()

# Fetch url
def fetch_url(url, default_timeout = DEFAULT_TIMEOUT):
    global last_fetch

    log("Fetching: " + url)
    # Sleep to avoid rate limiting
    sleep_time_sec = (SLEEP_TIME_MS - (int(time.time() * 1000) - last_fetch)) / 1000.0
    if (sleep_time_sec > 0):
        time.sleep(sleep_time_sec)

    # Try and make the url request, catching any errors
    # There were some sneaky errors here so these excepts needed to be made
    try:
        # Create the request as a user agent
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(request, timeout=default_timeout).read().decode('utf-8')
        last_fetch = int(time.time() * 1000)
    except (HTTPError, URLError) as error:
        if int(error.getcode()) == RATE_LIMITING_CODE:
            time.sleep(RATE_LIMIT_SLEEP)
        log('Error: %s -- URL: %s' % (error, url), level = 'ERROR')
        last_fetch = int(time.time() * 1000)
        return None
    except Exception as error:
        log('Error: %s -- URL: %s' % (error, url), level = 'ERROR')
        last_fetch = int(time.time() * 1000)
        return None

    return response

# Gzip and write
def gzip_data(data, output_path):
    with gzip.open(output_path, 'wb') as output_file:
        output_file.write(data.encode())

# Gzip and write json
def gzip_json(data, output_path):
    with gzip.GzipFile(output_path, 'w') as output_file:
        output_file.write(json.dumps(data).encode('utf-8'))

# Fetch all relavent information on a user
def fetch_data(username, output_path):
    api_profile_response = fetch_url(os.path.join(API_BASE, username))
    if api_profile_response != None:
        gzip_json(api_profile_response, os.path.join(output_path, OUTPUT_API_PROFILE))

    profile_response = fetch_url(os.path.join(MEMBER_BASE, username))
    if profile_response != None:
        gzip_data(profile_response, os.path.join(output_path, OUTPUT_PROFILE))

    return

    opponents = set()
    friends = {}
    stats = {}

    # Grab api profile json
    attempts = 0
    stats['has_api_profile'] = False
    while(attempts < MAX_ATTEMPTS):
        api_profile_response = fetch_url(os.path.join(API_BASE, username))
        if api_profile_response != None:
            api_profile_response = json.loads(api_profile_response)
            gzip_json(api_profile_response, os.path.join(output_path, OUTPUT_API_PROFILE))
            stats['has_api_profile'] = True
            break
        attempts += 1

    # Grab profile html
    attempts = 0
    stats['has_profile'] = False
    while(attempts < MAX_ATTEMPTS):
        profile_response = fetch_url(os.path.join(MEMBER_BASE, username))
        if profile_response != None:
            gzip_data(profile_response, os.path.join(output_path, OUTPUT_PROFILE))
            stats['has_profile'] = True
            break
        attempts += 1

    # Grab callback stats json
    attempts = 0
    stats['has_callback_stats'] = False
    while(attempts < MAX_ATTEMPTS):
        callback_stats_response = fetch_url(os.path.join(CALLBACK_STATS_BASE, username))
        if callback_stats_response != None:
            callback_stats_response = json.loads(callback_stats_response)
            gzip_json(callback_stats_response, os.path.join(output_path, OUTPUT_CALLBACK_STATS))
            stats['has_callback_stats'] = True
            break
        attempts += 1

    # Grab archive json
    attempts = 0
    stats['has_game_archive'] = False
    while(attempts < MAX_ATTEMPTS):
        archive_response = fetch_url(os.path.join(API_BASE, username, ARCHIVE_BASE))
        if archive_response != None:
            archive_response = json.loads(archive_response)
            gzip_json(archive_response['archives'], os.path.join(output_path, OUTPUT_ARCHIVE))
            stats['has_game_archive'] = True
            break
        attempts += 1

    # Grab game json
    stats['has_games'] = False
    if archive_response != None:
        if 'archives' in archive_response:
            stats['has_games'] = True
            for link in archive_response['archives']:
                parts = link.rstrip('/').split('/')
                year, month = int(parts[-2]), int(parts[-1])

                # Skip the request if the games happen before the starting date
                if (year < START_YEAR or (year == START_YEAR and month < START_MONTH)):
                    continue

                attempts = 0
                while(attempts < MAX_ATTEMPTS):
                    game_response = fetch_url(link)
                    if game_response != None:
                        game_response = json.loads(game_response)
                        opponents |= collect_users(game_response, username)
                        gzip_json(game_response, os.path.join(output_path, str(year) + "_" + str(month).zfill(2) + OUTPUT_GAMES))
                        break
                    attempts += 1

    # Write opponent list
    stats['has_opponent_list'] = True
    gzip_json(list(opponents), os.path.join(output_path, OUTPUT_OPPONENTS))

    # Gather friend list
    stats['has_friends'] = False
    if api_profile_response != None:
        if PLAYER_ID in api_profile_response:
            stats['has_friends'] = True
            profile_id = api_profile_response[PLAYER_ID]

            for gamemode in GAMEMODE_FRIEND_LISTS:
                # Friend pages are timed out for most users, so a profile request is needed
                fetch_url(os.path.join(STATS_BASE, gamemode, username))
                max_expire_attempts = MAX_EXPIRE_ATTEMPTS
                friends[gamemode] = []
                page_number = 1
                attempts = 0

                # Grab all the friends
                while True:
                    req = gamemode + FRIENDS_PREFIX + str(profile_id) + FRIENDS_SUFFIX + str(page_number)
                    current_friend_req = fetch_url(os.path.join(CALLBACK_LEADERBOARD_BASE, req))

                    # Need to put this in to prevent infinite looping failures
                    if max_expire_attempts == 0:
                        break

                    if attempts == MAX_ATTEMPTS:
                        max_expire_attempts -= 1
                        page_number += 1
                        attempts = 0
                        continue
                    # If the request was bad, try again up to the maximum number of times
                    elif current_friend_req == None:
                        attempts += 1
                        continue

                    current_friend_req = json.loads(current_friend_req)

                    # Empty leaders key means no more pages
                    if len(current_friend_req['leaders']) == 0:
                        # Except if the friends page has expired
                        if current_friend_req['expired']:
                            fetch_url(os.path.join(STATS_BASE, gamemode, username))
                            max_expire_attempts -= 1
                            continue
                        break

                    friends[gamemode].extend(current_friend_req['leaders'])
                    page_number += 1
                    attempts = 0

    # Write the friend lists
    for gamemode in GAMEMODE_FRIEND_LISTS:
        if gamemode not in friends:
            friends[gamemode] = []
        gzip_json(friends[gamemode], os.path.join(output_path, 'friends_' + gamemode + OUTPUT_GAMES))
    
    # Completed gathering data
    stats['time_completed'] = time.time()
    stats['server'] = socket.gethostname()

    # Write the stats file
    with open(os.path.join(output_path, OUTPUT_STATS), 'w') as output_file:
        json.dump(stats, output_file)
    
    # Tar up all files except for stats file
    with tarfile.open(os.path.join(output_path, username + TAR_SUFFIX), 'w') as tar:
        for filename in os.listdir(output_path):
            if filename != OUTPUT_STATS and filename != username + TAR_SUFFIX:
                tar.add(os.path.join(output_path, filename), arcname = filename)
                os.remove(os.path.join(output_path, filename))

    return(opponents)

def load_users(data_path):
    with open(data_path, 'r') as data_file:
        return json.load(data_file)

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 2 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <data path> <output path>" % (executable), file = sys.stderr)
        sys.exit(1)

    data_path = args.pop(0)
    output_path = args.pop(0)

    return (data_path, output_path)

def main():
    data_path, output_path = _load_args(sys.argv)
    users = load_users(data_path)

    for user in users:
        if not os.path.isdir(os.path.join(output_path, user)):
            os.mkdir(os.path.join(output_path, user))

        fetch_data(user, os.path.join(output_path, user))

if (__name__ == '__main__'):
    main()
