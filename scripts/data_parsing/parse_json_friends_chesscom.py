import gzip
import json
import os
import re
import sys
import tarfile
import time

# Files
SEEN_LIST = 'seen.txt'
COMPLETED_LIST = 'completed.txt'
OPPONENT_LIST = 'opponents.json.gz'

FRIENDS = 'freinds_'

FILES = ["friends_bullet.json.gz", "friends_blitz.json.gz", "friends_rapid.json.gz"]

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

def find_users(data):
    user_set = set()
    for user in json.loads(data.decode("utf-8")):
        user_set.add(user['user']['username'])

    return user_set

def parse_html_files(data_path):
    user_dict = {}
    friend_set = set()

    for username in os.listdir(data_path):
        # Check if file exists
        if not os.path.isfile(os.path.join(data_path, username, username + '.tar')):
            log("No Tar File: %s" % (username))
            continue

        friends = set()
        with tarfile.open(os.path.join(data_path, username, username + '.tar'), 'r:') as tar_file:
            for filename in FILES:
                if filename not in tar_file.getnames():
                    continue
                friends |= find_users(gzip.decompress(tar_file.extractfile(filename).read()))

        user_dict[username] = list(friends)
        friend_set |= friends

    return user_dict, friend_set

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 1 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <data path>" % (executable), file = sys.stderr)
        sys.exit(1)

    data_path = args.pop(0)

    return data_path

def main():
    data_path = _load_args(sys.argv)
    user_dict, friend_set = parse_html_files(data_path)

    log(str(len(friend_set)))

if (__name__ == '__main__'):
    main()
