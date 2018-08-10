.print Test Suite TO_DATE
select assert_equals('1900-01-01 00:00:00',to_date('January','%B'));

-- SELECT assert_equals('15-JAN-89',TO_DATE('January 15, 1989, 11:00 A.M.','Month dd, YYYY, HH:MI A.M.','NLS_DATE_LANGUAGE = American'));

.exit
