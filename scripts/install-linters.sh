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
    sudo apt-get install ruby2.3 ruby-dev --yes
    sudo ln -sf /usr/bin/ruby2.3 /usr/bin/ruby
    sudo ln -sf /usr/bin/gem2.3 /usr/bin/gem
fi

sudo gem install rake rubocop ruby-lint scss_lint

# Install latest node
curl -sL https://deb.nodesource.com/setup_8.x | sudo bash -
sudo apt-get install nodejs --yes

# Install python packages
pip install closure-linter cpplint docutils html-linter pycodestyle pylint yamllint

sudo npm install -g coffeelint csslint jshint

# PHP CodeSniffer
sudo pear install --force PHP_CodeSniffer 

cd /tmp

# Tidy
git clone https://github.com/htacg/tidy-html5.git --depth=1

cd tidy-html5/build/cmake
cmake ../..
make -j 4
sudo make install
cd -

# PMD
wget --no-check-certificate "https://github.com/pmd/pmd/releases/download/pmd_releases%2F6.4.0/pmd-bin-6.4.0.zip"
unzip -q pmd-bin-6.4.0.zip
mv pmd-bin-6.4.0 pmd-bin
