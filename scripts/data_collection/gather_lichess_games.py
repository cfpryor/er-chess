import bz2
import json
import os
import random
import sys
import tarfile
import time

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

def gather_data(users, path):
    count = 0
    game = []
    gathering_white = None
    gathering_black = None

    with bz2.BZ2File(path, 'r') as pgn_file:
        for line in pgn_file:
            count += 1
            if count % 100000 == 0:
                log(("Line %d of 623582920") % (count))

            line = line.decode("utf-8").lower().strip()
            if line.startswith("[event"):
                if gathering_white != None:
                    users[gathering_white].append(game)
                    gathering_white = None
                if gathering_black != None:
                    users[gathering_black].append(game)
                    gathering_black = None
                game = [line]
            else:
                game.append(line)

            if line.startswith("[white"):
                username = line.split("\"")[1]
                if username in users:
                    gathering_white = username

            if line.startswith("[black"):
                username = line.split("\"")[1]
                if username in users:
                    gathering_black = username

    return users

def load_data(path):
    log("Loading: %s" % (path))
    if not os.path.isfile(path):
        log("File does not exist: %s" % (path), level = 'WARNING')
        sys.exit(1)

    with open(path, 'r') as file:
        return json.load(file)

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 3 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <data path> <user_path> <output_filename>" % (executable), file = sys.stderr)
        sys.exit(1)

    data_path = args.pop(0)
    user_path = args.pop(0)
    output_filename = args.pop(0)

    return data_path, user_path, output_filename

def main():
    data_path, user_path, output_filename = _load_args(sys.argv)

    users_list = load_data(user_path)
    users_dict = {}
    for user in users_list:
        users_dict[user] = []

    users = gather_data(users_dict, data_path)
    with open(output_filename, 'w') as out_file:
        json.dump(users, out_file, indent=4)

if (__name__ == '__main__'):
    main()
