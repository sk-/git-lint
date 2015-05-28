sudo apt-get update
sudo apt-get remove rubygems ruby
sudo apt-get install curl build-essential php-pear optipng pngcrush php5 checkstyle libjpeg-turbo-progs xsltproc cmake
#sudo apt-get install nodejs-legacy in ubuntu 14

# Install ruby
curl -sSL https://get.rvm.io | bash -s stable --ruby=1.9.3
source $HOME/.rvm/scripts/rvm

# Install latest node
#curl http://nodejs.org/dist/node-latest.tar.gz | tar xz
#cd node-v*
#./configure
#sudo make install
#cd -
# Install npm
#curl -L https://npmjs.org/install.sh | sh
curl -sL https://deb.nodesource.com/setup | sudo bash -
sudo apt-get install nodejs

gem install rubocop
rubocop --help
gem install ruby-lint
gem install scss-lint

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

# PHP CodeSniffer
sudo pear install PHP_CodeSniffer

# Tidy
git clone https://github.com/htacg/tidy-html5.git
cd build/cmake
cmake ../..
make
sudo make install
cd -

# PMD
wget "http://downloads.sourceforge.net/project/pmd/pmd/5.1.3/pmd-bin-5.1.3.zip?r=&ts=`date +%s`&use_mirror=ufpr"
unzip -q pmd-bin-*
mv pmd-bin-5.1.3 pmd-bin
