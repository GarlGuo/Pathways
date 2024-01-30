# Insert you own home directory/data/db here - NOT /data/db, which is root directory
# make sure that you have ~/data/db on your computer.

# Run this in a tmux widow or a separate shell - this will run the database
# from the shell that its launched in

# Usage: ./start_mongo.sh

# If you get permission denied, do:
# chmod u+x start_mongo.sh

mongod --port 27017 --dbpath ~/data/db
