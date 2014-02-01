#!/bin/bash
FILENAME=$1;
OUTFILE='/tmp/git-lint/optipng.png';
origsize=`stat -c%s $FILENAME`;
rm $OUTFILE 2> /dev/null;
optipng -out $OUTFILE -o9 $FILENAME > /dev/null;
newsize=`stat -c%s $OUTFILE`;

if [ $newsize -gt 0 ] && [ $newsize -lt $origsize ]; then
    reduction=`bc <<< "scale = 2; (100*($origsize - $newsize) / $origsize)"`;
    echo "The file size can be losslessly reduced from $origsize to $newsize bytes. ($reduction % filesize reduction)";
    echo "Use: optipng -o9 $FILENAME";
    exit 1;
fi
