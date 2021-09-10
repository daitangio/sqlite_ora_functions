#!/bin/bash
# -*- mode: company ; mode: shell-script  -*-
set -e -u 
set -x
#docker restart dovecot_imap ||  docker run --rm -d --name dovecot_imap -p 143:143 -p 993:993 dovecot/dovecot:2.3.8 
set +x

#docker logs dovecot_imap

echo "Basic regexp test..."

if [ "$OS" == "Windows_NT" ] ; then
python_exec="python"
else
python_exec="python3"
fi
rm -f build/test_report*log
mkdir -p  build

for f in test-suite/*; do
    logfile=build/report_$(basename $f).log
    set +e
    $python_exec ./liteplus.py :memory: >& $logfile <$f    || (echo "$f _FAILED_  "  ; cat $logfile)
    if egrep   -C8 'FAILED|OperationalError|BUFFER OVERFLOW ERROR' $logfile >/dev/null; then
        if echo $f | grep exception_ >/dev/null ; then
            echo "[$f] EXCEPTION PASSED"
        else
            echo "[$f]" FAILED
            tail $logfile
            exit 1000
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
echo Success....Generating Documentation
./make-release.sh