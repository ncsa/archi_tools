"""
This file contains code related common query and databse codes.

This file is for DB-generic support.  e.g. nothing archimate
or model specific.
"""

import sqlite3
import shlog
import tabulate


######################################################
#
#  HACK -- copied this  -- need more code factoring.
#
########################################################

def q(args, sql):
    #a funnel routine for report queries, main benefit is query printing
    con = sqlite3.connect(args.dbfile)
    con.text_factory = lambda x: x.decode("utf-8")
    cur = con.cursor()
    shlog.verbose (sql)
    result  = cur.execute (sql)
    con.commit()
    return result

def qp(args, sql, list_of_lists):
    #a funnel routine for report queries, main benefit is query printing
    con = sqlite3.connect(args.dbfile)
    con.text_factory = lambda x: x.decode("utf-8")
    cur = con.cursor()
    shlog.verbose (sql)
    result  = cur.executemany (sql,list_of_lists)
    con.commit()
    return result


