#!/bin/bash

if [ ! -f config.json ]; then
  cp config-example.json config.json
fi

mkdir -p /home/ec2-user/tmp
export TMPDIR=/home/ec2-user/tmp #防止pip install no-space-left error"
python3 -m venv /home/ec2-user/botenv
app_env_home=/home/ec2-user/botenv

${app_env_home}/bin/python3 -m pip install --upgrade pip
${app_env_home}/bin/pip install --verbose  -r requirements.txt --log pip.log
nohup ${app_env_home}/bin/python3 -u webui.py >webui.log 2>&1 &
nohup ${app_env_home}/bin/python3 -u manager.py >manager.log 2>&1 &
