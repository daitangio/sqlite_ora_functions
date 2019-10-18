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
    currentRecord = cx.fetchone()
    if currentRecord != None:
        sys.stdout.write("\n")
        colnames = "" + ("|".join(currentRecord.keys())) + "|"
        sys.stdout.write(colnames + "\n")
        for x in range(1, len(colnames) + 1):
            sys.stdout.write("-")
        sys.stdout.write("\n")
        while currentRecord != None:
            row_str = str(tuple(currentRecord))
            for elem in tuple(currentRecord):
                if elem != None:
                    sys.stdout.write(str(elem))
                else:
                    sys.stdout.write("null")
                sys.stdout.write("|")
            sys.stdout.write("\n")
            currentRecord = cx.fetchone()


####################################
class SqliteFunctionException(Exception):
    pass


# Decorator to register functions and  to manage exception
## from functools  import wraps
GLOBAL_REGISTER_LIST = []


def sql_register(sql_name, numargs, numargs2=None, numargs3=None, numargs4=None, numargs5=None):
    def wrap(f):
        GLOBAL_REGISTER_LIST.append((sql_name, numargs, f))
        if numargs2!=None:
            GLOBAL_REGISTER_LIST.append((sql_name, numargs2, f))
        if numargs3!=None:
            GLOBAL_REGISTER_LIST.append((sql_name, numargs3, f))
        if numargs4!=None:
            GLOBAL_REGISTER_LIST.append((sql_name, numargs4, f))
        if numargs5!=None:
            GLOBAL_REGISTER_LIST.append((sql_name, numargs5, f))            
        def wrapped_f(*args):
            return f(*args)

        return wrapped_f

    return wrap


###################################
"""Yield successive n-sized chunks from l."""


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]


###################################
#################### FUNCTIONS STARTS HERWE ##############################

@sql_register("decode", -1)
def oracle_decode(*arg):
    """
    decode(expression, search, result [,search, result]...[,default])

    DECODE compares expr to each search value one by one. If expr is equal to a search, then Oracle Database returns the corresponding result. If no match is found, then Oracle returns default. If default is omitted, then Oracle returns null.

    Ref https://docs.oracle.com/cd/B19306_01/server.102/b14200/functions040.htm

    The implementation required some work
    """
    # Now default is present if the size is
    if len(arg) < 3:
        raise Exception("Provide at least 3 input to decode")
    defaultPresent = (len(arg) % 2) == 0
    if defaultPresent:
        defaultValue = arg[-1]
        varlist = arg[1:-1]
    else:
        defaultValue = None
        varlist = arg[1:]
    expr = arg[0]
    for pairs in list(chunks(varlist, 2)):
        search, result = pairs
        # print(" %s -> %s " %(search,result))
        if expr == search:
            return result
    return defaultValue


# print(oracle_decode("zz",1,2,2,4,'default'))



@sql_register("to_date", 2,3)
@functools.lru_cache(maxsize=64, typed=True)
def oracle_to_date(string2convert, fmt, nlsparam=None):    
    """
    https://docs.oracle.com/cd/B19306_01/server.102/b14200/functions183.htm
    TO_DATE(char [, fmt [, 'nlsparam' ] ])

    TO_DATE converts char of CHAR, VARCHAR2, NCHAR, or NVARCHAR2 datatype to a value of DATE datatype. 
    The fmt is a datetime model format specifying the format of char. If you omit fmt, then char must be in the default date format. 
    If fmt is J, for Julian, then char must be an integer.

    On SQLite date are in iso-8601 format: 'YYYY-MM-DD HH:MM:SS'

    Also, the supported format is the C standard (1989 version)

    The Function is cached for performance reason
    """
    dobj = datetime.datetime.strptime(string2convert, fmt)
    # Return a nice Sqlite date string
    return dobj.isoformat(sep=" ", timespec="seconds")





def oracle_to_char(input, fmt=None, nlsparam=None):
    """ 
    FIXME TO IMPLEMENT
    TO_CHAR
    TO_CHAR({ datetime | interval } [, fmt [, 'nlsparam' ] ])
    https://docs.oracle.com/cd/B19306_01/server.102/b14200/functions180.htm
    TO_CHAR (datetime) converts a datetime or interval value of DATE, TIMESTAMP, TIMESTAMP WITH TIME ZONE, or TIMESTAMP WITH LOCAL TIME ZONE datatype to a value of VARCHAR2 datatype in the format specified by the date format fmt. If you omit fmt, then date is converted to a VARCHAR2 value as follows: [....]

    The 'nlsparam' argument specifies the language in which month and day names and abbreviations are returned.
    """
    pass





@sql_register("regexp_replace", 3,4,5,6)
def oracle_regexp_replace(
    source, pattern, replace_string, position=1, occurence=0, match_parameter=None
):
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
    pythonFlags = translate_oracle_match_parameters(match_parameter)
    if position == 1:
        return re.sub(
            pattern, replace_string, source, count=occurence, flags=pythonFlags
        )
    else:
        return source[0 : (position - 1)] + re.sub(
            pattern,
            replace_string,
            source[(position - 1) :],
            count=occurence,
            flags=pythonFlags,
        )


def translate_oracle_match_parameters(match_parameter):
    pythonFlags = 0
    if match_parameter:
        if "i" in match_parameter:
            pythonFlags |= re.IGNORECASE
            # 'c' is the default
        if "n" in match_parameter:
            pythonFlags |= re.DOTALL
        if "m" in match_parameter:
            pythonFlags |= re.MULTILINE
        if "x" in match_parameter:
            raise Exception("x flag is unimplemented")
    return pythonFlags





@sql_register("regexp_like", 2,3)
def oracle_regexp_like(source, pattern, match_parameter=None):
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
    pythonFlags = translate_oracle_match_parameters(match_parameter)
    return 1 if re.search(pattern, source, flags=pythonFlags) else 0





@sql_register("nvl", 2)
def oracle_nvl(expr1, expr2):
    """
    Ref https://docs.oracle.com/database/121/SQLRF/functions131.htm#SQLRF00684

    NVL(expr1, expr2)

    NVL lets you replace null (returned as a blank) with a string in the results of a query. If expr1 is null, then NVL returns expr2. If expr1 is not null, then NVL returns expr1.

    The arguments expr1 and expr2 can have any data type. If their data types are different, then Oracle Database implicitly converts one to the other. If they cannot be converted implicitly, then the database returns an error. The implicit conversion is implemented as follows:


    """    
    if expr1:
        return expr1
    else:
        return expr2





@sql_register("nvl2", 3)
def oracle_nvl2(expr1, expr2, expr3):
    """ NVL2(expr1, expr2, expr3)
        NVL2 lets you determine the value returned by a query based on whether a specified expression is null or not null. 
        If expr1 is not null, then NVL2 returns expr2. If expr1 is null, then NVL2 returns expr3.
    """
    if expr1:
        return expr2
    else:
        return expr3


## IMAP EMAIL FUNCTIONS
def getImapMailboxHeaders(server, user, password, path, searchSpec=None):
    """ WORK IN PROGRESS
        imap_headers(server,user,password,path , index, [, searchspec])
        Load specified email header from an imap server. index starts from 0.
        
        Example
        imap_headers( 'imap.gmail.com','notatallawhistleblowerIswear@gmail.com','secret','folder',0)

    See also
    https://gist.github.com/robulouski/7441883
    https://oracle-base.com/articles/10g/utl_mail-send-email-from-the-oracle-database
    https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.create_aggregate

    """    
    import imaplib, getpass, email, email.header

    M = imaplib.IMAP4_SSL(server)

    try:
        rv, data = M.login(user, password)
    except imaplib.IMAP4.error as err:
        raise err
    rv, mailboxes = M.list()
    if rv != "OK":
        raise Exception("Cannot list mailboxes:" + rv)
    rv, data = M.select(path)
    # TODO CONTINUE
    raise Exception("Still not implemented")




@sql_register("fs", 1,2)
def filesystem_fs(path_str, glob_stuff="*", sep=","):
    """
    fs(path_str, glob_stuff="*", sep=",")
    Enable access to file system: list files
    """
    from pathlib import Path
    l = []
    for f in Path(path_str).glob(glob_stuff):
        l.append(f.name)
    return sep.join(l)


@sql_register("raise_exception", 1)
def raise_exception(exception_string):
    """ 
    Used to raise an exception string and halt execution

    """
    raise SqliteFunctionException(exception_string)


########################## SUPPORT





@sql_register("assert_equals", 2,3)
def assert_equals(expected, value, msg=""):
    """
    Assert function is used for unit testing
    """
    if value != expected:
        if msg != "":
            return ("Test FAILED: Expected: %s instead of %s TestCase:" + msg) % (
                expected,
                value,
            )
        else:
            return "Test FAILED: Expected: %s instead of %s" % (expected, value)
    else:
        return "ok"


def showHelp():
    print("HELP:")
    print("Lite*Plus: your full stop to SQLite3 compatibility layer")
    print("Super charge your script with a bunch of ad-hoc python functions")
    print(
        """ Commands:
    .exit                        Exit from liteplus
    .help                        This help message
    .print  Message              
    .dump                        Execute a dump of the current database

    The prompt show the commands executed and the total changes executed so far.
   
    select help("nvl")  ;   Get full documentation on nvl


    """
    )

@sql_register("help",1)
def help_fun(func_input):
    """Provide support for docstring documentation PEP-257"""
    for func_name, args, f in GLOBAL_REGISTER_LIST:
        if func_name == func_input:
            return str(f.__doc__)
    return "No function defined:"+str(func_input)

@sql_register("lite_plus_functions",0)
def lite_plus_tot_functions():
    """ Return the total number of lite_plus function extentions."""
    return len(GLOBAL_REGISTER_LIST)

@sql_register("lite_plus",1)
def lite_plus_function_list(i):
    """ Return the name of the i-function extension, in definition order. Order may change between implementations
    Take a look at doc/doc_builder.sql
    for an example usage of this function
    """
    func_name, args, f = GLOBAL_REGISTER_LIST[i]
    return str(func_name)
    

# GLOBAL
registeredFunctions = 0

# Constants

# Limit to the buffer for the statement execution
# Oracle PLSQL has a 32KB limit on literals.
# We use the same limit here.
MAX_BUFFER_SIZE_KB = 32


def main(argv=sys.argv):

    databaseName = argv[1]
    con = sqlite3.connect(databaseName)

    sqlite3.enable_callback_tracebacks(True)

    def register(fname, args, func):
        global registeredFunctions
        con.create_function(fname, args, func)
        # print("R*%i -> %s" % ( args,fname))
        registeredFunctions = registeredFunctions + 1

    for func_name, args, f in GLOBAL_REGISTER_LIST:
        register(func_name, args, f)

    import math

    for f in [math.sin, math.cos, math.tan, math.ceil, math.floor]:
        register(f.__name__, 1, f)
        GLOBAL_REGISTER_LIST.append((f.__name__,1,f))


    con.execute("PRAGMA foreign_keys = ON")
    # See https://en.wikipedia.org/wiki/DUAL_table
    con.execute("CREATE VIEW if not exists  dual AS SELECT 'x' AS dummy")
    # con.execute("pragma journal_mode=wal")
    LITE_PLUS_VERSION = "SQLite*Plus:%s on %s Registered Functions: %i" % (
        sqlite3.sqlite_version,
        databaseName,
        registeredFunctions,
    )
    if len(argv)==2:
        repl_cycle(con, LITE_PLUS_VERSION)
    else:
        execute_files(argv[2:],con, LITE_PLUS_VERSION)

def execute_files(flist,con, lite_plus_ver):
    for fname in flist:
        #print("Processing", fname)
        with open(fname,"r") as f:
            repl_cycle(con,lite_plus_ver,f)

def repl_cycle(con, lite_plus_ver, input_file=sys.stdin):
    # REPL cycle
    if input_file ==sys.stdin:
        sys.stdout.write(lite_plus_ver)
    buffer = ""
    commandExecuted = 0
    con.row_factory = sqlite3.Row
    while True:
        l = input_file.readline()
        buffer += l
        if len(buffer) > (MAX_BUFFER_SIZE_KB * 1024):
            raise Exception(
                (
                    "BUFFER OVERFLOW ERROR Line too long. Limit: %i Kb Offending line:\nSTART:%s\nEND:%s\n"
                    % (MAX_BUFFER_SIZE_KB, buffer[0:70], buffer[-70:])
                )
            )
        if ";" in l:
            # See https://github.com/jonathanslenders/python-prompt-toolkit/blob/master/examples/tutorial/sqlite-cli.py
            try:
                cx = con.cursor()
                cx.execute(buffer)
                printResult(cx)
            except Exception as e:
                sys.stdout.write("[LITE-ERROR] On the following chunk:")
                sys.stdout.write("\t%s" % (buffer))
                sys.stdout.write("[LITE-ERROR] \t" + repr(e))
            commandExecuted += 1
            buffer = ""
            # Present prompt only if interactive:
            if input_file ==sys.stdin:
                sys.stdout.write("\n%i-%i>" % (commandExecuted, con.total_changes))
        else:
            liteCmd = l.strip()
            if liteCmd == ".exit":
                break
            elif liteCmd == ".dump":
                sys.stdout.write(
                    "\n-- Dump generated by " + str(lite_plus_ver) + "\n"
                )
                for line in con.iterdump():
                    sys.stdout.write(line)
                    sys.stdout.write("\n")
            elif liteCmd.startswith(".print "):
                sys.stdout.write("\n%s\n" % (liteCmd[6:]))
                buffer = ""
            elif liteCmd == ".help":
                showHelp()
                buffer = ""


if __name__ == "__main__":
    main()
