#!/bin/bash
trap exit SIGINT

# Cache Variables
readonly SCRIPTS_DIR=$(dirname "$0")
readonly PROFILE_DIR="${SCRIPTS_DIR}/../data/chess_com/https/api.chess.com/pub/player/"
readonly RESULTS_DIR="${SCRIPTS_DIR}/../results"

# Lines to print
readonly EXPLORED="Explored"
readonly DELETED="Deleting User"

# Prefix and Suffix for files
readonly OUT_FILE_SUFFIX='.txt'

# Main
function main() {
  trap exit SIGINT

  # Print number of profiles
  echo $(ls ${PROFILE_DIR} | wc)

  # Print number of explored and deleted users in most current run
  local current_log=$(ls -t ${RESULTS_DIR}/*${OUT_FILE_SUFFIX} | head -1)

  grep "${EXPLORED}" ${current_log} | tail -1
  grep -c "${DELETED}" ${current_log}
}

main "$@"
