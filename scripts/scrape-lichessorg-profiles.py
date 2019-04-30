import json
import os
import sys
import time
import shutil
import urllib.request

from urllib.request import Request, urlopen

# Constants
SLEEP_TIME_MS = 500

# Website Variables
URL_BASE = 'https://www.lichess.org/@/'

# Cache Variables
SEED_PLAYERS = os.path.join(os.path.dirname(__file__), "..", "data", "lichess_org","profiles")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "lichess_org")
PLAYER_DIR = os.path.join(CACHE_DIR, "https", "lichess.org")
PROFILE = 'profile.txt'

# Global variables
last_fetch = 0


def fetch_profile(username):
    global last_fetch

    profile_path = os.path.join(PLAYER_DIR, username)
    if not os.path.exists(profile_path):
        os.mkdir(profile_path)
        # Sleep 0.5 second each call
        now = int(time.time() * 1000)
        sleep_time_sec = (SLEEP_TIME_MS - (now - last_fetch)) / 1000.0
        if (sleep_time_sec > 0):
            time.sleep(sleep_time_sec)

        url = os.path.join(URL_BASE, username)
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            response = urlopen(req)
        except:
            print("User Error: %s" % (username))
            shutil.rmtree(PLAYER_DIR + '/' + username)
            return

        data = response.read().decode('utf-8')
        profile_file_path = os.path.join(PLAYER_DIR, username,PROFILE)
        with open(profile_file_path, 'w') as file:
            file.write(data)

        last_fetch = int(time.time() * 1000)


def main():
    with open(SEED_PLAYERS) as f:
        lines = f.read().splitlines()
    unexplored_users = set()  # read from a file
    unexplored_users |= set(lines)
    print(len(unexplored_users))
    sys.stdout.flush()

    counter = 0
    for username in unexplored_users:
        fetch_profile(username)
        if counter % 100 == 0:
            print(counter)
            sys.stdout.flush()
        counter += 1


if (__name__ == '__main__'):
    main()
