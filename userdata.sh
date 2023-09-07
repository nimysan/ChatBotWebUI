#!/bin/bash

sudo dnf install git postgresql15 pip docker -y
echo install ok
sudo usermod -aG docker $USER

echo usermod
#newgrp docker a 这句代码导致后面脚本无法执行
#echo newgr

sudo systemctl start docker &

# 等待服务启动完成
while ! systemctl is-active docker; do
    sleep 1
done
echo "hhhhh"

# start pgAdmin4
docker run -d -p 62315:80 \
    -e "PGADMIN_DEFAULT_EMAIL=sample@sample.com" \
    -e "PGADMIN_DEFAULT_PASSWORD=SampleAdmin" \
    -d dpage/pgadmin4

#deploy ChatBotWebUI
git clone https://github.com/nimysan/ChatBotWebUI.git
cd  ChatBotWebUI

#初始化配置
cat << EOF > config.json
{
  "pg_config": [
    "chatbot-postgres-serverless-v2.cluster-c3iilnukj9yy.us-east-1.rds.amazonaws.com",
    "5432",
    "knowledge",
    "postgres",
    "Lxd%*1234"
  ],
  "openai_key": "sk-testxxxxx"
}
EOF

chmod a+x ./deploy.sh
./deploy.sh