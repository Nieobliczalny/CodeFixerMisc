#!/bin/bash
source ~/codechecker/venv/bin/activate
echo Preparing...
cd testdata
make clean 2&> /dev/null
git checkout master > /dev/null
rm -rf ~/.codechecker 2&> /dev/null
rm -rf /tmp/cctmp 2&> /dev/null
CodeChecker server > /dev/null &
CC_PID=$!
cd ../code
rm -f config.ini
ln -s configTest.ini config.ini
sleep 10s
echo Executing unit tests
python3 -m unittest discover -s ./ -p 'test*.py'
echo Unit tests finished
kill -15 $CC_PID
CodeChecker server -w /tmp/cctmp > /dev/null &
CC_PID=$!
rm -f config.ini
ln -s configTrainTest.ini config.ini
sleep 10s
echo Executing script tests - Clean case
python3 intTestBuildTrainDbClean.py
echo Script tests finished
kill -15 $CC_PID
CodeChecker server -w /tmp/cctmp > /dev/null &
CC_PID=$!
rm -f config.ini
ln -s configTrainTest.ini config.ini
sleep 10s
echo Executing script tests - Incremental case
python3 intTestBuildTrainDbIncremental.py
echo Script tests finished
kill -15 $CC_PID
cd ../