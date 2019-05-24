import json
import os
import re
import sys
import time
import urllib.request

from urllib.request import Request, urlopen

#Constants
URL_DICT = [('https://lichess.org/@/', 'profile.txt')]
TXT_INFO = [('Full_Name', '<strong class="name">([\S\s]+)<\/strong><p class=\"bio'),
            ('Joined', 'Member since ([\S]+)</p><p class="thin"'),
            ('Country', '<span class="country">[\S\s]+/> ([\S]+)</span><p '),
            ('Location', 'location">([\S\s]+)<\/span><span'),
            ('Followers', 'followers"><strong>([\S]+)<\/strong>'),
            ('Bullet_Current', 'BULLET[\S]+<strong>([0-9]+)<'),
            ('Blitz_Current', 'BLITZ[\S]+<strong>([0-9]+)<'),
            ('Rapid_Current', 'RAPID[\S]+<strong>([0-9]+)<'),
            ('Tactics_Current', 'TRAINING[\S]+<strong>([0-9]+)<'),
            ('FIDE', 'FIDE rating: <strong>([0-9]+)<\/strong>'),
            ('USCF', 'USCF rating: <strong>([0-9]+)<\/strong>')]

TXT_SUFFIX = 'txt'

SLEEP_TIME_MS = 500
last_fetch = 0

def parse_html_file(data_path):
    info_dict = {}
    for header, regex in TXT_INFO:
        info_dict[header] = None

    with open(data_path, 'r') as file:
        for line in file:
            for header, regex in TXT_INFO:
                match = re.search(r'' + regex, line)
                if match != None:
                    info_dict[header] = match.group(1)

    return info_dict

def write(data, path):
    if data == None:
        return

    with open(path, 'w') as file:
        try:
            data_json = json.loads(data)
            json.dump(data_json, file, indent = 4)
        except:
            file.write(data)

def fetch_profile(url):
    global last_fetch

    now = int(time.time() * 1000)
    sleep_time_sec = (SLEEP_TIME_MS - (now - last_fetch)) / 1000.0
    if (sleep_time_sec > 0):
        time.sleep(sleep_time_sec)

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    try:
        response = urlopen(req)
    except:
        print("Error: %s" % (url))
        last_fetch = int(time.time() * 1000)
        return

    last_fetch = int(time.time() * 1000)
    return response.read().decode('utf-8')

def load_users(user_path):
    with open(user_path, 'r') as file:
        return json.load(file)

def load_profiles(out_path, username):
    if not os.path.isdir(out_path):
        os.mkdir(out_path)

    for url_base, out_filename in URL_DICT:
        out_user_dir = os.path.join(out_path, username)
        if not os.path.isdir(out_user_dir):
            os.mkdir(out_user_dir)
        
        out_user_path = os.path.join(out_user_dir, out_filename)
        if not os.path.isfile(out_user_path):
            url = os.path.join(url_base, username)
            data = fetch_profile(url)
            write(data, out_user_path)

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
    user_data = {}

    for username in user_list:
        #load_profiles(out_path, username)
        #print(username, count)
        user_data[username] = {'Website': 'lichess'}
        for url_base, out_filename in URL_DICT:
            profile_path = os.path.join(out_path, username, out_filename)
            if out_filename.split(".")[-1] == TXT_SUFFIX:
                if os.path.isfile(profile_path):
                    user_data[username].update(parse_html_file(profile_path))
    with open('../data/finalized_profiles/lichess_profile_information.json', 'w') as file:
        json.dump(user_data, file, indent = 4)
        return
if (__name__ == '__main__'):
    main()
