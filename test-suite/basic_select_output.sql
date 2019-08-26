select 'Test' as Column1, 'test2' as column2 ;

select null as C1, 'value' as C2, null as C3_null;

-- Test pseudo-dual
select 1+1 from dual;
-- This syntax does not work (yet)
--select sysdate from dual;
-- This is the replacement
select julianday('now') as sysdate from dual;

-- Look at https://stackoverflow.com/questions/41007455/sqlite-vs-oracle-calculating-date-differences-hours 
-- for systdate modifications





-- Basic dump test
create table dump_me (a text);
insert into dump_me  values ('dumped');

.dump

.exit

