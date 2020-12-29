-- Ideas taken from 
-- https://dgl.cx/2020/06/sqlite-json-support
CREATE TABLE t (
   body TEXT,
   d INT GENERATED ALWAYS AS (json_extract(body, '$.d')) VIRTUAL);

insert into t values(json('{"d":"42"}'));
select * from t WHERE d = 42;

.exit