#!/bin/sh
python3.8 -m venv .
./bin/pip install -r requirements.txt
./bin/buildout -c test-5.2.x.cfg
