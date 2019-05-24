import json
import os
import re
import sys
import time

from pyjarowinkler import distance

FEATURES = ['Username', 'Full_Name', 'Country', 'Followers', 'Bullet_Current', 'Blitz_Current', 'Rapid_Current', 'Tactics_Current', 'FIDE', 'USCF']

def write_data(data, out_path):
    with open(out_path, 'w') as file:
        json.dump(data, file, indent = 4)

def jaro_winkler(string_1, string_2):
    return distance.get_jaro_distance(string_1, string_2, winkler=True, scaling=0.1)

def square_diff(val_1, val_2):
    return (val_1 - val_2) ** 2

def _create_feature_vector_helper(user_i, data_i, user_j, data_j):
    pair_feature = []
    for feature in FEATURES:
        if feature in ['Country']:
            if feature not in data_i or feature not in data_j:
                pair_feature.append(0)
                continue
            if data_i[feature] == None or data_j[feature] == None:
                pair_feature.append(0)
            else:
                if data_i[feature] == data_j[feature]:
                    pair_feature.append(1)
                else:
                    pair_feature.append(0)
        elif feature in ['Username']:
            pair_feature.append(jaro_winkler(user_i, user_j))
        elif feature in ['Full_Name']:
            if feature not in data_i or feature not in data_j:
                pair_feature.append(0)
                continue
            if data_i[feature] == None or data_j[feature] == None:
                pair_feature.append(0)
            else:
                pair_feature.append(jaro_winkler(user_i, user_j))
        elif feature in ['Followers', 'Bullet_Current', 'Blitz_Current', 'Rapid_Current', 'Tactics_Current', 'FIDE', 'USCF']:
            if feature not in data_i or feature not in data_j:
                pair_feature.append(10000000000000)
                continue
            if data_i[feature] == None or data_j[feature] == None:
                pair_feature.append(10000000000000)
            else:
                pair_feature.append(square_diff(int(str(data_i[feature]).replace(',', '')), int(str(data_j[feature]).replace(',', ''))))

    return pair_feature


def create_feature_vector(chesscom_data, lichess_data, positive_truth_list):
    data_list = []

    user_set = set()
    positive_truth_set = set()

    for positive_example in positive_truth_list:
        user_set.add((positive_example[0][0], positive_example[0][1]))
        user_set.add((positive_example[1][0], positive_example[1][1]))
        
        positive_truth_set.add(((positive_example[0][0], positive_example[0][1]), (positive_example[1][0], positive_example[1][1])))

    user_list = list(user_set)

    for i in range(0, len(user_list)): 
        name_i = user_list[i][0]
        if user_list[i][1] == "chesscom":
            if user_list[i][0] not in chesscom_data:
                continue
            data_i = chesscom_data[user_list[i][0]]
        else:
            if user_list[i][0] not in lichess_data:
                continue
            data_i = lichess_data[user_list[i][0]]
        
        for j in range(i + 1, len(user_list)):
            name_j = user_list[j][0]
            
            if user_list[j][1] == "chesscom":
                if user_list[j][0] not in chesscom_data:
                    continue
                data_j = chesscom_data[user_list[j][0]]
            else:
                if user_list[j][0] not in lichess_data:
                    continue
                data_j = lichess_data[user_list[j][0]]

            if (user_list[i], user_list[j]) in positive_truth_set or (user_list[j], user_list[i]) in positive_truth_set:
                feature_vector = _create_feature_vector_helper(name_i, data_i, name_j, data_j)
                data_list.append([(user_list[i], user_list[j])] + feature_vector + [1])
                continue

            skip = False
            for feature in FEATURES:
                if (feature not in data_i or feature not in data_j) and feature != 'Username':
                    skip = True
                    break
            if skip:
                continue

            if data_i['Bullet_Current'] != None and data_j['Bullet_Current'] != None:
                if data_i['Blitz_Current'] != None and data_j['Blitz_Current'] != None:
                    if data_i['Rapid_Current'] != None and data_j['Rapid_Current'] != None:
                        if data_i['Country'] != None and data_j['Country'] != None:
                            if abs(int(data_i['Bullet_Current']) - int(data_j['Bullet_Current'])) > 300:
                                if abs(int(data_i['Blitz_Current']) - int(data_j['Blitz_Current'])) > 300:
                                    if abs(int(data_i['Rapid_Current']) - int(data_j['Rapid_Current'])) > 300:
                                        if data_i['Country'] != data_j['Country'] and jaro_winkler(name_i, name_j) < 0.3:
                                            feature_vector = _create_feature_vector_helper(name_i, data_i, name_j, data_j)
                                            data_list.append([(user_list[i], user_list[j])] + feature_vector + [0])
                                            continue

    print(len(data_list), len(user_list)**2)
    return data_list

def load_users(user_path):
    with open(user_path, 'r') as file:
        return json.load(file)

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 4 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <chesscom_data_path> <lichess_data_path> <positive_truth_data_path> <out_path>" % (executable), file = sys.stderr)
        sys.exit(1)

    chesscom_path = args.pop(0)
    lichess_path = args.pop(0)
    pos_truth_path = args.pop(0)
    out_path = args.pop(0)
    return chesscom_path, lichess_path, pos_truth_path, out_path

def main():
    chesscom_path, lichess_path, pos_truth_path, out_path = _load_args(sys.argv)
    chesscom_data = load_users(chesscom_path)
    lichess_data = load_users(lichess_path)
    pos_truth_data = load_users(pos_truth_path)

    data = create_feature_vector(chesscom_data, lichess_data, pos_truth_data)
    write_data(data, out_path)

if (__name__ == '__main__'):
    main()
