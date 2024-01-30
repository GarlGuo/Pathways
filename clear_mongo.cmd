# Only run this is you are sure that you want to kill the database
# AND you havent saved any data in it that you want to keep

# run this file as administrator, otherwise you cannot stop MongoDB services in Windows

rem stop service to avoid conflicts
net stop MongoDB

rmdir /s /q %CD%\db

rem restart service
net start MongoDB