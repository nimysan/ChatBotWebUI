#!/bin/bash

if [ ! -f config.json ]
then
	cp config-example.json config.json
fi
echo "-----------------------"
echo $PATH
env
echo "-----------------------"
pip install -r requirements.txt --debug --log pip.log
nohup python3 -u webui.py > webui.log 2>&1 &
