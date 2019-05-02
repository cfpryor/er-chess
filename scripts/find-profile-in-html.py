import json
import os
import re
import sys
import time

# Desired Profile Section (Chess.com)

DESIRED_SECTIONS = {"<div class=\"section-wrapper\">": ["</div>", False],
                    "<p class=\"bio\">": ["</p>", False],
                    "<div class=\"social_links col2\">": ["</div>", False]}

# Profile Name
PROFILE = 'profile.txt'

# Logging Constants
LOGGING_NUMBER = 5000

def write_profile_info(profile_dict, path):
    with open(path, 'w') as file:
       json.dump(profile_dict, file, indent = 4)

def fetch_profile_info(username, path, desired_sections = DESIRED_SECTIONS):
    profile_info = ""

    with open(path, 'r') as file:
        for line in file:
            for section_start in desired_sections:
                if section_start in line:
                    desired_sections[section_start][1] = True
                    continue
                elif desired_sections[section_start][0] in line and desired_sections[section_start][1]: 
                    desired_sections[section_start][1] = False

                if desired_sections[section_start][1] == True and line != "":
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
