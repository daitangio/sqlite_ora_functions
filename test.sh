#!/bin/bash
# -*- mode: company ; mode: shell-script  -*-
set -e -u 
echo "Basic regexp test..."
rm -f build/test_report*log
mkdir -p  build
for f in test-suite/*; do
    logfile=build/test_report_$(basename $f).log
    set +e
    python ./liteplus.py :memory: >& $logfile <$f    || (echo "$f _FAILED_  "  ; cat $logfile)
    if egrep   -C8 'FAILED|OperationalError|BUFFER OVERFLOW ERROR' $logfile >/dev/null; then
        echo "[$f]" FAILED
        cat $logfile 
        #exit 1000
    else
        echo "[$f]" PASSED
    fi
    set -e
done
