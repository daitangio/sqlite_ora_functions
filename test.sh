#!/bin/bash
# -*- mode: company ; mode: shell-script  -*-
set -e -u 
set -x
#docker restart dovecot_imap ||  docker run --rm -d --name dovecot_imap -p 143:143 -p 993:993 dovecot/dovecot:2.3.8 
set +x
#docker logs dovecot_imap

echo "Basic regexp test..."



if which python3 ; then
python_exec="python3"
else
python_exec="python"
fi

rm -f build/test_report*log
mkdir -p  build

for f in test-suite/*; do
    logfile=build/report_$(basename $f).log
    set -eu -o pipefail 
    echo -n "[$f]...."
    $python_exec ./liteplus.py :memory: >& $logfile <$f    || (echo "$f _FAILED_  "  ; tail $logfile ; exit 10)    
    set +e     
    if egrep   -C8 'Exception:|FAILED|OperationalError|BUFFER OVERFLOW ERROR' $logfile >/dev/null; then
        if echo $f | grep exception_ >/dev/null ; then
            echo "EXCEPTION PASSED"
        else
            echo "FAILED"
            tail $logfile
            exit 10
        fi
        #cat $logfile 
        #exit 1000
    else
        if echo $f | grep exception_ >/dev/null ; then
            echo "EXCEPTION FAILED"
        else
            echo "PASSED"
        fi
    fi
    set -e
done
echo Success....Generating Documentation
./make-release.sh