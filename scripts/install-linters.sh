sudo apt-getg remove rubygems
sudo apt-get install curl build-essential optipng pngcrush php5 php-codesniffer ruby1.9.3 checkstyle libjpeg-turbo-progs xsltproc
#sudo apt-get install nodejs-legacy in ubuntu 14

# Install latest node
curl http://nodejs.org/dist/node-latest.tar.gz | tar xz
cd node-v*
./configure
sudo make install
cd -

# Install npm
curl -L https://npmjs.org/install.sh | sh

sudo gem install rubocop
sudo gem install ruby-lint
sudo gem install scss-lint
pip install http://closure-linter.googlecode.com/files/closure_linter-latest.tar.gz
pip install pylint
pip install pep8
pip install pyYAML
pip install docutils
pip install html-linter

# See https://github.com/n1k0/casperjs/issues/876
sudo npm config set registry http://registry.npmjs.org/
sudo npm install -g csslint
sudo npm install -g jshint

# Tidy
git clone https://github.com/w3c/tidy-html5.git
cd tidy-html5
make -C build/gmake/
sudo make install -C build/gmake/
cd -

# PMD
wget "http://downloads.sourceforge.net/project/pmd/pmd/5.1.3/pmd-bin-5.1.3.zip?r=&ts=`date +%s`&use_mirror=ufpr"
unzip pmd-bin-*
mv pmd-bin-5.1.3 pmd-bin
