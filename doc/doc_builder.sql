.print Auto generated documentation via python doc strings

WITH RECURSIVE
  cnt(x) AS (
     SELECT 1
     UNION ALL
     SELECT x+1 FROM cnt
      LIMIT (lite_plus_functions()-1)
  )
SELECT 
'FUNCTION:'|| func_name  ||
(CASE help(func_name)
 WHEN 'None' THEN '!UNDOCUMENTED!'
 ELSE
'
=======================================
' ||help(func_name)  || '
'
END ) as autodoc
from (
SELECT distinct lite_plus(x) as func_name FROM cnt order by 1);


.exit
