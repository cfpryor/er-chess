import json
import os

# Pathing information
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chess_com")
PLAYER_DIR = os.path.join(CACHE_DIR, "https", "api.chess.com", "pub", "player")

# User filenames
CACHE_USER_OPPONENTS = '__opponents.json'
CHESS_COM_USER_PATH = os.path.join(CACHE_DIR, '__users.json')

def dump_users(user_set):
    with open(CHESS_COM_USER_PATH, 'w') as file:
        json.dump(list(user_set), file, indent=4)

def load_opponents(username):
    opponent_path = os.path.join(PLAYER_DIR, username, CACHE_USER_OPPONENTS)
    if not os.path.isfile(opponent_path):
        return set()

    with open(opponent_path, 'r') as file:
        opponent_list = json.load(file)

    return set(opponent_list)

def main():
    # Set of all users
    user_set = set()
    
    # Grab all the opponents and store in set.
    for user in os.listdir(PLAYER_DIR):
        opponent_set = load_opponents(user)
        user_set |= opponent_set

    # Dump out all the users gathered.
    dump_users(user_set)

if (__name__ == '__main__'):
    main()
