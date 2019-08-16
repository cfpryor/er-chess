import gzip
import json
import os
import re
import shutil
import socket
import sys
import tarfile
import time

# Tar suffix
TAR_SUFFIX = '.tar'

# Common names
GAME_DIRECTORY = 'games'
ARCHIVE_DIRECTORY = 'archives'
DATA_FILE = 'response.data'
SEEN_LIST = 'seen.txt'
COMPLETED_LIST = 'completed.txt'

# Source Filenames
SOURCE_ARCHIVE = os.path.join(GAME_DIRECTORY, ARCHIVE_DIRECTORY, DATA_FILE)
SOURCE_GAMES = DATA_FILE
SOURCE_OPPONENTS = '__opponents.json'
SOURCE_PROFILE = 'profile.txt'

# Outupt Filenames
OUTPUT_ARCHIVE = 'archive.json.gz'
OUTPUT_GAMES = '.json.gz'
OUTPUT_OPPONENTS = 'opponents.json.gz'
OUTPUT_PROFILE = 'profile.html.gz'
OUTPUT_STATS = 'stats.json'


# Gzip json file and move it
def gzip_json(source_path, output_path, remove = False, dict_name = None):
    # Skip if the file does not exist
    if not os.path.isfile(source_path):
        return

    # Read in the source data
    source_data = json.load(open(source_path, 'r'))
    if dict_name != None:
        source_data = source_data[dict_name]

    # Gzip the file
    with gzip.GzipFile(output_path, 'w') as output_file:
        output_file.write(json.dumps(source_data).encode('utf-8')) 

    # Remove file if desired
    if remove:
        os.remove(output_path)

# Gzip file and move it
def gzip_file(source_path, output_path, remove = False):
    # Skip if the file does not exist
    if not os.path.isfile(source_path):
        return

    # Read in the source file
    source_data = open(source_path, 'rb').read()

    # Gzip the file
    with gzip.open(output_path, 'wb') as output_file:
        output_file.write(source_data)

    # Remove file if desired
    if remove:
        os.remove(output_path)

# Convert old directory formatting to new formatting
def update_data(data_path, output_path):
    # Matches to a four digit number (in this case a year)
    year_regex = re.compile('^\d{4}$')
    completed_set = set()
    seen_set = set()
    stats = {}
    count = 0

    print("%d: Starting Compressing Games" % (time.time()))
    sys.stdout.flush()
    for user in os.listdir(data_path):
        source_user_path = os.path.join(data_path, user)
        output_user_path = os.path.join(output_path, user)

        if not os.path.isdir(output_user_path):
            os.mkdir(output_user_path)

        # Create stats file
        stats['time_completed'] = os.stat(source_user_path).st_mtime
        stats['server'] = socket.gethostname()
        stats['friends'] = False

        # Convert archive file
        stats['has_game_archive'] = os.path.isfile(os.path.join(source_user_path, SOURCE_ARCHIVE))
        gzip_json(os.path.join(source_user_path, SOURCE_ARCHIVE), os.path.join(output_user_path, OUTPUT_ARCHIVE), dict_name = 'archives')

        # Convert list of opponents
        stats['has_opponent_list'] = os.path.isfile(os.path.join(source_user_path, SOURCE_OPPONENTS))
        gzip_json(os.path.join(source_user_path, SOURCE_OPPONENTS), os.path.join(output_user_path, OUTPUT_OPPONENTS))

        # Convert HTML profile
        stats['has_profile'] = os.path.isfile(os.path.join(source_user_path, SOURCE_PROFILE))
        gzip_file(os.path.join(source_user_path, SOURCE_PROFILE), os.path.join(output_user_path, OUTPUT_PROFILE))

        # Convert all game files
        stats['has_games'] = False
        if os.path.isdir(os.path.join(source_user_path, GAME_DIRECTORY)):
            for year_directory in os.listdir(os.path.join(source_user_path, GAME_DIRECTORY)):
                if year_regex.search(year_directory) != None:
                    for month_directory in os.listdir(os.path.join(source_user_path, GAME_DIRECTORY, year_directory)):
                        game_file = os.path.join(os.path.join(source_user_path, GAME_DIRECTORY, year_directory, month_directory, SOURCE_GAMES))
                        if not os.path.isfile(game_file):
                            continue

                        gzip_json(game_file, os.path.join(output_user_path, year_directory + "_" +  month_directory + OUTPUT_GAMES))
                        stats['has_games'] = True

        # Write the stats file
        with open(os.path.join(output_user_path, OUTPUT_STATS), 'w') as output_file:
            json.dump(stats, output_file)

        # Tar up all files except for stats file
        with tarfile.open(os.path.join(output_user_path, user + TAR_SUFFIX), 'w') as tar:
            for filename in os.listdir(output_user_path):
                if filename != OUTPUT_STATS and filename != user + TAR_SUFFIX:
                    tar.add(os.path.join(output_user_path, filename), arcname = filename)
                    os.remove(os.path.join(output_user_path, filename))

        
        # Update seen and completed lists
        if os.path.isfile(os.path.join(source_user_path, SOURCE_OPPONENTS)):
            with open(os.path.join(source_user_path, SOURCE_OPPONENTS), 'r') as opponent_file:
                seen_set.update(json.load(opponent_file))
        completed_set.add(user)

        # Remove old directory
        shutil.rmtree(source_user_path)

        # Print for output
        if count % 10 == 0:
            print("%d: Count - %d User - %s" % (time.time(), count, user))
            sys.stdout.flush()
        count += 1
    print("%d: Finished Compressing Games" % (time.time()))
    sys.stdout.flush()

    print("%d: Starting Writing Seen List" % (time.time()))
    sys.stdout.flush()
    # Load any seen list already created
    if os.path.isfile(os.path.join(output_path, SEEN_LIST)):
        with open(os.path.join(output_path, SEEN_LIST), 'r') as seen_file:
            for line in seen_file:
                if line.strip() != "":
                    seen_set.add(line.strip())
    
    # Write seen list
    with open(os.path.join(output_path, SEEN_LIST), 'w') as seen_file:
        seen_file.write('\n'.join(list(seen_set)) + '\n')
    print("%d: Finished Writing Seen List" % (time.time()))
    sys.stdout.flush()
    
    print("%d: Starting Writing Completed List" % (time.time()))
    sys.stdout.flush()
    # Load any completed list already created
    if os.path.isfile(os.path.join(output_path, COMPLETED_LIST)):
        with open(os.path.join(output_path, COMPLETED_LIST), 'r') as completed_file:
            for line in completed_file:
                if line.strip() != "":
                    completed_set.add(line.strip())

    # Write completed list
    with open(os.path.join(output_path, COMPLETED_LIST), 'w') as completed_file:
        completed_file.write('\n'.join(list(completed_set)) + '\n')
    print("%d: Finished Writing Completed List" % (time.time()))
    sys.stdout.flush()

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 2 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <data path> <output path>" % (executable), file = sys.stderr)
        sys.exit(1)

    data_path = args.pop(0)
    output_path = args.pop(0)

    return (data_path, output_path)

def main():
    data_path, output_path = _load_args(sys.argv)
    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    update_data(data_path, output_path)

if (__name__ == '__main__'):
    main()
