#!/bin/bash
# -*- mode: company ; mode: shell-script  -*-
set -e -u 
echo "Basic regexp test..."
rm -f build/test_report*log
mkdir -p  build
for f in test-suite/*; do
    logfile=build/test_report_$(basename $f).log
    python ./liteplus.py :memory: >& $logfile <$f
    #python ./liteplus.py :memory:  <$f
    if egrep   -C8 'FAILED|OperationalError' $logfile >/dev/null; then
        echo "[$f]" FAILED
        cat $logfile 
        #exit 1000
    else
        echo "[$f]" PASSED
    fi
done
