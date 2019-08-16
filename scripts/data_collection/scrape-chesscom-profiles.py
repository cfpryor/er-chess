import json
import os
import sys
import time
import urllib.request

from urllib.request import Request, urlopen

#Constants
SLEEP_TIME_MS = 500

#Website Variables
URL_BASE = 'https://www.chess.com/member/'

#Cache Variables
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chess_com")
PLAYER_DIR = os.path.join(CACHE_DIR, "https", "api.chess.com", "pub", "player")
PROFILE = 'profile.txt'

#Global variables
last_fetch = 0

def fetch_profile(username, out_path):
    global last_fetch

    profile_path = os.path.join(out_path, username, PROFILE)
    if not os.path.isfile(profile_path):
        #Sleep 0.5 second each call
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
            return
            
        last_fetch = int(time.time() * 1000)

        return response.read().decode('utf-8')

def write_profile(username, out_path, data):
    if data == None or data == "":
        return

    profile_path = os.path.join(out_path, username, PROFILE)
    if not os.path.isdir(os.path.join(out_path, username)):
        os.mkdir(os.path.join(out_path, username))
    
    with open(profile_path, 'w') as file:
        file.write(data)

def load_users(user_path):
    with open(user_path, 'r') as file:
        return json.load(file)

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 2 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <in_file> <out_directory>" % (executable), file = sys.stderr)
        sys.exit(1)

    in_path = args.pop(0)
    out_path = args.pop(0)
    return in_path, out_path

def main():
    user_path, out_path = _load_args(sys.argv)
    user_list = load_users(user_path)
    if not os.path.isdir(out_path):
        os.mkdir(out_path)
    
    counter = 0
    for username in user_list: 
        data = fetch_profile(username, out_path)
        write_profile(username, out_path, data)
        if counter % 100 == 0:
            print(counter)
            sys.stdout.flush()
        counter += 1

if (__name__ == '__main__'):
    main()
