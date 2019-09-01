import gzip
import json
import os
import re
import sys
import string
import tarfile
import time
import textdistance
import jellyfish
import pycountry

from time import strptime, mktime
from pyjarowinkler import distance

FEATURE_LIST = ['name', 'location', 'country', 'is_streamer', 'followers', 'last_online', 'status', 'joined', 'title', 'fide', 'ucsf', 'bullet', 'lightning', 'rapid', 'tactics']

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

def jaro_winkler(string_1, string_2):
    return distance.get_jaro_distance(string_1, string_2, winkler=True, scaling=0.1)

def levenshtein(string_1, string_2):
    return 1 - jellyfish.levenshtein_distance(string_1, string_2) / max(len(string_1), len(string_2))

def abriviate_country(country_full):
    if len(country_full) == 2:
        return country_full

    countries = {}
    for country in pycountry.countries:
        countries[country.name] = country.alpha_2

    return countries.get(country_full, 'Unknown code')

def find_max_min(data, users, key):
    min_l = 1000000
    max_l = 0
    min_c = 1000000
    max_c = 0

    for user in users:
        if user not in data:
            continue
        if key in data[user] and data[user][key] != None:
            value = int(data[user][key])
            if data[user]["website"] == 'lichess':
                if value > max_l:
                    max_l = value
                if value < min_l:
                    min_l = value
            if data[user]["website"] == 'chesscom':
                if value > max_c:
                    max_c = value
                if value < min_c:
                    min_c = value
    return [min_l, max_l, min_c, max_c]

def normalize_rating(rating, min_value, max_value, center):
    rating = int(rating)
    if rating < center:
        return ((rating - min_value) / (center - min_value)) / 2
    else:
        return (1 - ((max_value - rating) / (max_value - center))) / 2 + 0.5

def calculate_rating_similarity(data, user_i, user_j, time_control, min_max_list):
    user_values = []
    for user in [user_i, user_j]:
        if time_control in data[user] and data[user][time_control] != None:
            if data[user]['website'] == 'lichess':
                user_values.append(normalize_rating(data[user][time_control], min_max_list[0], min_max_list[1], 1500))
            if data[user]['website'] == 'chesscom':
                user_values.append(normalize_rating(data[user][time_control], min_max_list[2], min_max_list[3], 1200))
        else:
            user_values.append(0.5)

    return (1 - abs(user_values[0] - user_values[1]))**2

def calculate_eco_stats(eco_dict, top_n):
    win_list = []
    loss_list = []
    draw_list = []
    total_list = []
    for key in eco_dict:
        win_list.append((key, int(eco_dict[key]['win'])))
        loss_list.append((key, int(eco_dict[key]['loss'])))
        draw_list.append((key, int(eco_dict[key]['draw'])))
        total_list.append((key, int(eco_dict[key]['win']) + int(eco_dict[key]['loss']) + int(eco_dict[key]['draw'])))
    win_list_sorted = sorted(win_list, key=lambda tup: tup[1], reverse = True)
    loss_list_sorted = sorted(loss_list, key=lambda tup: tup[1], reverse = True)
    draw_list_sorted = sorted(draw_list, key=lambda tup: tup[1], reverse = True)
    total_list_sorted = sorted(total_list, key=lambda tup: tup[1], reverse = True)

    win_set = set()
    loss_set = set()
    draw_set = set()
    total_set = set()
    for i in range(0, top_n):
        win_set.add(win_list_sorted[i][0])
        loss_set.add(loss_list_sorted[i][0])
        draw_set.add(draw_list_sorted[i][0])
        total_set.add(total_list_sorted[i][0])

    return [win_set, loss_set, draw_set, total_set]

def active_same_time(time_list_i, time_list_j):
    both_times = []
    for start, end in time_list_i:
        both_times.append([start, end, 'i'])
    for start, end in time_list_j:
        both_times.append([start, end, 'j'])
 
    previous_key = None
    for time_start, time_end, key in sorted(both_times):
        #print(time_start, time_end, key)
        if previous_key == None:
            previous_end = int(time_end)
            previous_key = key
            continue
        if int(time_start) < previous_end and key != previous_key:
            return 1.0
    return 0.0

def active_same_time_old(time_list_i, time_list_j):
    for start_time_i, end_time_i in time_list_i:
        for start_time_j, end_time_j in time_list_j:
            if start_time_i < start_time_j:
                if end_time_i > start_time_j:
                    return 1.0
            else:
                if end_time_j > start_time_i:
                    return 1.0
    return 0.0

def create_features(data, ground_truth, ground_truth_value):
    output = []
    rows = []
    user_set = set()
    for user_i, user_j in ground_truth:
        user_set.add(user_i)
        user_set.add(user_j)

    for user_i, user_j in sorted(list(ground_truth)):
        row = []
        if user_i not in data or user_j not in data:
            continue
        if 'username' not in data[user_i]:
            print(data[user_i])
            continue
        if 'username' not in data[user_j]:
            print(data[user_j])
            continue

        row.append([[data[user_i]['username'], data[user_i]['website']], [data[user_j]['username'], data[user_j]['website']]])
        
        if data[user_i]['username'] == None or data[user_j]['username'] == None:
            row.append(0.5)
            row.append(0.5)
        else:
            row.append(jaro_winkler(data[user_i]['username'], data[user_j]['username']))
            row.append(levenshtein(data[user_i]['username'], data[user_j]['username']))

        if data[user_i]['name'] == None or len(data[user_i]['name']) == 0 or data[user_j]['name'] == None or len(data[user_j]['name']) == 0:
            row.append(0.5)
            row.append(0.5)
        else:
            row.append(jaro_winkler(data[user_i]['name'], data[user_j]['name']))
            row.append(levenshtein(data[user_i]['name'], data[user_j]['name']))

        if data[user_i]['location'] == None or len(data[user_i]['location']) == 0 or data[user_j]['location'] == None or len(data[user_j]['location']) == 0:
            row.append(0.5)
        else:
            row.append(jaro_winkler(data[user_i]['location'], data[user_j]['location']))

        if data[user_i]['country'] == None or data[user_j]['country'] == None:
            row.append(0.5)
        else:
            if abriviate_country(data[user_i]['country'].split("/")[-1]) == abriviate_country(data[user_j]['country'].split("/")[-1]):
                row.append(1.0)
            else:
                row.append(0.0)
        
        if data[user_i]['opponents'] == None or data[user_j]['opponents'] == None:
            row.append(0.5)
        else:
            if (data[user_j]['website'] == data[user_i]['website']) and (data[user_j]['username'] in data[user_i]['opponents'] or data[user_j]['username'] in data[user_j]['opponents']):
                row.append(1.0)
            else:
                row.append(0.0)

        if data[user_i]['friends'] == None or data[user_j]['friends'] == None:
            row.append(0.5)
        else:
            if (data[user_j]['website'] == data[user_i]['website']) and (data[user_j]['username'] in data[user_i]['friends'] or data[user_j]['username'] in data[user_j]['friends']):
                row.append(1.0)
            else:
                row.append(0.0)

        if data[user_j]['website'] == data[user_i]['website']:
            row.append(1.0)
        else:
            row.append(0.0)

        row.append(calculate_rating_similarity(data, user_i, user_j, 'bullet', find_max_min(data, user_set, 'bullet')))
        row.append(calculate_rating_similarity(data, user_i, user_j, 'lightning', find_max_min(data, user_set, 'lightning')))
        row.append(calculate_rating_similarity(data, user_i, user_j, 'rapid', find_max_min(data, user_set, 'rapid')))
        row.append(calculate_rating_similarity(data, user_i, user_j, 'tactics', find_max_min(data, user_set, 'tactics')))

        if 'is_streamer' not in data[user_i] or data[user_i]['is_streamer'] == None:
            if 'is_streamer' not in data[user_j] or data[user_j]['is_streamer'] == None:
                row.append(1.0)
            else:
                row.append(0.0)
        else:
            if 'is_streamer' not in data[user_j] or data[user_j]['is_streamer'] == None:
                row.append(0.0)
            else:
                row.append(1.0)

        if 'title' not in data[user_i] or 'title' not in data[user_j]:
            row.append(0.0)
        elif data[user_i]['title'] == None or data[user_j]['title'] == None:
            row.append(0.5)
        elif data[user_i]['title'] == data[user_j]['title']:
            row.append(1.0)
        else:
            row.append(0.0)
        
        if 'eco' not in data[user_i] or 'eco' not in data[user_j] or len(data[user_i]['eco']) < 3 or len(data[user_j]['eco']) < 3:
            row.append(0.0)
            row.append(0.0)
            row.append(0.0)
            row.append(0.0)
        else:
            top_eco_tuple_i = calculate_eco_stats(data[user_i]['eco'], 3)
            top_eco_tuple_j = calculate_eco_stats(data[user_j]['eco'], 3)
            for iterator in range(0, len(top_eco_tuple_i)):
                row.append(len(top_eco_tuple_i[iterator].intersection(top_eco_tuple_j[iterator])) / 3)

        #if 'active' not in data[user_i] or 'active' not in data[user_j]:
        #    append(0.0)
        #else:
        #    row.append(active_same_time(data[user_i]['active'], data[user_j]['active']))

        row.append(ground_truth_value)
        rows.append(row)
        #print(row)
    return rows

def find_negative_truth(user_list, data, positive_ground_truth):
    negative_ground_truth_set = set()
    log("Length of user list: %d" % (len(user_list)))
    counter = 0
    for i in range(0, len(user_list)):
        if user_list[i] not in data or 'active' not in data[user_list[i]]:
            continue

        for j in range(i+1, len(user_list)):
            counter += 1
            if user_list[j] not in data or 'active' not in data[user_list[j]]:
                continue

            if (user_list[j], user_list[i]) in positive_ground_truth or (user_list[i], user_list[j]) in positive_ground_truth:
                continue

            if counter % 1000 == 0:
                log("Counter: %d Set Length: %d" % (counter, len(negative_ground_truth_set)))

            if active_same_time(data[user_list[j]]['active'], data[user_list[i]]['active']):
                negative_pair = [(user_list[i], data[user_list[i]]['website']), (user_list[j], data[user_list[j]]['website'])]
                sorted_tuple = tuple(sorted(negative_pair))
                negative_ground_truth_set.add(sorted_tuple)

    return(negative_ground_truth_set)

def load_ground_truth(path):
    log("Loading: %s" % (path))
    if not os.path.isfile(path):
        log("File does not exist: %s" % (path), level = 'WARNING')
        sys.exit(1)

    truth_set = set()
    with open(path, 'r') as file:
        data = json.load(file)
        for pair in data:
            truth_pair = []
            for user in pair:
                truth_pair.append(user[0] + "_" + user[1])
            truth_set.add(tuple(sorted(truth_pair)))
    return truth_set

def load_ground_truth_negative(path):
    log("Loading: %s" % (path))
    if not os.path.isfile(path):
        log("File does not exist: %s" % (path), level = 'WARNING')
        sys.exit(1)

    truth_set = set()
    with open(path, 'r') as file:
        data = json.load(file)
        for pair in data:
            truth_pair = []
            for user in pair:
                truth_pair.append(user[0])
            truth_set.add(tuple(sorted(truth_pair)))
    return truth_set

def load_data(path):
    log("Loading: %s" % (path))
    if not os.path.isfile(path):
        log("File does not exist: %s" % (path), level = 'WARNING')
        sys.exit(1)

    with open(path, 'r') as file:
        return json.load(file)

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
    ground_truth_data = load_ground_truth(ground_truth_path)
    negative_truth_data = load_ground_truth_negative('negative_ground_truth.json')
    data = load_data(data_path)

    positive_rows = create_features(data, ground_truth_data, 1.0)
    negative_rows = create_features(data, negative_truth_data, 0.0)

    print(len(positive_rows), len(negative_rows))

    positive_rows.extend(negative_rows)
    print(len(positive_rows))
    with open("features.txt", 'w') as out_file:
        json.dump(positive_rows, out_file, indent=4)

    #user_set = set()
    #for user_i, user_j in ground_truth_data:
    #    user_set.add(user_i)
    #    user_set.add(user_j)

    #ground_negative_truth = find_negative_truth(list(user_set), data, ground_truth_data)
    #dump_list = []
    #for pair_i, pair_j in ground_negative_truth:
    #    dump_list.append([list(pair_i), list(pair_j)])
    #with open("negative_ground_truth.json", 'w') as out_file:
    #   json.dump(dump_list, out_file, indent=4)
    #print(len(ground_negative_truth))

if (__name__ == '__main__'):
    main()
