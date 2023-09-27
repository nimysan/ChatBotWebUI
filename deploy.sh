#!/bin/bash

cp config-example.json config.json
pip install -r requirements.txt
python3 webui.py
