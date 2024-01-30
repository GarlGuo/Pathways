#! /bin/bash

cd dependencies
if [[ ! -d redis-data ]]; then
  mkdir redis-data
  cd redis-data 
  touch redis.log
  cd -
fi
redis-server redis-server.linux.conf &
