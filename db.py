#!/usr/bin/env python
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

def qd(args, sql):
    #return results of query as a list of dictionaries,
    #one for each row. 
    
    con = sqlite3.connect(args.dbfile)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    shlog.verbose(sql)
    results = cur.execute (sql)
    shlog.normal(results)
    return results

def qdescription(args, sql):
    con = sqlite3.connect(args.dbfile)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    shlog.verbose("description query %s" % sql)
    results = cur.execute (sql)
    description = [d[0] for d in cur.description]
    shlog.verbose("description obtained  %s" % (description))
    con.close()
    return  description

def query(args):
    for r in qd(args, args.sql):
        shlog.normal("row: %s" % r)
        shlog.normal("type: %s" % type(r))
        shlog.normal("keys: %s" % r.keys())
        shlog.normal("contents: %s" %",".join([r[k] for k in r.keys()]))
    shlog.normal ("description: %s" % qdescription(args, args.sql))

if __name__ == "__main__":
    #main_parser = argparse.ArgumentParser(add_help=False)
    import argparse
    main_parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    main_parser.add_argument('--loglevel','-l',
                             help=shlog.LOGHELP,
                             default="NORMAL")
    
    main_parser.add_argument("--dbfile", "-d", default="LSST_archi_tool.db")
    main_parser.set_defaults(func=None) #if none then there are  subfunctions    
    subparsers = main_parser.add_subparsers(title="subcommands",
                       description='valid subcommands',
                       help='additional help')
    

    #Subcommand  to  make a query 
    query_parser = subparsers.add_parser('query', help=query.__doc__)
    query_parser.set_defaults(func=query )  
    query_parser.add_argument("--force", "-f", help="remove existing db file of the same name", default=False, action='store_true')
    query_parser.add_argument("--show" , "-s", help="show result in excel", default=False, action='store_true')
    query_parser.add_argument("sql", help="query to execute", default="SELECT * from DUAL")

  
    args = main_parser.parse_args()


    # translate text arguement to log level.
    # least to most verbose FATAL WARN INFO DEBUG
    # level also printst things to the left of it. 
    loglevel=shlog.__dict__[args.loglevel]
    assert type(loglevel) == type(1)
    shlog.basicConfig(level=shlog.__dict__[args.loglevel])
    shlog.normal("Database is %s" % args.dbfile)
    if not args.func:  # there are no subfunctions
        main_parser.print_help()
        exit(1)
    args.func(args)
