#!/bin/bash
# -*- mode: company ; mode: shell-script  -*-
set -e -u 
echo "Basic regexp test..."
rm -f build/test_report*log
mkdir -p  build
for f in test-suite/*; do
    logfile=build/report_$(basename $f).log
    set +e
    python ./liteplus.py :memory: >& $logfile <$f    || (echo "$f _FAILED_  "  ; cat $logfile)
    if egrep   -C8 'FAILED|OperationalError|BUFFER OVERFLOW ERROR' $logfile >/dev/null; then
        if echo $f | grep exception_ >/dev/null ; then
            echo "[$f] EXCEPTION PASSED"
        else
            echo "[$f]" FAILED
        fi
        #cat $logfile 
        #exit 1000
    else
        if echo $f | grep exception_ >/dev/null ; then
            echo "[$f] EXCEPTION FAILED"
        else
            echo "[$f]" PASSED
        fi
    fi
    set -e
done
