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
function get_size {
    LS_OUTPUT=($(ls -n $1));
    echo ${LS_OUTPUT[4]};
}

FILENAME=$1;
BASENAME=`basename $FILENAME`;
origsize=$(get_size $FILENAME);
output=`pngcrush -d /tmp/git-lint -rem alla -reduce -brute $FILENAME 2>&1 | grep -i "not a png file"`;
if [ "$output" != "" ]; then
    echo 'Not a PNG file';
    exit 1;
fi
newsize=$(get_size /tmp/git-lint/$BASENAME);

if [ "$newsize" != "" ] && [ $newsize -gt 0 ] && [ $newsize -lt $origsize ]; then
    reduction=`bc <<< "scale = 2; (100*($origsize - $newsize) / $origsize)"`;
    echo "The file size can be losslessly reduced from $origsize to $newsize bytes. ($reduction% filesize reduction)";
    echo "Use: pngcrush -rem alla -reduce -brute $FILENAME <new_filename>";
    exit 1;
fi
