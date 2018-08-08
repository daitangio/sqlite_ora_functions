#!/usr/bin/env python
# -*- mode: company ; mode: python  -*-
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

match_parameter is a text literal that lets you change the default matching behavior of the function. The behavior of this parameter 
is the same for this function as for REGEXP_COUNT. 
match_param is a text literal that lets you change the default matching behavior of the function. You can specify one or more of the following values for match_param:

'i' specifies case-insensitive matching.

'c' specifies case-sensitive matching.

'n' allows the period (.), which is the match-any-character character, to match the newline character. If you omit this parameter, then the period does not match the newline character.

'm' treats the source string as multiple lines. Oracle interprets the caret (^) and dollar sign ($) as the start and end, respectively, of any line anywhere in the source string, rather than only at the start or end of the entire source string. If you omit this parameter, then Oracle treats the source string as a single line.

'x' ignores whitespace characters. By default, whitespace characters match themselves.

If you specify multiple contradictory values, then Oracle uses the last value. For example, if you specify 'ic', then Oracle uses case-sensitive matching. If you specify a character other than those shown above, then Oracle returns an error.

If you omit match_param, then:

The default case sensitivity is determined by the value of the NLS_SORT parameter.

A period (.) does not match the newline character.

The source string is treated as a single line.

"""
def oracle_regexp_replace(source,pattern,replace_string,position=1,occurence=0,match_parameter=None):
    try:
        pythonFlags=0
        if match_parameter:
            if 'i' in match_parameter:
                pythonFlags=re.IGNORECASE
        else:
            pythonFlags=0
        
        if position == 1:
            return re.sub(pattern,replace_string,source,count=occurence,flags=pythonFlags)
        else:
            return source[0:(position-1)] +  re.sub(pattern,replace_string,source[(position-1):],count=occurence,flags=pythonFlags)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

def regexp(y, x, search=re.search):
    return 1 if search(y, x) else 0


def showHelp():
    print("HELP:")
    print("Lite*Plus: your full stop to SQLite3 compatibility layer")
    print("Super charge your script with a bunch of ad-hoc python functions")
    print("")

def main(argv=sys.argv):

    databaseName=argv[1]
    con = sqlite3.connect(databaseName)
    
    sqlite3.enable_callback_tracebacks(True)
    
    def register(fname, args,func):
        con.create_function(fname,args,func)
        print("R*%i -> %s" % ( args,fname))
    
    #con.create_function('regexp', 2, regexp)
    register('regexp_replace', 3, oracle_regexp_replace)
    register('regexp_replace', 4, oracle_regexp_replace)
    register('regexp_replace', 5, oracle_regexp_replace)
    register('regexp_replace', 6, oracle_regexp_replace)

    # Push some math functions
    import math
    for f in [math.sin,math.cos,math.tan,math.ceil,math.floor]:
         register(f.__name__,1,f)

    con.execute("pragma journal_mode=wal")
    con.execute("PRAGMA foreign_keys = ON")
    
    print("SQLite*Plus:%s on %s " % (sqlite3.sqlite_version, databaseName))
    #print(databaseName+">")
    # REPL cycle
    buffer=""
    commandExecuted=0
    while True:
        l=sys.stdin.readline()
        buffer += l
        if ';' in l:
            # See https://github.com/jonathanslenders/python-prompt-toolkit/blob/master/examples/tutorial/sqlite-cli.py
            try:
                messages = con.execute(buffer)
            except Exception as e:
                print("[LITE-ERROR]* \t"+repr(e))
            else:
                for message in messages:
                    print(message)
            commandExecuted +=1
            buffer=""
            print("%i>" %(commandExecuted))
        else:
            liteCmd=l.strip()
            if liteCmd=='.exit':
                print("LITE PLUS EXITING...")
                break
            elif liteCmd=='.help':
                showHelp()
        
if __name__ == '__main__':
    main()
