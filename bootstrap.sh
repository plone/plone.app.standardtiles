rm -r ./lib ./include ./local ./bin
virtualenv --clear .
bin/pip install --upgrade pip setuptools zc.buildout
bin/buildout $* annotate | tee annotate.txt | grep -E 'setuptools *= *[0-9][^ ]*|zc.buildout *= *[0-9][^ ]*'| sed 's/= /==/' > requirements.txt
cat annotate.txt
cat requirements.txt
bin/pip install --upgrade -r requirements.txt
bin/buildout $*