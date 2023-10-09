#!/bin/bash

if [ ! -f config.json ]; then
  cp config-example.json config.json
fi

mkdir -p /home/ec2-user/tmp
export TMPDIR=/home/ec2-user/tmp #防止pip install no-space-left error"

TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
#curl http://169.254.169.254/latest/meta-data/profile -H "X-aws-ec2-metadata-token: $TOKEN"
region=`curl --silent http://169.254.169.254/latest/dynamic/instance-identity/document -H "X-aws-ec2-metadata-token: $TOKEN"| jq -r .region`

export AWS_DEFAULT_REGION=$region
python3 -m venv /home/ec2-user/botenv
app_env_home=/home/ec2-user/botenv

${app_env_home}/bin/python3 -m pip install --upgrade pip
${app_env_home}/bin/pip install --verbose  -r requirements.txt --log pip.log

pids=$(ps aux | grep botenv | grep -v "grep" | awk '{print $2}')
for pid in $pids; do
    kill -0 $pid  2>/dev/null
    if [ $? -eq 0 ]; then
        kill $pid   # 进程存在,可以杀掉
    fi
done

export BOT_UNDER_PROXY=Yes
nohup ${app_env_home}/bin/python3 -u webui.py >webui.log 2>&1 &
nohup ${app_env_home}/bin/python3 -u manager.py >manager.log 2>&1 &
