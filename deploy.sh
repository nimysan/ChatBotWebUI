#!/bin/bash

#git clone https://github.com/nimysan/ChatBotWebUI.git

pip install -r requirements.txt
cp config-example.json config.json
nohup python3 webui.py &
