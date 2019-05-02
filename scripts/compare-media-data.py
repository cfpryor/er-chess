import json
import os
import re
import sys
import time

def load_data(path):
    with open(path, 'r') as file:
        return json.load(file)

def match_ground_truth(truth_data_dict):
    mapping_dict = {}
    direct_match_dict = {}

    for user_key in truth_data_dict:
        for handle_index in range(len(truth_data_dict[user_key])):
            if truth_data_dict[user_key][handle_index] == None:
                continue

            if handle_index == 11:
                direct_match_dict[user_key] = truth_data_dict[user_key][handle_index]

            if truth_data_dict[user_key][handle_index] not in mapping_dict:
                mapping_dict[truth_data_dict[user_key][handle_index]] = []
            mapping_dict[truth_data_dict[user_key][handle_index]].append(user_key)

    for key in direct_match_dict:
        print(key, direct_match_dict[key])

    for key in mapping_dict:
        if (len(mapping_dict[key]) > 1):
            print(key, mapping_dict[key], len(mapping_dict[key]))

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 1 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <data path>" % (executable), file = sys.stderr)
        sys.exit(1)

    data_path = args.pop(0)

    return data_path

def main():
    data_path = _load_args(sys.argv)
    total_dict = {}

    for data_file in os.listdir(data_path):
        data_dict = load_data(os.path.join(data_path, data_file))
        total_dict.update(data_dict)

    match_ground_truth(total_dict)

if (__name__ == '__main__'):
    main()
