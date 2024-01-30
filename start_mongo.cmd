# before run this script, go to the Services in Windows and ensure the service of MongoDB Server is RUNNING for ALL TASKS.
# run this script in *** administrator mode ***

if not exist %CD%\db\data ( 
	mkdir %CD%\db\data
) 

if not exist %CD%\db\log ( 
	mkdir %CD%\db\log
) 

mongod --port 27017 --dbpath %CD%\db\data --logpath %CD%\db\log\mongodb.log --logappend --install
