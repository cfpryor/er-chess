import gzip
import json
import os
import random
import sys
import tarfile
import time

import scrape_chesscom

# Files
SEEN_LIST = 'seen.txt'
COMPLETED_LIST = 'completed.txt'

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

def load_set(path):
    log("Loading: %s" % (path))
    if not os.path.isfile(path):
        log("File does not exist: %s" % (path), level = 'WARNING')
        sys.exit(1)

    return set(line.strip() for line in open(path, 'r'))

def run_scraping(data_path):
    log("Starting Scrape")

    # while(True): Need to loop

    log("Loading Seen and Completed Lists")
    seen_set = load_set(os.path.join(data_path, SEEN_LIST))
    completed_set = load_set(os.path.join(data_path, COMPLETED_LIST))

    log("Picking User")
    while(True):
        username = random.sample(seen_set, 1)[0]

        # Repick user if already completed or if the directory exists
        if username not in completed_set:
            if not os.path.exists(os.path.join(data_path, username)):
                os.mkdir(os.path.join(data_path, username))
                break

    log("Scraping for User: %s" % (username))
    new_opponents = scrape_chesscom.fetch_data(username, os.path.join(data_path, username)) - seen_set

    log("Appending to Seen and Completed")
    with open(os.path.join(data_path, SEEN_LIST), "a") as seen_file:
        seen_file.write("\n".join(list(new_opponents)) + "\n")

    with open(os.path.join(data_path, COMPLETED_LIST), "a") as completed_file:
        completed_file.write(username + "\n")

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 1 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <data path>" % (executable), file = sys.stderr)
        sys.exit(1)

    data_path = args.pop(0)

    return data_path

def main():
    data_path = _load_args(sys.argv)
    run_scraping(data_path)

if (__name__ == '__main__'):
    main()
