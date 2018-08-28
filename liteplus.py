#!/usr/bin/env python
# -*- mode: company ; mode: python  -*-
"""How to do regular expressions in sqlite3 (using python)."""
from __future__ import print_function

import re
import sys
import time
import datetime
import sqlite3

import functools

######################################
# Low level support 
######################################
"""
 Print a cursor result
"""
def printResult(cx):
    currentRecord=cx.fetchone()
    if currentRecord!=None:
        sys.stdout.write('\n')
        colnames=''+('|'.join(currentRecord.keys()))+'|'
        sys.stdout.write(colnames+'\n')
        for x in range(1,len(colnames)+1):
            sys.stdout.write('-')
        sys.stdout.write('\n')
        while currentRecord != None:
            row_str=str(tuple(currentRecord))
            for elem in tuple(currentRecord):
                if elem!=None:
                    sys.stdout.write(elem)
                else:
                    sys.stdout.write("null")
                sys.stdout.write('|')
            sys.stdout.write('\n')
            currentRecord=cx.fetchone()    


####################################
# Decorator to manage exception
class handle_exception(object):
    def __init__(self, f):
        """
        If there are no decorator arguments, the function
        to be decorated is passed to the constructor.
        """
        self.f = f

    def __call__(self, *args):
        """
        The __call__ method is not called until the
        decorated function is called.
        """
        try:            
            return self.f(*args)
        except:
            print("[LITE-ERROR] Detected Exception thrown by %s: %s" % (self.f.__name__,sys.exc_info()[0]))
            raise
###################################
"""Yield successive n-sized chunks from l."""
def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]
###################################
"""
decode(expression, search, result [,search, result]….[,default])

DECODE compares expr to each search value one by one. If expr is equal to a search, then Oracle Database returns the corresponding result. If no match is found, then Oracle returns default. If default is omitted, then Oracle returns null.

Ref https://docs.oracle.com/cd/B19306_01/server.102/b14200/functions040.htm

The implementation required some work
"""
@handle_exception
def oracle_decode(*arg):
    # Now default is present if the size is
    if(len(arg) < 3):
        raise Exception('Provide at least 3 input to decode')
    defaultPresent = (len(arg) %2) == 0
    if defaultPresent:
        defaultValue=arg[-1]
        varlist=arg[1:-1]
    else:
        defaultValue=None
        varlist=arg[1:]
    expr=arg[0]
    for pairs in list(chunks(varlist,2)):
        search,result=pairs
        #print(" %s -> %s " %(search,result))
        if expr==search:
            return result
    return defaultValue

#print(oracle_decode("zz",1,2,2,4,'default'))

"""
https://docs.oracle.com/cd/B19306_01/server.102/b14200/functions183.htm
TO_DATE(char [, fmt [, 'nlsparam' ] ])

TO_DATE converts char of CHAR, VARCHAR2, NCHAR, or NVARCHAR2 datatype to a value of DATE datatype. The fmt is a datetime model format specifying the format of char. If you omit fmt, then char must be in the default date format. If fmt is J, for Julian, then char must be an integer.

On SQLite date are in iso-8601 format: 'YYYY-MM-DD HH:MM:SS'

Also, the supported format is the C standard (1989 version)

The Function is cached for performance reason
"""
@handle_exception
@functools.lru_cache(maxsize=64, typed=True)
def oracle_to_date(string2convert, fmt, nlsparam=None):
    dobj=datetime.datetime.strptime(string2convert, fmt)
    # Return a nice Sqlite date string
    return dobj.isoformat(sep=' ',timespec='seconds')

""" 
FIXME TO IMPLEMENT
TO_CHAR
TO_CHAR({ datetime | interval } [, fmt [, 'nlsparam' ] ])
https://docs.oracle.com/cd/B19306_01/server.102/b14200/functions180.htm
TO_CHAR (datetime) converts a datetime or interval value of DATE, TIMESTAMP, TIMESTAMP WITH TIME ZONE, or TIMESTAMP WITH LOCAL TIME ZONE datatype to a value of VARCHAR2 datatype in the format specified by the date format fmt. If you omit fmt, then date is converted to a VARCHAR2 value as follows: [....]

The 'nlsparam' argument specifies the language in which month and day names and abbreviations are returned.
"""
@handle_exception
def oracle_to_char(input,fmt=None,nlsparam=None):
    pass

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

GG: UNIMPLEMENTED

If you specify multiple contradictory values, then Oracle uses the last value. For example, if you specify 'ic', then Oracle uses case-sensitive matching. If you specify a character other than those shown above, then Oracle returns an error.

If you omit match_param, then:

The default case sensitivity is determined by the value of the NLS_SORT parameter.

A period (.) does not match the newline character.

The source string is treated as a single line.

"""
@handle_exception
def oracle_regexp_replace(source,pattern,replace_string,position=1,occurence=0,match_parameter=None):
    pythonFlags=translate_oracle_match_parameters(match_parameter)
    if position == 1:
        return re.sub(pattern,replace_string,source,count=occurence,flags=pythonFlags)
    else:
        return source[0:(position-1)] +  re.sub(pattern,replace_string,source[(position-1):],count=occurence,flags=pythonFlags)



def translate_oracle_match_parameters(match_parameter):
    pythonFlags=0
    if match_parameter:
        if 'i' in match_parameter:
            pythonFlags |=re.IGNORECASE
            # 'c' is the default
        if 'n' in match_parameter:
            pythonFlags |=re.DOTALL
        if 'm' in match_parameter:
            pythonFlags |=re.MULTILINE
        if 'x' in match_parameter:
            raise Exception("x flag is unimplemented")
    return pythonFlags

"""
Ref https://docs.oracle.com/database/121/SQLRF/conditions007.htm#SQLRF00501

REGEXP_LIKE is similar to the LIKE condition, except REGEXP_LIKE performs regular expression matching instead of the simple pattern matching performed by LIKE. This condition evaluates strings using characters as defined by the input character set.

REGEXP_LIKE(source_char, pattern
            [, match_param ]
           )

source_char is a character expression that serves as the search value. It is commonly a character column and can be of any of the data types CHAR, VARCHAR2, NCHAR, NVARCHAR2, CLOB, or NCLOB.

pattern is the regular expression. It is usually a text literal and can be of any of the data types CHAR, VARCHAR2, NCHAR, or NVARCHAR2. It can contain up to 512 bytes. If the data type of pattern is different from the data type of source_char, Oracle converts pattern to the data type of source_char. For a listing of the operators you can specify in pattern, refer to Appendix D, "Oracle Regular Expression Support".

match_parameter is a text literal that lets you change the default matching behavior of the function.

"""
@handle_exception
def oracle_regexp_like(source,pattern,match_parameter=None):
    pythonFlags=translate_oracle_match_parameters(match_parameter)
    return 1 if re.search(pattern,source,flags=pythonFlags) else 0

"""
Ref https://docs.oracle.com/database/121/SQLRF/functions131.htm#SQLRF00684

NVL(expr1, expr2)

NVL lets you replace null (returned as a blank) with a string in the results of a query. If expr1 is null, then NVL returns expr2. If expr1 is not null, then NVL returns expr1.

The arguments expr1 and expr2 can have any data type. If their data types are different, then Oracle Database implicitly converts one to the other. If they cannot be converted implicitly, then the database returns an error. The implicit conversion is implemented as follows:


"""
@handle_exception
def oracle_nvl(expr1,expr2):
    if expr1:
        return expr1
    else:
        return expr2


""" NVL2(expr1, expr2, expr3)
NVL2 lets you determine the value returned by a query based on whether a specified expression is null or not null. 
If expr1 is not null, then NVL2 returns expr2. If expr1 is null, then NVL2 returns expr3.
"""
@handle_exception
def oracle_nvl2(expr1,expr2,expr3):
    if expr1:
        return expr2
    else:
        return expr3
    
    
"""
Assert function is used for unit testing
"""
@handle_exception
def assert_equals(expected,value,msg=""):
    if value!=expected:
        if msg !="":
            return ( ("Test FAILED: Expected: %s instead of %s TestCase:"+msg) % (expected,value))
        else:
            return ( "Test FAILED: Expected: %s instead of %s" % (expected,value))
    else:
        return 'ok'

    

def showHelp():
    print("HELP:")
    print("Lite*Plus: your full stop to SQLite3 compatibility layer")
    print("Super charge your script with a bunch of ad-hoc python functions")
    print(""" Commands:
    .exit                        Exit from liteplus
    .help                        This help message
    .print  Message              
    """)




# GLOBAL
registeredFunctions=0
def main(argv=sys.argv):

    databaseName=argv[1]
    con = sqlite3.connect(databaseName)
    
    sqlite3.enable_callback_tracebacks(True)
    
    def register(fname, args,func):
        global registeredFunctions
        con.create_function(fname,args,func)
        #print("R*%i -> %s" % ( args,fname))
        registeredFunctions = registeredFunctions+1
        
    register('assert_equals',2,assert_equals)
    register('assert_equals',3,assert_equals)
    
    register('regexp_replace', 3, oracle_regexp_replace)
    register('regexp_replace', 4, oracle_regexp_replace)
    register('regexp_replace', 5, oracle_regexp_replace)
    register('regexp_replace', 6, oracle_regexp_replace)
    

    register('regexp_like',2,oracle_regexp_like)
    register('regexp_like',3,oracle_regexp_like)

    register('nvl',2,oracle_nvl)    
    register('nvl2',3,oracle_nvl2)

    register('to_date',2,oracle_to_date)
    register('to_date',3,oracle_to_date)

    # Decode accepts variable data
    register('decode',-1,oracle_decode)
    
    # Push some math functions
    import math
    for f in [math.sin,math.cos,math.tan,math.ceil,math.floor]:
         register(f.__name__,1,f)

    con.execute("PRAGMA foreign_keys = ON")
    #con.execute("pragma journal_mode=wal")
    
    print("SQLite*Plus:%s on %s Registered Functions: %i" % (sqlite3.sqlite_version, databaseName, registeredFunctions))
    #print(databaseName+">")
    # REPL cycle
    buffer=""
    commandExecuted=0
    con.row_factory = sqlite3.Row
    while True:
        l=sys.stdin.readline()
        buffer += l
        if ';' in l:
            # See https://github.com/jonathanslenders/python-prompt-toolkit/blob/master/examples/tutorial/sqlite-cli.py
            try:
                cx=con.cursor()
                cx.execute(buffer)
                printResult(cx)
            except Exception as e:
                print("[LITE-ERROR] On the following chunk:")
                print("\t%s" %(buffer))
                print("[LITE-ERROR] \t"+repr(e))
            commandExecuted +=1
            buffer=""
            sys.stdout.write("\n%i>" %(commandExecuted))
        else:
            liteCmd=l.strip()
            if liteCmd=='.exit':
                print("LITE PLUS EXITING...")
                break
            elif liteCmd=='.help':
                showHelp()
                buffer=""
            elif liteCmd.startswith('.print '):
                print("\n%s\n"%(liteCmd[6:]))
                buffer=""
        
if __name__ == '__main__':
    main()
