sudo apt-get install optipng pngcrush jpegtran php5 php-codesniffer ruby checkstyle nodejs nodejs-legacy npm libjpeg-turbo-progs xsltproc
sudo gem install rubocop
sudo gem install ruby-lint
sudo gem install scss-lint
pip install http://closure-linter.googlecode.com/files/closure_linter-latest.tar.gz
pip install pylint
pip install pep8
pip install pyYAML
pip install docutils
pip install html-linter
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
