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

ARGV=("$@");
ARGC=$((${#ARGV[@]}-1));
FILENAME=${ARGV[$ARGC]};
unset ARGV[$ARGC];

remove_template.py $FILENAME |
tidy ${ARGV[@]} 2>&1 |
egrep -v "Warning: (.* proprietary attribute \"(itemtype|itemid|itemscope|itemprop)\"|missing <!DOCTYPE> declaration|inserting implicit <body>|inserting missing 'title' element)$" |
uniq
