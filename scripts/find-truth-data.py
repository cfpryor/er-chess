import json
import os
import re
import sys
import time

# Desired Profile Section (Chess.com)
PROFILE_START = "<div class=\"section-wrapper\">"
PROFILE_END = "</div>"

# Profile Name
PROFILE = 'profile.txt'

# Logging Constants
LOGGING_NUMBER = 5000

def write_profile_info(profile_dict, path):
    with open(path, 'w') as file:
       json.dump(profile_dict, file, indent = 4)

def fetch_profile_info(username, path, profile_start = PROFILE_START, profile_end = PROFILE_END):
    profile_info = ""
    start_scanning = False

    with open(path, 'r') as file:
        for line in file:
            if profile_start in line:
                start_scanning = True
                continue
            elif profile_end in line and start_scanning:
                return profile_info

            if start_scanning:
                profile_info += line

    return profile_info

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
    profile_dict = {}

    starting_time = time.time()
    print("Starting at time: %d" % (starting_time))
    print("Number of profiles: %d" % (len(os.listdir(data_path))))

    counter = 0
    previous_time = starting_time

    for username in os.listdir(data_path):
        # Grab profile information and continue if there is none
        profile_info = fetch_profile_info(username, os.path.join(data_path, username, PROFILE))
        if len(profile_info) > 0:
            profile_dict[username] = profile_info

        # Logging info
        counter += 1
        if counter % LOGGING_NUMBER == 0:
            current_time = time.time()
            print("Profiles Searched: %d Time: %d Time from Start: %d Delta Time: %d" % (counter, time.time(), current_time - starting_time, current_time - previous_time))
            sys.stdout.flush()
            previous_time = current_time

    if len(profile_dict) > 0:
        write_profile_info(profile_dict, output_path)

if (__name__ == '__main__'):
    main()
