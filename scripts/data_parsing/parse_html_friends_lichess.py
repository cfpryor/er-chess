import gzip
import json
import os
import re
import sys
import tarfile
import time

# class="offline user-link ulpt" href="/@/

# Files
SEEN_LIST = 'seen.txt'
COMPLETED_LIST = 'completed.txt'
OPPONENT_LIST = 'opponents.json.gz'

FOLLOWER = 'followers_'
FOLLOWING = 'following_'

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
    regex = "<a class=\"offline user-link ulpt\" href=\"/@/([\S]+)\""
    matches = re.findall(r'' + regex, data.decode("utf-8").lower().strip(), re.DOTALL)
    return matches

def parse_html_files(data_path):
    user_dict = {}
    friend_set = set()
    counter = 0

    for username in os.listdir(data_path):
        # Check if file exists
        if not os.path.isfile(os.path.join(data_path, username, username + '.tar')):
            log("No Stats File: %s" % (username))
            continue

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

        user_dict[username] = list(set(followers) & set(following))
        friend_set |= set(followers) & set(following)

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

    print(len(friend_set))
    #print(friend_list, friend_set)

if (__name__ == '__main__'):
    main()
