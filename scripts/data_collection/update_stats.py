import json
import os
import sys

STATS_FILENAME = 'stats.json'

# Update stats files by adding and removing the items in the dictionaries
def update_stats(data_path, add_dict, remove_dict):
    stats_dict = {}
    counter = 0

    for username in os.listdir(data_path):
        # Print to have output
        if counter % 1000 == 0:
            print("Counter: %d" % (counter))
            sys.stdout.flush()

        # Check if file exists
        if not os.path.isfile(os.path.join(data_path, username, STATS_FILENAME)):
            print("No Stats File: %s" % (username))
            sys.stdout.flush()
            continue

        # Open the old stats file
        with open(os.path.join(data_path, username, STATS_FILENAME), 'r') as stats_file:
            stats_dict = json.load(stats_file)

        # Add desired information
        for key in add_dict:
            stats_dict[key] = add_dict[key]

        # Remove unwanted information
        for key in remove_dict:
            if key in stats_dict:
                del stats_dict[key]

        # Write the updated stats file
        with open(os.path.join(data_path, username, STATS_FILENAME), 'w') as stats_file:
            json.dump(stats_dict, stats_file)

        counter += 1

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 1 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <data path>" % (executable), file = sys.stderr)
        sys.exit(1)

    data_path = args.pop(0)

    return data_path

def main():
    data_path = _load_args(sys.argv)

    # What needs to be added and removed
    add_dict = {'has_friends':False, 'has_api_profile':False, 'has_callback_stats':False}
    remove_dict = {'friends'}

    # Update all the stats file in this directory
    update_stats(data_path, add_dict, remove_dict)

if (__name__ == '__main__'):
    main()
