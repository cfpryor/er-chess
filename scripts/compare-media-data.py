import json
import os
import re
import sys
import time

CHESSCOM_FILENAME = 'chesscom_profiles.json'
LICHESS_FILENAME = 'lichess_profiles.json'
POS_GROUND_TRUTH_FILENAME = 'positive_ground_truth.json'

CHESSCOM_KEY = 'chesscom'
LICHESS_KEY = 'lichess'

def write_user_list(user_list, path):
    with open(path, 'w') as file:
        json.dump(user_list, file, indent = 4)

def load_data(path):
    with open(path, 'r') as file:
        return json.load(file)

def match_truth(id_dict, output_path):
    chesscom_regex = '(chess).com/member/([^"]+)'
    lichess_regex = '(lichess).org/@/([^"]+)'
    
    handle_mapping = set()
    chesscom_set = set()
    lichess_set = set()

    handle_dict = {}

    for user_id in id_dict:
        if user_id[1] == CHESSCOM_KEY:
            chesscom_set.add(user_id[0])
        if user_id[1] == LICHESS_KEY:
            lichess_set.add(user_id[0])

        for handle_id in range(1, len(id_dict[user_id]) - 1):
            if id_dict[user_id][handle_id] == None:
                continue
            
            match = re.search(r'' + lichess_regex, id_dict[user_id][handle_id])
            if match != None:
                user_id_match = (match.group(2).lower(), LICHESS_KEY)
                lichess_set.add(match.group(2).lower())
                
                if (user_id, user_id_match) not in handle_mapping and (user_id_match, user_id) not in handle_mapping:
                    handle_mapping.add((user_id, user_id_match))

            match = re.search(r'' + chesscom_regex, id_dict[user_id][handle_id])
            if match != None:
                user_id_match = (match.group(2).lower(), CHESSCOM_KEY)
                chesscom_set.add(match.group(2).lower())

                if (user_id, user_id_match) not in handle_mapping and (user_id_match, user_id) not in handle_mapping:
                    handle_mapping.add((user_id, user_id_match))

            if id_dict[user_id][handle_id] not in handle_dict:
                handle_dict[id_dict[user_id][handle_id]] = []

            handle_dict[id_dict[user_id][handle_id]].append(user_id)
    
    for key in handle_dict:
        if key in ["facebook.com/\"", "chess.com/member/gary_sorkin\"><a", "youtube.com/channel/UCKGR-mRvc0U3lS27SC9pemQ\""]:
            continue
        if len(handle_dict[key]) > 1:
            for i in range(0, len(handle_dict[key])):
                for j in range(i, len(handle_dict[key])):
                    if (handle_dict[key][i], handle_dict[key][j]) not in handle_mapping and (handle_dict[key][j], handle_dict[key][i]) not in handle_mapping:
                        handle_mapping.add((handle_dict[key][i], handle_dict[key][j]))

    write_user_list(list(chesscom_set), os.path.join(output_path, CHESSCOM_FILENAME))
    write_user_list(list(lichess_set), os.path.join(output_path, LICHESS_FILENAME))
    write_user_list(list(handle_mapping), os.path.join(output_path, POS_GROUND_TRUTH_FILENAME))

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
                    direct_match_dict[user_key].append([truth_data_dict[user_key][-1], match.group(2).lower(), LICHESS_KEY, truth_data_dict[user_key][handle_index]])

            if handle_index == 15:
                if handle_index < len(truth_data_dict[user_key]):
                    users_set.add((user_key, truth_data_dict[user_key][-1]))
                    match = re.search(r'' + chesscom, truth_data_dict[user_key][handle_index])
                    if match != None:
                        users_set.add((match.group(2), match.group(1) + 'com'))
                    if user_key not in direct_match_dict:
                        direct_match_dict[user_key] = []
                    direct_match_dict[user_key].append([truth_data_dict[user_key][-1], match.group(2).lower(), CHESSCOM_KEY, truth_data_dict[user_key][handle_index]])

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
                        direct_match_dict[user_i].append([website_i, user_j.lower(), website_j, key])

    with open('positive_ground_truth.json', 'w') as file:
        json.dump(direct_match_dict, file, indent = 4)

    print(len(users_set), len(direct_match_dict), match_count)
    return users_set

def assign_ids(data):
    id_dict = {}
    
    for data_dict in data:
        for user in data_dict:
            if (user.lower(), data_dict[user][-1]) not in id_dict:
                id_dict[(user.lower(), data_dict[user][-1])] = [user.lower()] + data_dict[user]

    return id_dict

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
    data_list = []

    for data_file in os.listdir(data_path):
        data_dict = load_data(os.path.join(data_path, data_file))
        for key in data_dict:
            data_dict[key].append(data_file.split("_")[0])
        data_list.append(data_dict)
    
    id_dict = assign_ids(data_list)
    match_truth(id_dict, output_path)
    #for user_id in id_dict:
    #    print(user_id, id_dict[user_id])
    #users_set = match_ground_truth(total_dict)

if (__name__ == '__main__'):
    main()
