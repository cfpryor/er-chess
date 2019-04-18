import json
import os
import re
import sys
import time

#Desired Note Section (Chess.com)
FIDE = "ctrl.stats.officialRating.rating"
NOTES_START = "<div class=\"section-wrapper\">"
NOTES_END = "</div>"
LINK_START = "href=\""

#Cache Variables
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chess_com")
PLAYER_DIR = os.path.join(CACHE_DIR, "https", "api.chess.com", "pub", "player")
PROFILE = 'profile.txt'

def print_truth(truth_dict):
	for user in truth_dict:
		print("\n\n---------------------------\n%s\n---------------------------"%(user))
		for (raw, processed) in truth_dict[user]:
			print("===============\n%s\n---------------\n%s\n===============\n"%(raw.strip(), processed))

def fetch_truth_fide(username, path, notes_start, notes_end, truth_dict):
	start_scanning = False

	with open(path, 'r') as file:
		for line in file:
			if FIDE in line:
				if username not in truth_dict:
					truth_dict[username] = []
				truth_dict[username].append(line)
	return truth_dict

def fetch_truth_media(username, path, notes_start, notes_end, truth_dict):
	start_scanning = False

	with open(path, 'r') as file:
		for line in file:
			if notes_start in line:
				start_scanning = True
			elif notes_end in line and start_scanning:
				start_scanning = False
			elif start_scanning:
				if username not in truth_dict:
					truth_dict[username] = []

				if LINK_START in line:
					#Look for specific link
					link = re.search('href=\"([A-Za-z0-9#,;&?=%@\-:\._/]+)\"', line)
					if link == None:
						continue
					truth_dict[username].append([line, link.group(1)])
				else:
					truth_dict[username].append([line, None])

	return truth_dict

def main():
	unexplored_users = set(os.listdir(PLAYER_DIR))
	truth_dict = {}

	for username in unexplored_users:
		#Skip username if profile does not exist
		path = os.path.join(PLAYER_DIR, username, PROFILE)
		if os.path.isfile(path):
			truth_dict = fetch_truth_media(username, path, NOTES_START, NOTES_END, truth_dict)

	print_truth(truth_dict)
	print(len(truth_dict))

if (__name__ == '__main__'):
	main()
