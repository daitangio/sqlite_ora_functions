#!/usr/bin/env python
"""How to do regular expressions in sqlite3 (using python)."""
from __future__ import print_function

import re
import sys
import time
import datetime
import sqlite3


def words():
    yield "giovanni"
    yield "giorgi"
    yield "oracle"
    yield "compatible"
    yield "layer"
    yield "is"
    yield "here"
    #with open('/usr/share/dict/words', 'rb') as fp:
    #    for word in fp:
    #        yield word.strip()

# RE replace
# re.sub(pattern, repl, string, count=0, flags=0)
# 
"""
ORACLE:
https://docs.oracle.com/database/121/SQLRF/functions163.htm#SQLRF06302

REGEXP_REPLACE(source,pattern,replace_string[,position,occurence,match_param])

position is a positive integer indicating the character of source_char where Oracle should begin the search. The default is 1, meaning that Oracle begins the search at the first character of source_char.

"""
def oracle_regexp_replace(source,pattern,replace_string,position=1,occurence=0):
    try:
        if position == 1:
            return re.sub(pattern,replace_string,source,count=occurence)
        else:
            return source[0:(position-1)] +  re.sub(pattern,replace_string,source[(position-1):],count=occurence)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

def regexp(y, x, search=re.search):
    return 1 if search(y, x) else 0



def main(argv=sys.argv):

    con = sqlite3.connect(":memory:")
    def register(fname, args,func):
        con.create_function(fname,args,func)
        print("R*%i -> %s" % ( args,fname))
    
    #con.create_function('regexp', 2, regexp)
    register('regexp_replace', 3, oracle_regexp_replace)
    register('regexp_replace', 4, oracle_regexp_replace)
    register('regexp_replace', 5, oracle_regexp_replace)

    # Push some math functions
    import math
    for f in [math.sin,math.cos,math.tan,math.ceil,math.floor]:
         register(f.__name__,1,f)

    con.execute("pragma journal_mode=wal")
    con.execute("PRAGMA foreign_keys = ON")
    print("SQlite:%s OracleZ and Sane Pragma with WAL" % (sqlite3.sqlite_version))
    con.execute('CREATE TABLE words (word text);')

    wordtuple = tuple(words())

    con.executemany('INSERT INTO words VALUES(?)', zip(wordtuple))

    for row in con.execute("SELECT regexp_replace(word,'(oracle)','sqlite \\1') FROM words"):
        print(row)
    print("* Check position>1 replace g with z only one occurence")
    for row in con.execute("SELECT regexp_replace(word,'g','z',1,1) FROM words where word ='giorgi'"):
        print(row)
    for row in con.execute("SELECT regexp_replace(word,'g','z',2,1) FROM words where word ='giorgi'"):
        print(row)


    # Oracle example
    # REGEXP_REPLACE(phone_number,'([[:digit:]]{3})\.([[:digit:]]{3})\.([[:digit:]]{4})','(\1) \2-\3')
    
    # start = datetime.datetime.now()
    # for row in con.execute('SELECT * FROM words WHERE word REGEXP ?', [r'(?i)xylo']):
    #     print(row)
    # end = datetime.datetime.now()
    # print(start)
    # print(end)

    # start = datetime.datetime.now()
    # for val in filter(lambda w: re.search(r'(?i)xylo', w), wordtuple):
    #     print(val)
    # end = datetime.datetime.now()

    # print(start)
    # print(end)


if __name__ == '__main__':
    main()
