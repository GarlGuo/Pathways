# This will navigate to the ~/data/db folder on your machine and
# DELETE all data in the diagnostic.data folders and journal folders
# and DELETE all database data in ~/data/db

# Only run this is you are sure that you want to kill the database
# AND you havent saved any data in it that you want to keep

# Usage: ./clear_mongo.sh

# If you get permission denied, do:
# chmod u+x clear_mongo.sh

cd ~/data/db
rm -r diagnostic.data journal
rm -f *
