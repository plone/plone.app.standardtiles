#!/bin/sh

# bootstrap using pip
rm -r ./lib ./include ./local ./bin
virtualenv --clear .
./bin/pip install -U pip
./bin/pip install -r requirements.txt
./bin/buildout $*
