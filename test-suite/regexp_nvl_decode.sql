
SELECT assert_equals('sqlite oracle', regexp_replace('oracle sqlite','(\w+) (\w+)','\2 \1')) ;

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

select assert_equals(2,decode('b','a',1,'b',2));
select assert_equals('default',decode('tricked','a',1,'b',2,'default'));

select assert_equals('New Jersey', DECODE (warehouse_id, 1, 'Southlake', 
                             2, 'San Francisco', 
                             3, 'New Jersey', 
                             4, 'Seattle',
                                'Non domestic') )
from (select 3 as warehouse_id );

select assert_equals(NULL,decode(1,999,2)) ;
select assert_equals('default provided',decode(1,999,2,'default provided')) ;
.exit
