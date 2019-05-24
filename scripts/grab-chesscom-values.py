import json
import os
import re
import sys
import time
import urllib.request

from urllib.request import Request, urlopen

#Constants
URL_DICT = [('https://www.chess.com/member', 'profile.txt'), ('https://www.chess.com/callback/member/stats', 'stats.json')]

TXT_INFO = [('Full_Name', 'user-full-name', 'name">([\S\s]+)<'),
            ('Joined', 'item-data', 'data">([\S\s]+)<[\S]+'),
            ('Views', 'item-data', 'data">([\S\s]+)<[\S]+'),
            ('Followers', 'item-data', 'data">([\S\s]+)<[\S]+' ),
            ('Points', 'item-data', 'data">([\S\s]+)<[\S]+' ),
            ('Membership', 'membership-level-large', 'tip="([A-Za-z0-9\s]+)[\S]+')]

JSON_INFO = [('Bullet_Current', 'stats', ('bullet', 'rating')),
             ('Bullet_Best', 'stats', ('bullet', 'highest_rating')),
             ('Blitz_Current', 'stats', ('lightning', 'rating')),
             ('Blitz_Best', 'stats', ('lightning', 'highest_rating')),
             ('Rapid_Current', 'stats', ('rapid', 'rating')),
             ('Rapid_Best', 'stats', ('rapid', 'highest_rating')),
             ('Lessons_Current', 'stats', ('lessons', 'rating')),
             ('Lessons_Best', 'stats', ('lessons', 'highest_rating')),
             ('Tactics_Current', 'stats', ('tactics', 'rating')),
             ('Tactics_Best', 'stats', ('tactics', 'highest_rating')),
             ('FIDE', 'officialRating', ('FIDE', 'rating')),
             ('USCF', 'officialRating', ('USCF', 'rating')),
             ('National', 'officialRating',('National', 'rating'))]

TXT_SUFFIX = 'txt'
JSON_SUFFIX = 'json'

SLEEP_TIME_MS = 500
last_fetch = 0

def parse_html_file(data_path):
    info_dict = {}
    grab_next_lines = ''
    location = ''
    for header, key, identifier in TXT_INFO:
        info_dict[header] = None

    with open(data_path, 'r') as file:
        previous_line = ''
        for line in file:
            if grab_next_lines != '':
                if grab_next_lines in line:
                    grab_next_lines = ''
                else:
                    location = location + line
                continue
            for header, key, regex in TXT_INFO:
                if key in line:
                    if key == 'item-data':
                        if header in previous_line:
                            match = re.search(r'' + regex, line)
                            if match != None:
                                info_dict[header] = match.group(1)
                    elif key == 'user-full-name':
                        match = re.search(r'' + regex, line)
                        if match != None:
                            info_dict[header] = match.group(1)
                        grab_next_lines = '</div>'
                    else:
                        match = re.search(r'' + regex, line)
                        if match != None:
                            info_dict[header] = match.group(1)
            previous_line = line

        if location != '':
            parts = location.strip().split(',')
            if len(parts) == 2:
                info_dict['Location'] = parts[0].strip()
                info_dict['Country'] = parts[1].strip()
            else:
                info_dict['Country'] = parts[0].strip()

    return info_dict

def parse_json_file(data_path, info = JSON_INFO):
    info_dict = {}
    with open(data_path, 'r') as file:
        data = json.load(file)

    for header, key, path in info:
        info_dict[header] = None
        if key in data:
            if key == 'stats':
                for stats in data[key]:
                    if stats['key'] == path[0]:
                        if path[1] in stats['stats']:
                            info_dict[header] = stats['stats'][path[1]]
            
            if key == 'officialRating':
                if data[key]['ratingType'] == path[0]:
                    info_dict[header] = data[key][path[1]]

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
        #print(username, count)
        #load_profiles(out_path, username)
        
        if username in user_data:
            continue
        username_lower = username.lower()
        user_data[username_lower] = {'Website':'chesscom'}
        for url_base, out_filename in URL_DICT:
            profile_path = os.path.join(out_path, username_lower, out_filename)
            if out_filename.split(".")[-1] == TXT_SUFFIX:
                if os.path.isfile(profile_path):
                    user_data[username_lower].update(parse_html_file(profile_path))
            elif out_filename.split(".")[-1] == JSON_SUFFIX:
                if os.path.isfile(profile_path):
                    user_data[username_lower].update(parse_json_file(profile_path))
    with open('../data/finalized_profiles/chesscom_profile_information.json', 'w') as file:
        json.dump(user_data, file, indent = 4)
        #return
if (__name__ == '__main__'):
    main()
