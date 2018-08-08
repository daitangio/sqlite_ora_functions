#!/bin/bash
# -*- mode: company ; mode: shell-script  -*-
set -e -u 
echo "Basic regexp test..."
python ./liteplus.py :memory: >test_report.log <<EOF

SELECT assert_equals('sqlite oracle', regexp_replace('oracle sqlite','(\w+) (\w+)','\\2 \\1')) ;

-- CHECK REPLACE POSITIONAL USE

SELECT assert_equals('ziorgi',regexp_replace('giorgi','g','z',1,1)) ;

SELECT assert_equals('giorzi',regexp_replace('giorgi','g','z',2,1)) ;

-- 'Case in-sensitive: expected ziorzi' 
SELECT assert_equals('ziorzi',regexp_replace('Giorgi','g','z',1,0,'i') );

-- 'Case Sensitive: expected Giorzi';
select assert_equals('Giorzi',regexp_replace('Giorgi','g','z',1,0,'c') ) ;

select assert_equals(1,C) from ( 
       Select count(*) as C from (SELECT 'Giorgi' AS S ) where regexp_like(S,'giorgi','i')
);

select assert_equals(0,C) from ( 
       Select count(*) as C from (SELECT 'Giorgi' AS S ) where regexp_like(S,'giorgi','c')
);

select assert_equals(1,nvl(NULL,1),'NVL NULL');
select assert_equals(2,nvl(2,1),'NVL NOT NULL');

select assert_equals('yeppa',nvl2('notnull','yeppa','failed')); 
select assert_equals('yeppa',nvl2(NULL,'failed','yeppa')); 


-- .help
SELECT 'TEST ENDS NOW';
.exit

;
EOF

if grep -i  failed test_report.log ; then
    echo AT LEAST ONE TEST FAILED
    exit 1000
else
    echo Test PASSED 
fi
