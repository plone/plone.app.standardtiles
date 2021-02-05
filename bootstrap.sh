# rm -rf ./lib ./include ./local ./bin
# virtualenv --clear .
# ls -al ./bin
[ ! -f bin/pip ] && virtualenv .
# Determine setuptools and buildout versions from annotate using latest buildout
./bin/pip install --upgrade pip setuptools zc.buildout
./bin/buildout $* annotate | tee annotate.txt | grep -E 'setuptools *= *[0-9][^ ]*|zc.buildout *= *[0-9][^ ]*'| sed 's/= /==/' > requirements.txt
cat annotate.txt
cat requirements.txt
# Reset out virtualenv to the versions we need so buildout doesn't have to upgrade
./bin/pip install --upgrade -r requirements.txt
# run buildout
#./bin/buildout $*
