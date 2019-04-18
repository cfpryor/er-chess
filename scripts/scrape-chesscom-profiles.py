import json
import os
import sys
import time
import urllib.request

from urllib.request import Request, urlopen

#Constants
SLEEP_TIME_MS = 500

#Website Variables
URL_BASE = 'https://www.chess.com/member/'

#Cache Variables
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chess_com")
PLAYER_DIR = os.path.join(CACHE_DIR, "https", "api.chess.com", "pub", "player")
PROFILE = 'profile.txt'

#Global variables
last_fetch = 0

def fetch_profile(username):
	global last_fetch

	profile_path = os.path.join(PLAYER_DIR, username, PROFILE)
	if not os.path.isfile(profile_path):
		#Sleep 0.5 second each call
		now = int(time.time() * 1000)
		sleep_time_sec = (SLEEP_TIME_MS - (now - last_fetch)) / 1000.0
		if (sleep_time_sec > 0):
			time.sleep(sleep_time_sec)

		url = os.path.join(URL_BASE, username)
		req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

		try:
			response = urlopen(req)
		except:
			print("User Error: %s" % (username))
			return

		data = response.read().decode('utf-8')
		with open(profile_path, 'w') as file:
			file.write(data)

		last_fetch = int(time.time() * 1000)

def main():
	unexplored_users = set(os.listdir(PLAYER_DIR))
	print(len(unexplored_users))
	sys.stdout.flush()

	counter = 0
	for username in unexplored_users:
		fetch_profile(username)
		if counter % 100 == 0:
			print(counter)
			sys.stdout.flush()
		counter += 1

if (__name__ == '__main__'):
	main()
