import json
import os
import re
import sys
import time
import urllib.request

from urllib.request import Request, urlopen

#Constants
SLEEP_TIME_MS = 500

#./ericdapanda/profile.txt:      <div ng-controller="MemberViewCtrl" ng-init="init('EricDaPanda', 'https://images.chesscomfiles.com/uploads/v1/user/17018146.1d030add.30x30o.81fc34afaf14.jpeg', true, 'comment', true)">
#./ericdapanda/profile.txt:  ng-init="init('web_user_callback_load_notes', {&quot;userId&quot;:17018146,&quot;itemsPerPage&quot;:8}, true, 'user_notes', false)" ng-cloak>
#./ericdapanda/profile.txt:<section id="sidebar-user-trophy-showcase" ng-controller="UserTrophyShowcaseCtrl" ng-init="init('EricDaPanda')" ng-hide="model.trophyShowcaseLength === 0">
#./ericdapanda/profile.txt:            ng-init="newMessage.receiver=userRecipient"

#./onlydrum/profile.txt:      <div ng-controller="MemberViewCtrl" ng-init="init('OnlyDrum', 'https://betacssjs.chesscomfiles.com/bundles/web/images/noavatar_l.1c5172d5.gif', true, 'comment', true)">
#./onlydrum/profile.txt:  ng-init="init('web_user_callback_load_notes', {&quot;userId&quot;:47275602,&quot;itemsPerPage&quot;:8}, true, 'user_notes', false)" ng-cloak>
#./onlydrum/profile.txt:<section id="sidebar-user-trophy-showcase" ng-controller="UserTrophyShowcaseCtrl" ng-init="init('OnlyDrum')" ng-hide="model.trophyShowcaseLength === 0">
#./onlydrum/profile.txt:            ng-init="newMessage.receiver=userRecipient"

# https://www.chess.com/callback/leaderboard/live/lightning?friendsOfId=51429148&page=1

# 2466453
# hikaru - 15448422
# cofytea - 27495250
#Website Variables
URL_BASE_MEMBER = 'https://www.chess.com/stats/live/bullet/'
#URL_BASE_MEMBER = 'https://www.chess.com/member'
# URL_BASE = 'https://www.chess.com/leaderboard/live/bullet?friendsOnly='
URL_BASE = 'https://www.chess.com/callback/leaderboard/live/lightning?friendsOfId='
URL_PAGE = '&page='

#Cache Variables
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chess_com")
PLAYER_DIR = os.path.join(CACHE_DIR, "https", "api.chess.com", "pub", "player")
PROFILE = 'profile.txt'
FRIENDS_BASE = 'friends_'

#Global variables
last_fetch = 0

IMAGE_LINE = 'MemberViewCtrl'
IGNORE_LINE = 'noavatar'
FIND_IMAGE_ID = '(user\/)([^/^.][0-9]+)'
IMAGE_ID_GROUP = 1

NOTES_LINE = 'web_user_callback_load_notes'
FIND_NOTES_ID = '([^:^,][0-9]+)'
NOTES_ID_GROUP = 2

def find_id(path):
    member_id = None
    notes_id = None

    if not os.path.isfile(path):
        print("Not a file: %s" % (path))
        return

    with open(path, 'r') as file:
        for line in file:
            if IMAGE_LINE in line:
                if IGNORE_LINE in line:
                    continue
                match = re.search(r'' + FIND_IMAGE_ID, line)
                if match != None:
                    member_id = match.group(2)

            if NOTES_LINE in line:
                match = re.search(r'' + FIND_NOTES_ID, line)
                if match != None:
                    notes_id = match.group(1)

    if member_id == None and notes_id == None:
        return None
    elif member_id == None:
        return str(notes_id)
    else:
        return str(member_id)

def fetch_profile(username, out_path, profile, url):
    global last_fetch

    profile_path = os.path.join(out_path, username, profile)
    # if not os.path.isfile(profile_path):
    #if os.path.isfile(profile_path):
    if True:
        #Sleep 0.5 second each call
        now = int(time.time() * 1000)
        sleep_time_sec = (SLEEP_TIME_MS - (now - last_fetch)) / 1000.0
        if (sleep_time_sec > 0):
            time.sleep(sleep_time_sec)

        print(url)
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            response = urlopen(req)
        except:
            print("User Error: %s" % (username))
            return
            
        last_fetch = int(time.time() * 1000)

        return response.read().decode('utf-8')

def write_profile(username, out_path, profile, data):
    if data == None or data == "":
        return

    profile_path = os.path.join(out_path, username, profile)
    if not os.path.isdir(os.path.join(out_path, username)):
        os.mkdir(os.path.join(out_path, username))
    
    data_json = json.loads(data)
    with open(profile_path, 'w') as file:
        #file.write(data)
        json.dump(data_json, file, indent = 4)

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
        id_key = find_id(os.path.join(out_path, username, PROFILE))
        if id_key == None:
            print("No key: %s" % (username))
        
        print('Username: %s ID_Key: %s' % (username, id_key))

        data = ''
        previous_data = 'start'
        count = 0
        while True:
            count += 1
            url = URL_BASE_MEMBER + username
            fetch_profile(username, out_path, PROFILE, url)

            url = URL_BASE + id_key + URL_PAGE + str(count)
            data = fetch_profile(username, out_path, FRIENDS_BASE + str(count) + '.txt', url)
            
            if previous_data == data:
                break
            write_profile(username, out_path, FRIENDS_BASE + str(count) + '.txt', data)
            previous_data = data

        if counter % 100 == 0:
            print(counter)
            sys.stdout.flush()
        counter += 1
        if counter > 4:
            break
        #break

if (__name__ == '__main__'):
    main()
