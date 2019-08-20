select 'Test' as Column1, 'test2' as column2 ;

select null as C1, 'value' as C2, null as C3_null;

-- Basic dump test
create table dump_me (a text);
insert into dump_me  values ('dumped');

.dump

.exit

