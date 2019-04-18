#!/bin/bash

# Directory and files relative locations
readonly SCRIPTS_DIR=$(dirname "$0")
readonly SCRAPE_PATH="${SCRIPTS_DIR}/scrape-chesscom.py"
readonly RESULTS_DIR="${SCRIPTS_DIR}/../results"

# Prefix and Suffix for files
readonly LOG_FILES_PREFIX='out_'
readonly OUT_FILE_SUFFIX='.txt'
readonly ERR_FILE_SUFFIX='.err'

# Main
function main() {
	trap exit SIGINT
	start_scrape
}

function start_scrape() {
	mkdir -p ${RESULTS_DIR}

	while :
	do
		out_filename="${LOG_FILES_PREFIX}$(date +%s)"

		time python3 ${SCRAPE_PATH} > "${RESULTS_DIR}/${out_filename}${OUT_FILE_SUFFIX}" 2> "${RESULTS_DIR}/${out_filename}${ERR_FILE_SUFFIX}"
		sleep 60
	done
}

main "$@"
