#!/bin/sh

# bootstrap using pip
rm -r ./lib ./include ./local ./bin
virtualenv --clear .
./bin/pip install -U pip
./bin/pip install -r https://github.com/plone/buildout.coredev/raw/5.1/requirements.txt
./bin/buildout $*
