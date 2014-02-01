#!/bin/bash
# Copyright 2013-2014 Sebastian Kreft
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
