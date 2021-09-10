
-- select pycall_create('print','params');

.print Pycall Test

create table param_table (key text, value text);

insert into param_table values('param1','yeppa');



.pycall print, param_table


.print Exit

.exit