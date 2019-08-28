
select help("help") from dual;

select assert_equals('Provide support for docstring documentation PEP-257',help("help")) from dual;

.exit