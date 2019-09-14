import json
import os
import sys

DEFAULT_NUMBER_SPLITS = 7
FILENAME_PREFIX = '__users_'
FILENAME_SUFFIX = '.json'

def split_users(users, number_splits = DEFAULT_NUMBER_SPLITS):
    splits = []
    split_length = len(users) / float(number_splits)
    previous_split = 0.0

    while previous_split < len(users):
        splits.append(users[int(previous_split):int(previous_split + split_length)])
        previous_split += split_length

    return splits

def load_users(user_path):
    with open(user_path, 'r') as file:
        return json.load(file)

def write_splits(out_path, splits):
    if not os.path.isfile(out_path):
        os.mkdir(out_path)
    
    for i in range(len(splits)):
        with open(os.path.join(out_path, FILENAME_PREFIX + str(i) + FILENAME_SUFFIX), 'w') as file:
            json.dump(splits[i], file, indent = 4)

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
    splits = split_users(user_list)
    write_splits(out_path, splits)

if (__name__ == '__main__'):
    main()
