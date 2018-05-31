set -x
set -e

root="$(git rev-parse --show-toplevel)"
${root}/scripts/clean-linters.sh

sudo apt-get update -qq
sudo apt-get remove rubygems ruby --yes
sudo apt-get install curl build-essential php-pear optipng pngcrush checkstyle libjpeg-turbo-progs xsltproc cmake --yes

# Ubuntu 14
if lsb_release -c | grep -q trusty
then
    # Install ruby
    sudo apt-add-repository --yes ppa:brightbox/ruby-ng
    sudo apt-get update
    sudo apt-get install ruby2.2 ruby2.2-dev --yes
    sudo ln -sf /usr/bin/ruby2.2 /usr/bin/ruby
    sudo ln -sf /usr/bin/gem2.2 /usr/bin/gem
    sudo apt-get install nodejs-legacy php5 --yes

    sudo update-alternatives --remove ruby /usr/bin/ruby2.2
    sudo update-alternatives --remove irb /usr/bin/irb2.2
    sudo update-alternatives --remove gem /usr/bin/gem2.2

    sudo update-alternatives \
        --install /usr/bin/ruby ruby /usr/bin/ruby2.2 50 \
        --slave /usr/bin/irb irb /usr/bin/irb2.2 \
        --slave /usr/bin/rake rake /usr/bin/rake2.2 \
        --slave /usr/bin/gem gem /usr/bin/gem2.2 \
        --slave /usr/bin/rdoc rdoc /usr/bin/rdoc2.2 \
        --slave /usr/bin/testrb testrb /usr/bin/testrb2.2 \
        --slave /usr/bin/erb erb /usr/bin/erb2.2 \
        --slave /usr/bin/ri ri /usr/bin/ri2.2

    update-alternatives --config ruby
    update-alternatives --display ruby
fi

# Ubuntu 16
if lsb_release -c | grep -q xenial
then
    # Install ruby
    sudo apt-get install ruby2.3 --yes
    sudo ln -sf /usr/bin/ruby2.3 /usr/bin/ruby
    sudo ln -sf /usr/bin/gem2.3 /usr/bin/gem
fi

sudo gem install rake
sudo gem install rubocop
sudo gem install ruby-lint
sudo gem install scss_lint

# Install latest node
curl -sL https://deb.nodesource.com/setup_4.x | sudo bash -
sudo apt-get install nodejs --yes

# Install python packages
pip install closure-linter
pip install pylint
pip install pycodestyle
pip install yamllint
pip install docutils
pip install html-linter
pip install cpplint

# See https://github.com/n1k0/casperjs/issues/876
sudo npm config set registry http://registry.npmjs.org/
sudo npm install -g csslint
sudo npm install -g jshint
sudo npm install -g coffeelint

# PHP CodeSniffer
sudo pear install --force PHP_CodeSniffer 

cd /tmp

# Tidy
git clone https://github.com/htacg/tidy-html5.git
cd tidy-html5/build/cmake
cmake ../..
make
sudo make install
cd -

# PMD
wget --no-check-certificate "http://downloads.sourceforge.net/project/pmd/pmd/5.1.3/pmd-bin-5.1.3.zip?r=&ts=`date +%s`&use_mirror=ufpr"
unzip -q pmd-bin-*
mv pmd-bin-5.1.3 pmd-bin
