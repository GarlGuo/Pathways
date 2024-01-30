#! /bin/bash

function handle_roster() {
  python3 process_roster_and_generate_files.py --csv --pickle
}

function handle_pathway() {
  python3 process_pathways_and_generate_files.py --csv --pickle
}

function handle_both() {
  handle_roster
  handle_pathway
}

clear
while true; do
  read -p "Enter data file to process. for [r]oster, press [r]. for [p]athways, press [p]. for [b]oth files, press [b]" choice
  case $choice in
  [Rr]*)
    handle_roster
    break
    ;;
  [Pp]*)
    handle_pathway
    break
    ;;
  [Bb]*)
    handle_both
    break
    ;;
  *) echo "please answer r/p/b." ;;
  esac
done
