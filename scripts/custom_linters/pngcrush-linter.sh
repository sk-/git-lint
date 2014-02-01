#!/bin/bash
FILENAME=$1;
BASENAME=`basename $FILENAME`;
origsize=`stat -c%s $FILENAME`;
pngcrush -d /tmp/git-lint -rem alla -reduce -brute $FILENAME > /dev/null;
newsize=`stat -c%s /tmp/git-lint/$BASENAME`;

if [ $newsize -gt 0 ] && [ $newsize -lt $origsize ]; then
    reduction=`bc <<< "scale = 2; (100*($origsize - $newsize) / $origsize)"`;
    echo "The file size can be losslessly reduced from $origsize to $newsize bytes. ($reduction % filesize reduction)";
    echo "Use: pngcrush -rem alla -reduce -brute $FILENAME <new_filename>";
    exit 1;
fi
