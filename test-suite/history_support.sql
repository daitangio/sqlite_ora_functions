.mode table
.headers on
.echo on

create table CUSTOMER(
    xd number not null, /* On SQLITE you got a rowid special unique id*/
    NDG number not null,
    xds number,
    d_start timestamp,
    d_end timestamp,
    editor varchar2(40),
    name varchar2(80),
    Primary key (xd),
 CONSTRAINT FK_HISTORY_CUSTOMER
    FOREIGN KEY (XDS)
    REFERENCES CUSTOMER (XD)
);

-- Forbids different CUSTOMERS with same NDG:
create unique index CUSTOMER_UQ_NDG ON CUSTOMER( case when xd=xds then NDG END );

-- View on active data
create view VCUSTOMER as 
 select * from CUSTOMER where xd=xds;

-- Insert record example (unique id are fixed for simplicity)
INSERT INTO CUSTOMER(XD,XDS,d_start,d_end,ndg,name,editor) values(1 ,1,date('now'),null,100,'Zeno Parisi','BOT');



select * from customer order by XD desc; 

-- Copy old record XD > XDS
INSERT INTO CUSTOMER(XD,XDS,d_start,d_end,editor,name,ndg)
select rowid+1 /*trick to get a new one */, XDS,d_start,date('now'),editor,name,ndg
from CUSTOMER where xd=xds and NDG=100;

-- Update XD=XDS
update CUSTOMER set name='Zeno Paris', editor='GG', d_start=date('now') where xd=xds and ndg=100;

-- After update
select * from customer order by XD desc; 

-- New record
INSERT INTO customer(XD,XDS,d_start,d_end,ndg,name,editor) 
select max(rowid)+1,max(rowid)+1, date('now'),null,200,'Scott Tiger','BOT'
from customer;


/* Trigger support for trasparent updates on vcustomer
 * 
 */
create trigger auto_history_customer_update
instead of update on vcustomer
FOR EACH ROW
begin
 INSERT INTO CUSTOMER(XD,XDS,d_start,d_end,editor,name,ndg)
    select max(rowid)+1 /*trick to get a new one */, XDS,d_start,date('now'),editor,name,ndg
    from CUSTOMER where xd=xds and NDG =OLD.ndg;
 update CUSTOMER set name=NEW.name, editor=NEW.editor, d_start=date('now') where xd=xds and xd=OLD.XD;
end;

/* This trigger only manage rowids */

create trigger auto_history_customer_insert
instead of insert on vcustomer
FOR EACH ROW
begin
 INSERT INTO CUSTOMER(XD,XDS,          d_start,     d_end,    editor,     name,     ndg)
  select    max(rowid)+1,max(rowid)+1, NEW.d_start, NEW.d_end,NEW.editor, NEW.name, NEW.NDG
  from customer;
end;



-- Trigger support example

update vcustomer  set editor='Changed via trigger' where NDG=200;
-- select * from customer order by xd desc;
select * from  vcustomer;
.echo off

.print Real table data:
select * from customer order by d_start desc;

.exit