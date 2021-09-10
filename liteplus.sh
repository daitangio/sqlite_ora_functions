#!/bin/bash
set -euo pipefail
temp_file=$$.tmp
db=$1
./liteplus_filter.py $db  $2 >$temp_file
sqlite3 $db < $temp_file && rm $temp_file