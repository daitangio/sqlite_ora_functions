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


-- Rowid: here no super power needed. The same oracle code works on sqlite
create table dup_table (column1 text, column2 text, column3 text);

insert into dup_table values('1','2','3');
insert into dup_table values('1','2','3');
insert into dup_table values('1','3','3');
insert into dup_table values('1','3','3');


select rowid, column1 || '_' || column2 || '_' || column3 as COL_MERGE from dup_table;

DELETE FROM dup_table
WHERE rowid not in
    (SELECT MIN(rowid)
    FROM dup_table
    GROUP BY column1, column2);

select assert_equals(2, count(*)) from dup_table;


-- Basic dump test
create table dump_me (a text);
insert into dump_me  values ('dumped');

.dump

.exit

