#!/bin/bash
# -*- mode: company ; mode: shell-script  -*-
set -e -u -x
echo "Basic regexp test"
python ./liteplus.py :memory: <<EOF

SELECT regexp_replace('oracle','(oracle)','sqlite \\1') ;

SELECT 'CHECK REPLACE POSITIONAL USE' ;

SELECT regexp_replace('giorgi','g','z',1,1) ;
SELECT regexp_replace('giorgi','g','z',2,1) ;

SELECT 'Case in-sensitive: expected ziorzi' ;
SELECT regexp_replace('Giorgi','g','z',1,0,'i') ;

SELECT 'Case Sensitive: expeted Giorzi';
SELECT regexp_replace('Giorgi','g','z',1,0,'c') ;

.help
.exit

;
EOF
