#!/bin/bash
FILENAME=$1;
origsize=`stat -c%s $FILENAME`;
newsize=`jpegtran -copy none -optimize -perfect $FILENAME | wc -c`;

if [ $newsize -gt 0 ] && [ $newsize -lt $origsize ]; then
    reduction=`bc <<< "scale = 2; (100*($origsize - $newsize) / $origsize)"`;
    echo "The file size can be losslessly reduced from $origsize to $newsize bytes. ($reduction % filesize reduction)";
    echo "Use: jpegtran -copy none -optimize -perfect -outfile <outfile> $FILENAME";
    exit 1;
fi
