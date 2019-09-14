import json
import os
import sys

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 1 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <data path>" % (executable), file = sys.stderr)
        sys.exit(1)

    data_path = args.pop(0)

    return data_path

def main():
    data_path = _load_args(sys.argv)
    user_set = set()

    for data_filename in os.listdir(data_path):
        path = os.path.join(data_path, data_filename)
        with open(path, 'r') as data_file:
            user_set |= set(json.load(data_file))

    with open(os.path.join(data_path, 'user_list.json'), 'w') as out_file:
        json.dump(list(user_set), out_file, indent=4)

if (__name__ == '__main__'):
    main()
