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
SLEEP_TIME_MS = 300
DEFAULT_TIMEOUT = 60
MAX_EXPIRE_ATTEMPTS = 10
MAX_ATTEMPTS = 3

FOLLOWINGS_PREFIX = 'following?page='
FOLLOWERS_PREFIX = 'followers?page='
TAR_SUFFIX = '.tar'

# URL Variables
URL_BASE = 'https://lichess.org/@/'

API_BASE = 'https://lichess.org/api/'
USER_API_BASE = os.path.join(API_BASE, 'user')

# Outupt Filenames
OUTPUT_API_PROFILE = 'api_profile.json.gz'
OUTPUT_OPPONENTS = 'opponents.json.gz'
OUTPUT_PROFILE = 'profile.html.gz'
OUTPUT_STATS = 'stats.json'
OUTPUT_FOLLOWING = 'following_'
OUTPUT_FOLLOWERS = 'followers_'

TERMINAL_FOLLOWING = "<tbody class=\"infinitescroll\"></tbody></table></main></div><a id=\"reconnecting\" class=\"link text\" data-icon=\"B\">Reconnecting"
NONE_FOLLOWING = "<table class=\"slist\"><tbody><tr><td colspan=\"2\">None found.<br /></td></tr></tbody></table></main></div><a id=\"reconnecting\" class=\"link text\" data-icon=\"B\">Reconnecting"
TERMINAL_FOLLOWERS = "<tbody class=\"infinitescroll\"></tbody></table></main></div><a id=\"reconnecting\" class=\"link text\" data-icon=\"B\">Reconnecting"
NONE_FOLLOWERS= "<table class=\"slist\"><tbody><tr><td colspan=\"2\">None found.<br /></td></tr></tbody></table></main></div><a id=\"reconnecting\" class=\"link text\" data-icon=\"B\">Reconnecting"

# Global variables
last_fetch = 0
start_log = int(time.time() * 1000)

# Logging output
def log(message, level = 'INFO'):
    global start_log

    program_time = int(time.time() * 1000) - start_log

    # Prints log containing time since start of program, message level, and the message
    print("%7d %8s: %s" % (program_time, level, message))
    sys.stdout.flush()

# Name to lowercase
def clean_name(username):
    return username.lower()

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
    api_profile_response = fetch_url(os.path.join(USER_API_BASE, username))
    if api_profile_response != None:
        gzip_json(api_profile_response, os.path.join(output_path, OUTPUT_API_PROFILE))

    return

    friends = {}
    stats = {}

    # Grab profile html
    attempts = 0
    stats['has_profile'] = False
    while(attempts < MAX_ATTEMPTS):
        profile_response = fetch_url(os.path.join(URL_BASE, username))
        if profile_response != None:
            gzip_data(profile_response, os.path.join(output_path, OUTPUT_PROFILE))
            stats['has_profile'] = True
            break
        attempts += 1

    # Gather fowllowing list
    stats['has_following'] = True
    attempts = 0

    # Pages are timed out for most users, so a profile request is needed
    max_expire_attempts = MAX_EXPIRE_ATTEMPTS
    page_number = 1

    # Grab all the following
    while True:
        current_following_response = fetch_url(os.path.join(URL_BASE, username, FOLLOWINGS_PREFIX + str(page_number)))
        # Need to put this in to prevent infinite looping failures
        if attempts == MAX_ATTEMPTS:
            max_expire_attempts -= 1
            page_number += 1
            break

        # If the request was bad, try again up to the maximum number of times
        elif current_following_response == None:
            attempts += 1
            continue
        
        if TERMINAL_FOLLOWING in str(current_following_response.encode('utf-8')) or NONE_FOLLOWING in str(current_following_response.encode('utf-8')):
            break

        gzip_data(current_following_response, os.path.join(output_path, OUTPUT_FOLLOWING + str(page_number) + ".html.gz"))
        page_number += 1
        attempts = 0
    
    # Gather followers list
    stats['has_followers'] = True
    attempts = 0

    # Pages are timed out for most users, so a profile request is needed
    max_expire_attempts = MAX_EXPIRE_ATTEMPTS
    page_number = 1

    # Grab all the followers
    while True:
        current_followers_response = fetch_url(os.path.join(URL_BASE, username, FOLLOWERS_PREFIX + str(page_number)))
        # Need to put this in to prevent infinite looping failures
        if attempts == MAX_ATTEMPTS:
            max_expire_attempts -= 1
            page_number += 1
            break

        # If the request was bad, try again up to the maximum number of times
        elif current_followers_response == None:
            attempts += 1
            continue
        
        if TERMINAL_FOLLOWERS in str(current_followers_response.encode('utf-8')) or NONE_FOLLOWERS in str(current_followers_response.encode('utf-8')):
            break

        gzip_data(current_followers_response, os.path.join(output_path, OUTPUT_FOLLOWERS + str(page_number) + ".html.gz"))
        page_number += 1
        attempts = 0

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
