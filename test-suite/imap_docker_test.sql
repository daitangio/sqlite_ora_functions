select imap_count("127.0.0.1","jj","pass") as email_count ;

select imap_email("127.0.0.1","jj","pass",0)  as message1;

WITH RECURSIVE
  cnt(x) AS (VALUES(1) UNION ALL SELECT x+1 FROM cnt WHERE x<imap_count("127.0.0.1","jj","pass","test"))
select x-1 as num, imap_email("127.0.0.1","jj","pass",x-1,"test") as message FROM cnt;




-- select x from dual where x between 0 and imap_count("127.0.0.1","jj","pass")-1;

/*
select imap_email("127.0.0.1","jj","pass",idx, "INBOX")  as message
where idx between 0 and (imap_count("127.0.0.1","jj","pass")-1);
*/

.exit