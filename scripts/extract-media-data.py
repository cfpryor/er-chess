import json
import os
import re
import sys
import time

TRUTH_NAME = [  'Email', 'Twitch', 'Facebook_Link', 'Twitter_Link', 'Twitter_Handle',
                'Instagram_Link', 'Github_Link', 'Linkedin_Link', 'Googleplus_Link',
                'Discord_Link', 'Myspace_Link', 'Lichess_Link', 'Youtube_Channel',
                'FIDE_Link', 'USCF_Link', 'ChessCom_Link']
TRUTH_REGEX = [ '[\w\.-]+@[\w\.-]+',
                'twitch.tv/[\S]+',
                'facebook.com/[\S]+',
                'twitter.com/[\S]+',
                '(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9-_]+)',
                'instagram.com/[\S]+',
                'github.com/[\S]+',
                'linkedin.com/[\S]+',
                'plus.google.com/[\S]+',
                'discord.gg[\S]+',
                'myspace.com/[\S]+',
                'lichess.org/[\S]+',
                'youtube.com/channel/[\S]+',
                'ratings.fide.com/[\S]+',
                'uschess.org/[\S]+',
                'chess.com/member/[\S]+']

def write_truth(truth_data, path):
    with open(path, 'w') as file:
        json.dump(truth_data, file, indent = 4)

def extract_truth_data(data_dict, truth_regex = TRUTH_REGEX, truth_name = TRUTH_NAME):
    truth_data_dict = {}

    for key in data_dict:
        for index in range(len(truth_regex)):
            match = re.search(r'' + truth_regex[index], data_dict[key])
            if (match != None):
                if key not in truth_data_dict:
                    truth_data_dict[key] = [None] * len(truth_name)
                truth_data_dict[key][index] = match.group(0)

    print(len(truth_data_dict))
    return truth_data_dict

def load_data(path):
    with open(path, 'r') as file:
        return json.load(file)

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 2 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <data path> <out_path>" % (executable), file = sys.stderr)
        sys.exit(1)

    data_path = args.pop(0)
    out_path = args.pop(0)

    return data_path, out_path

def main():
    data_path, out_path = _load_args(sys.argv)

    data_dict = load_data(data_path)
    truth_data = extract_truth_data(data_dict)
    write_truth(truth_data, out_path)

if (__name__ == '__main__'):
    main()
