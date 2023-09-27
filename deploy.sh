#!/bin/bash

if [ ! -f config.json ]
then
	cp config-example.json config.json
fi
pip install -r requirements.txt --debug --log pip.log
nohup python3 -u webui.py > webui.log 2>&1
