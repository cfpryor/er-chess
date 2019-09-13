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

def gather_users(path):
    count = 0
    users = set()

    with bz2.BZ2File(path, 'r') as pgn_file:
        for line in pgn_file:
            count += 1
            if count % 100000 == 0:
                log(("Line %d of 623582920") % (count))

            line = line.decode("utf-8").lower().strip()

            if line.startswith("[white"):
                users.add(line.split("\"")[1])

            if line.startswith("[black"):
                users.add(line.split("\"")[1])

    return users

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

    user_list = list(gather_users(data_path))
    log("Number of Users: %d" % (len(user_list)))
    with open(output_path, 'w') as out_file:
        json.dump(user_list, out_file, indent=4)

if (__name__ == '__main__'):
    main()
