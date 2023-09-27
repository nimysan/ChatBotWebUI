#!/bin/bash

if [ ! -f config.json ]
then
	cp config-example.json config.json
fi
echo "-----------------------"
export PATH=/home/ec2-user/.local/bin:/home/ec2-user/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin
echo $PATH
env
echo "-----------------------"
pip install -r requirements.txt --debug --log pip.log
nohup python3 -u webui.py > webui.log 2>&1 &
