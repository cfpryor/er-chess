import gzip
import json
import os
import sys
import tarfile

# Files
SEEN_LIST = 'seen.txt'
COMPLETED_LIST = 'completed.txt'
OPPONENT_LIST = 'opponents.json.gz'

# Update the seen and complete lists
def update_lists(data_path):
    counter = 0
    opponent_set = set()
    user_set = set()

    for username in os.listdir(data_path):
        # Add user to completed list
        user_set.add(username)

        # Print to have output
        if counter % 1000 == 0:
            print("Counter: %d" % (counter))
            sys.stdout.flush()

        # Check if file exists
        if not os.path.isfile(os.path.join(data_path, username, username + '.tar')):
            print("No Stats File: %s" % (username))
            sys.stdout.flush()
            continue

        # Load the gziped opponents file inside the tar
        curr_opponents = []
        with tarfile.open(os.path.join(data_path, username, username + '.tar'), 'r:') as tar_file:
            # Make sure the opponet file exists
            if OPPONENT_LIST not in tar_file.getnames():
                print("User has no opponent file: %s" % (username))
                sys.stdout.flush()
                continue
            curr_opponents = json.loads(gzip.decompress(tar_file.extractfile(OPPONENT_LIST).read()).decode('utf-8'))

        # Add opponents to seen list
        opponent_set |= set(curr_opponents)
        counter += 1

    # Write seen list
    with open(os.path.join(data_path, SEEN_LIST), 'w') as seen_file:
        seen_file.write('\n'.join(list(opponent_set)) + '\n')
    print("Finished Seen List: Size %d" % len(opponent_set))

    # Write completed list
    with open(os.path.join(data_path, COMPLETED_LIST), 'w') as completed_file:
        completed_file.write('\n'.join(list(user_set)) + '\n')
    print("Finished Completed List: Size %d" % len(user_set))

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 1 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <data path>" % (executable), file = sys.stderr)
        sys.exit(1)

    data_path = args.pop(0)

    return data_path

def main():
    data_path = _load_args(sys.argv)

    # Update all the stats file in this directory
    update_lists(data_path)

if (__name__ == '__main__'):
    main()
