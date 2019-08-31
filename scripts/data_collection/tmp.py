import gzip
import json
import os
import socket
import sys
import tarfile
import time
import urllib.request

import scrape_chesscom
import scrape_lichess

# Files
SEEN_LIST = 'seen.txt'
COMPLETED_LIST = 'completed.txt'
CHESSCOM_DIR = 'chesscom'
LICHESS_DIR = 'lichess'

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

def load_data(path):
    log("Loading: %s" % (path))
    if not os.path.isfile(path):
        log("File does not exist: %s" % (path), level = 'WARNING')
        sys.exit(1)

    with open(path, 'r') as file:
        return json.load(file)

def load_queries(data):
    chesscom_set = set()
    lichess_set = set()

    for pair in data:
        for user in pair:
            if user[1] == 'lichess':
                lichess_set.add(user[0])
            if user[1] == 'chesscom':
                chesscom_set.add(user[0])

    return chesscom_set, lichess_set

def gather_chesscom_data(users, path):
    log("Starting Scrape")
    seen_set = set()

    for username in users:
        if not os.path.exists(os.path.join(path, username)):
            os.mkdir(os.path.join(path, username))
        else:
            log("Data Exists for this User: %s" % (username))
            continue

        log("Scraping for User: %s" % (username))
        seen_set |= scrape_chesscom.fetch_data(username, os.path.join(path, username))

    log("Writing Seen and Completed")
    with open(os.path.join(path, SEEN_LIST), "w") as seen_file:
        seen_file.write("\n".join(list(seen_set)) + "\n")

    with open(os.path.join(path, COMPLETED_LIST), "w") as completed_file:
        completed_file.write("\n".join(list(users)) + "\n")

def gather_lichess_data(users, path):
    log("Starting Scrape")
    seen_set = set()

    for username in users:
        if not os.path.exists(os.path.join(path, username)):
            os.mkdir(os.path.join(path, username))
        else:
            log("Data Exists for this User: %s" % (username))
            continue

        log("Scraping for User: %s" % (username))
        scrape_lichess.fetch_data(username, os.path.join(path, username))

    log("Writing Completed")
    with open(os.path.join(path, COMPLETED_LIST), "w") as completed_file:
        completed_file.write("\n".join(list(users)) + "\n")

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
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    ground_truth_data = load_data(data_path)
    chesscom, lichess = load_queries(ground_truth_data)
  
    #if not os.path.exists(os.path.join(output_path, CHESSCOM_DIR)):
    #    os.mkdir(os.path.join(output_path, CHESSCOM_DIR))
    #gather_chesscom_data(chesscom, os.path.join(output_path, CHESSCOM_DIR))
    
    if not os.path.exists(os.path.join(output_path, LICHESS_DIR)):
        os.mkdir(os.path.join(output_path, LICHESS_DIR))
    gather_lichess_data(lichess, os.path.join(output_path, LICHESS_DIR))

if (__name__ == '__main__'):
    main()
