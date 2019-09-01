import gzip
import json
import os
import re
import sys
import string
import tarfile
import time
from time import strptime, mktime

TXT_INFO = [('name', '<strong class="name">([\S\s]+)<\/strong><p class=\"bio'),
            ('joined', 'Member since ([\S]+)</p><p class="thin"'),
            ('country', '<span class="country">[\S\s]+/> ([\S]+)</span><p '),
            ('location', 'location">([\S\s]+)<\/span><span'),
            ('followers', 'followers"><strong>([\S]+)<\/strong>'),
            ('bullet', 'BULLET[\S]+<strong>([0-9]+)<'),
            ('lightning', 'BLITZ[\S]+<strong>([0-9]+)<'),
            ('rapid', 'RAPID[\S]+<strong>([0-9]+)<'),
            ('tactics', 'TRAINING[\S]+<strong>([0-9]+)<'),
            ('fide', 'FIDE rating: <strong>([0-9]+)<\/strong>'),
            ('uscf', 'USCF rating: <strong>([0-9]+)<\/strong>'),
            ('title', 'title" title="[\S]+">(\S\S)'),
            ('is_streamer', 'trophy award icon3d streamer" title="([\S]+ [\S]+)"'),
            ('last_online', 'Active <time class="timeago" datetime="([\S]+)"'),
            ('status', 'line patron" title="([\S]+ [\S]+)"')]

# Outupt Filenames
OUTPUT_API_PROFILE = 'api_profile.json.gz'
OUTPUT_ARCHIVE = 'archive.json.gz'
OUTPUT_CALLBACK_STATS = 'callback_stats.json.gz'
OUTPUT_GAMES = '.json.gz'
OUTPUT_OPPONENTS = 'opponents.json.gz'
OUTPUT_PROFILE = 'profile.html.gz'
OUTPUT_STATS = 'stats.json'

BULLET_FRIENDS = 'friends_bullet.json.gz'
BLITZ_FRIENDS = 'friends_blitz.json.gz'
RAPID_FRINEDS = 'friends_rapid.json.gz'

CHESSCOM = 'chesscom'
LICHESS = 'lichess'
LICHESS_GAMES = 'lichess_games'

FOLLOWER = 'followers_'
FOLLOWING = 'following_'

TIMES = ['bullet', 'lightning', 'rapid', 'tactics']
FEATURE_LIST = ['name', 'location', 'country', 'is_streamer', 'followers', 'last_online', 'status', 'joined', 'title', 'fide', 'ucsf']
MONTH_FILENAMES = ['2017_04.json.gz', '2017_05.json.gz', '2017_06.json.gz', '2017_07.json.gz', '2017_08.json.gz', '2017_09.json.gz', '2017_10.json.gz',
                    '2017_11.json.gz', '2017_12.json.gz', '2018_01.json.gz', '2018_02.json.gz', '2018_03.json.gz', '2018_04.json.gz', '2018_05.json.gz',
                    '2018_06.json.gz', '2018_07.json.gz', '2018_08.json.gz', '2018_09.json.gz', '2018_10.json.gz', '2018_11.json.gz', '2018_12.json.gz']

# Global variables
start_log = int(time.time() * 1000)

# Logging output
# TODO(Connor) Move log and fetch_url functions into util file
def log(message, level = 'INFO'):
    global start_log

    program_time = int(time.time() * 1000) - start_log

    # Prints log containing time since start of program, message level, and the message
    print("%7d %8s: %s" % (program_time, level, message))
    sys.stdout.flush()

def load_data(path):
    log("Loading: %s" % (path))
    if not os.path.isfile(path):
        log("File does not exist: %s" % (path), level = 'WARNING')
        sys.exit(1)

    with open(path, 'r') as file:
        return json.load(file)

def load_queries(data):
    chesscom_set = set()
    lichess_set = set()

    for pair in data:
        for user in pair:
            if user[1] == 'lichess':
                lichess_set.add(user[0])
            if user[1] == 'chesscom':
                chesscom_set.add(user[0])

    return chesscom_set, lichess_set

# Savetime formatting 2019.02.21T03:00:58
def convert_to_epoch(datetime_string):
    try:
        target_timestamp = strptime(datetime_string, '%Y.%m.%dT%H:%M:%S')
        return mktime(target_timestamp)
    except:
        log("Error with datetime string: %s" % (datetime_string))
        return None


def load_chesscom_data(path, user_list):
    user_dict = {}
    for user in user_list:
        if not os.path.exists(os.path.join(path, user)):
            log(("Directory does not Exist: %s") % (os.path.join(path, user)))
            continue

        user_dict[user + '_chesscom'] = {'website': CHESSCOM, 'username': user, 'active': []}
        with tarfile.open(os.path.join(path, user, user + '.tar'), 'r:') as tar_file:
            filename = OUTPUT_API_PROFILE
            if filename not in tar_file.getnames():
                log("File does not exist: %s" % (filename))
                api_json = {}
            else:
                #api_json = json.loads(gzip.decompress(tar_file.extractfile(filename).read()).decode("utf-8"))
                data = gzip.decompress(tar_file.extractfile(filename).read()).decode('unicode-escape').encode("ascii", errors="ignore").decode()
                api_json = json.loads(data)

            for feature in FEATURE_LIST:
                if feature in api_json:
                    user_dict[user + '_chesscom'][feature] = api_json[feature]
                else:
                    user_dict[user + '_chesscom'][feature] = None

            friend_set = set()
            for filename in [BULLET_FRIENDS, BLITZ_FRIENDS, RAPID_FRINEDS]:
                if filename not in tar_file.getnames():
                    log("File does not exist: %s" % (filename))
                else:
                    friend_json = json.loads(gzip.decompress(tar_file.extractfile(filename).read()).decode())
                    for friend in friend_json:
                        if 'user' in friend:
                            if 'username' in friend['user']:
                                friend_set.add(str(friend['user']['username']).lower())
            user_dict[user + '_chesscom']['friends'] = list(friend_set)

            filename = OUTPUT_OPPONENTS
            if filename not in tar_file.getnames():
                log("File does not exist: %s" % (filename))
                opponent_list = []
            else:
                opponent_list = json.loads(gzip.decompress(tar_file.extractfile(filename).read()).decode('unicode-escape').encode("ascii", errors="ignore").decode())
            user_dict[user + '_chesscom']['opponents'] = opponent_list

            filename = OUTPUT_CALLBACK_STATS
            for time in TIMES:
                user_dict[user + '_chesscom'][time] = None

            if filename not in tar_file.getnames():
                log("File does not exist: %s" % (filename))
            else:
                ratings_json = json.loads(gzip.decompress(tar_file.extractfile(filename).read()).decode())
                #ratings_json = json.loads(gzip.decompress(tar_file.extractfile(filename).read()).decode('unicode-escape').encode("ascii", errors="ignore").decode())
                if 'stats' in ratings_json:
                    for ratings in ratings_json['stats']:
                        if 'key' not in ratings:
                            continue
                        if ratings['key'] not in TIMES:
                            continue
                        if 'stats' not in ratings:
                            continue
                        if 'rating' not in ratings['stats']:
                            continue
                        user_dict[user + '_chesscom'][ratings['key']] = ratings['stats']['rating']

            user_dict[user + '_chesscom']['eco'] = {}
            for filename in MONTH_FILENAMES:
                if filename not in tar_file.getnames():
                    continue
                games_json = json.loads(gzip.decompress(tar_file.extractfile(filename).read()).decode())
                if 'games' not in games_json:
                    continue
                for game in games_json['games']:
                    if 'pgn' not in game:
                        continue
                    side = "black"
                    result = None
                    eco = None
                    start_date = None
                    start_time = None
                    end_date = None
                    end_time = None
                    for parts in str(game['pgn']).lower().split("\n"):
                        if parts.startswith('[white \"'):
                            if parts.split("\"")[1] == user:
                                side = 'white'
                        if parts.startswith('[result \"'):
                            result = parts.split("\"")[1]
                        if parts.startswith('[eco \"'):
                            eco = parts.split("\"")[1]
                        if parts.startswith('[utcdate '):
                            start_date = parts.split("\"")[1]
                        if parts.startswith('[utctime '):
                            start_time = parts.split("\"")[1]
                        if parts.startswith('[enddate '):
                            end_date = parts.split("\"")[1]
                        if parts.startswith('[endtime '):
                            end_time = parts.split("\"")[1]


                    if start_date != None and start_time != None and end_date != None and end_time != None:
                        user_dict[user + '_chesscom']['active'].append([convert_to_epoch(start_date + "T" + start_time), convert_to_epoch(end_date + "T" + end_time)])

                    if eco not in user_dict[user + '_chesscom']['eco']:
                        user_dict[user + '_chesscom']['eco'][eco] = {'win':0, 'loss':0, 'draw':0}
                    if (result == "0-1" and side == 'black') or (result == "1-0" and side == 'white'):
                        user_dict[user + '_chesscom']['eco'][eco]['win'] += 1
                    elif (result == "0-1" and side == 'white') or (result == "1-0" and side == 'black'):
                        user_dict[user + '_chesscom']['eco'][eco]['loss'] += 1
                    else:
                        user_dict[user + '_chesscom']['eco'][eco]['draw'] += 1
    return user_dict

def parse_lichess_html_file(data):
    info_dict = {}
    for header, regex in TXT_INFO:
        info_dict[header] = None

    for header, regex in TXT_INFO:
        match = re.search(r'' + regex, data)
        if match != None:
            info_dict[header] = match.group(1)

    return info_dict

def find_users(data):
    regex = "<a class=\"offline user-link ulpt\" href=\"/@/([\S]+)\""
    matches = re.findall(r'' + regex, data.decode("utf-8").lower().strip(), re.DOTALL)
    return matches

def find_friends(data_path, username):
    if not os.path.isfile(os.path.join(data_path, username, username + '.tar')):
        log("No Stats File: %s" % (username))
        return []

    file_counter = 1
    followers = []
    while(True):
        with tarfile.open(os.path.join(data_path, username, username + '.tar'), 'r:') as tar_file:
            follower_filename = FOLLOWER + str(file_counter) + ".html.gz"
            if follower_filename not in tar_file.getnames():
                break
            followers.extend(find_users(gzip.decompress(tar_file.extractfile(follower_filename).read())))
            file_counter += 1
    
    file_counter = 1
    following = []
    while(True):
        with tarfile.open(os.path.join(data_path, username, username + '.tar'), 'r:') as tar_file:
            following_filename = FOLLOWING + str(file_counter) + ".html.gz"
            if following_filename not in tar_file.getnames():
                break
            following.extend(find_users(gzip.decompress(tar_file.extractfile(following_filename).read())))
            file_counter += 1

    return list(set(followers) & set(following))

def get_sec(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

# 1. e4 { [%clk 0:01:00] } e5 { [%clk 0:01:00] } 2. nf3 { [%clk 0:00:59] } c5 { [%clk 0:00:59] }
def calculate_time(pgn, time_control):
    black_previous = None
    white_previous = None
    curr_move = 'white'
    total_time = 0

    parts = re.findall(r"\[%clk ([\S]+)\] \}", pgn)
    turn = 0
    for part in parts:
        part = part.split(".")[0]
        seconds = get_sec(part)
        if curr_move == 'white':
            if white_previous != None:
                total_time += white_previous - seconds + time_control
            white_previous = seconds
            curr_move = 'black'
        elif curr_move == 'black':
            if black_previous != None:
                total_time += black_previous - seconds + time_control
            black_previous = seconds
            curr_move = 'white'
            turn += 1

    return total_time

def load_lichess_data(path, user_list):
    user_dict = {}
    log("Loading Games")
    for game_month in os.listdir(os.path.join(path, LICHESS_GAMES)):
        log("Game %s" % (game_month))
        with open(os.path.join(path, LICHESS_GAMES, game_month), 'r', encoding="utf-8") as game_file:
            month_data = json.load(game_file)
            for user in user_list:
                user_dict[user + '_lichess'] = {'eco' : {}, 'opponents': [], 'active' : []}
                if user in month_data:
                    for game in month_data[user]:
                        game_list = []
                        side = 'black'
                        result = None
                        eco = None
                        date = None
                        time = None
                        time_played = 0
                        time_control = 0
                        for item in game:
                            line = item.encode('ascii', 'ignore').decode()
                            if line.startswith('[white \"'):
                                user_dict[user + '_lichess']['opponents'].append(line.split("\"")[1])
                                if line.split("\"")[1] == user:
                                    side = 'white'
                            if line.startswith('[black \"'):
                                user_dict[user + '_lichess']['opponents'].append(line.split("\"")[1])
                            if line.startswith('[result '):
                                result = line.split("\"")[1]
                            if line.startswith('[eco '):
                                eco = line.split("\"")[1]
                            if line.startswith('[timecontrol '):
                                if len(line.split("\"")[1].split("+")) > 1:
                                    time_control = int(line.split("\"")[1].split("+")[1])
                            if line.startswith('1. '):
                                time_played = calculate_time(line, time_control)
                            if line.startswith('[utcdate '):
                                date = line.split("\"")[1]
                            if line.startswith('[utctime '):
                                time = line.split("\"")[1]

                        if eco not in user_dict[user + '_lichess']['eco']:
                            user_dict[user + '_lichess']['eco'][eco] = {'win':0, 'loss':0, 'draw':0}

                        if (result == "0-1" and side == 'black') or (result == "1-0" and side == 'white'):
                            user_dict[user + '_lichess']['eco'][eco]['win']  += 1
                        elif (result == "0-1" and side == 'white') or (result == "1-0" and side == 'black'):
                            user_dict[user + '_lichess']['eco'][eco]['loss']  += 1
                        else:
                            user_dict[user + '_lichess']['eco'][eco]['draw']  += 1
                        if date != None and time != None:
                            epoch_start = convert_to_epoch(date + "T" + time)
                            user_dict[user + '_lichess']['active'].append([epoch_start, epoch_start + time_played])
                else:
                    log("User: %s not in Game File: %s" % (user, os.path.join(path, LICHESS_GAMES, game_month)))
                user_dict[user + '_lichess']['opponents'] = list(set(user_dict[user + '_lichess']['opponents']))
    log("Finished Loading Games")

    for user in user_list:
        with tarfile.open(os.path.join(path, user, user + '.tar'), 'r:') as tar_file:
            if not os.path.exists(os.path.join(path, user)):
                log(("Directory does not Exist: %s") % (os.path.join(path, user)))
                continue

            filename = OUTPUT_PROFILE
            profile_json = {}
            if filename not in tar_file.getnames():
                log("File does not exist: %s" % (filename))
                for header, regex in TXT_INFO:
                    profile_json[header] = None
            else:
                data = gzip.decompress(tar_file.extractfile(filename).read()).decode('unicode-escape').encode("ascii", errors="ignore").decode()
                profile_json = parse_lichess_html_file(data)
            
            for key in profile_json:
                user_dict[user + '_lichess'][key] = profile_json[key]

            if user_dict[user + '_lichess']['joined'] != None:
                user_dict[user + '_lichess']['joined'] = mktime(strptime(user_dict[user + '_lichess']['joined'], '%d-%b-%Y'))
            if user_dict[user + '_lichess']['last_online'] != None:
                user_dict[user + '_lichess']['last_online'] = mktime(strptime(user_dict[user + '_lichess']['last_online'], '%Y-%m-%dT%H:%M:%S.%fZ'))

            friends = find_friends(path, user)
            user_dict[user + '_lichess']['friends'] = list(friends)
            user_dict[user + '_lichess']['website'] = LICHESS
            user_dict[user + '_lichess']['username'] = user
    return user_dict

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 2 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <data path> <ground truth path>" % (executable), file = sys.stderr)
        sys.exit(1)

    data_path = args.pop(0)
    ground_truth_path = args.pop(0)

    return data_path, ground_truth_path

def main():
    data_path, ground_truth_path = _load_args(sys.argv)
    ground_truth_data = load_data(ground_truth_path)
    chesscom, lichess = load_queries(ground_truth_data)

    chesscom_dict = load_chesscom_data(os.path.join(data_path, CHESSCOM), chesscom)
    lichess_dict = load_lichess_data(os.path.join(data_path, LICHESS), lichess)
    
    final_data_dict = {**chesscom_dict, **lichess_dict}

    with open(os.path.join(data_path, "finalized_data.json"), 'w') as out_file:
        json.dump(final_data_dict, out_file, indent=4)

if (__name__ == '__main__'):
    main()
