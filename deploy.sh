#!/bin/bash

if [ ! -f config.json ]
then
	cp config-example.json config.json
fi

python3 -m venv /home/ec2-user/botenv
app_env_home=/home/ec2-user/botenv

${app_env_home}/bin/python3 -m pip install --upgrade pip
${app_env_home}/bin/pip install -r requirements.txt --debug --log pip.log
nohup ${app_env_home}/bin/python3 -u webui.py > webui.log 2>&1 &
