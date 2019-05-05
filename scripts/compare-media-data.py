import json
import os
import re
import sys
import time

CHESSCOM_FILENAME = 'chesscom_profiles.json'
LICHESS_FILENAME = 'lichess_profiles.json'

CHESSCOM_KEY = 'chesscom'
LICHESS_KEY = 'lichess'

def write_user_list(user_set, path):
    if not os.path.isdir(path):
        os.mkdir(path)

    chesscom_list = []
    lichess_list = []

    for user, website in user_set:
        if website == CHESSCOM_KEY:
            chesscom_list.append(user)
        elif website == LICHESS_KEY:
            lichess_list.append(user)
        else:
            print("Error -- User: %s Website: %s" % (user, website))

    with open(os.path.join(path, CHESSCOM_FILENAME), 'w') as file:
        json.dump(chesscom_list, file, indent = 4)
    
    with open(os.path.join(path, LICHESS_FILENAME), 'w') as file:
        json.dump(lichess_list, file, indent = 4)

def load_data(path):
    with open(path, 'r') as file:
        return json.load(file)

def match_ground_truth(truth_data_dict):
    mapping_dict = {}
    direct_match_dict = {}
    match_count = 0
    # 'Website', 'Match', 'Match_Website', 'Match_Full'
    users_set = set()

    chesscom = '(chess).com/member/([^"]+)'
    lichess = '(lichess).org/@/([^"]+)'

    for user_key in truth_data_dict:
        for handle_index in range(len(truth_data_dict[user_key]) - 1):
            if truth_data_dict[user_key][handle_index] == None:
                continue

            if handle_index == 11:
                if 'lichess.org/@' not in truth_data_dict[user_key][handle_index]:
                    continue
                if handle_index < len(truth_data_dict[user_key]):
                    users_set.add((user_key, truth_data_dict[user_key][-1]))
                    match = re.search(r'' + lichess, truth_data_dict[user_key][handle_index])
                    if match != None:
                        users_set.add((match.group(2), match.group(1)))
                    if user_key not in direct_match_dict:
                        direct_match_dict[user_key] = []
                    direct_match_dict[user_key].append([truth_data_dict[user_key][-1], match.group(2), LICHESS_KEY, truth_data_dict[user_key][handle_index]])

            if handle_index == 15:
                if handle_index < len(truth_data_dict[user_key]):
                    users_set.add((user_key, truth_data_dict[user_key][-1]))
                    match = re.search(r'' + chesscom, truth_data_dict[user_key][handle_index])
                    if match != None:
                        users_set.add((match.group(2), match.group(1) + 'com'))
                    if user_key not in direct_match_dict:
                        direct_match_dict[user_key] = []
                    direct_match_dict[user_key].append([truth_data_dict[user_key][-1], match.group(2), CHESSCOM_KEY, truth_data_dict[user_key][handle_index]])

            if truth_data_dict[user_key][handle_index] not in mapping_dict:
                mapping_dict[truth_data_dict[user_key][handle_index]] = []
            mapping_dict[truth_data_dict[user_key][handle_index]].append((user_key, truth_data_dict[user_key][-1]))
            if  len(mapping_dict[truth_data_dict[user_key][handle_index]]) > 1:
                users_set.add((user_key, truth_data_dict[user_key][-1]))


    for key in mapping_dict:
        if (len(mapping_dict[key]) > 1):
            match_count += 1
            #print(key, mapping_dict[key], len(mapping_dict[key]))
            for user_i, website_i in mapping_dict[key]:
                for user_j, website_j in mapping_dict[key]:
                    if user_i != user_j:
                        if user_i not in direct_match_dict:
                            direct_match_dict[user_i] = []
                        direct_match_dict[user_i].append([website_i, user_j, website_j, key])

    with open('positive_ground_truth.json', 'w') as file:
        json.dump(direct_match_dict, file, indent = 4)

    print(len(users_set), len(direct_match_dict), match_count)
    return users_set

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 2 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <data path> <output path>" % (executable), file = sys.stderr)
        sys.exit(1)

    data_path = args.pop(0)
    output_path = args.pop(0)

    return data_path, output_path

def main():
    data_path, output_path = _load_args(sys.argv)
    total_dict = {}

    for data_file in os.listdir(data_path):
        data_dict = load_data(os.path.join(data_path, data_file))
        for key in data_dict:
            data_dict[key].append(data_file.split("_")[0])
        total_dict.update(data_dict)

    users_set = match_ground_truth(total_dict)
    #write_user_list(users_set, output_path)

if (__name__ == '__main__'):
    main()
