#!/usr/bin/env python
"""
Acquire archi CSVs frm the Downloads area, into the csv_vailt.
ingest into archi.db sqllite datbase.
Print baisic reporting. 


"""
import argparse
import sqlite3
import shlog
import csv
import operator
import itertools
import fnmatch
import tabulate
import os
import datetime
import glob
import sys
import uuid

def extend(args):
      """
      Extend an archimate CSV file for re-import by repliating a prototype line nappend times.

      Code UUID in ther prototype for elements for the cell to be ne a newly generated UUID
      """
      csvfile = open(args.csv, 'ab') 
      prototype = args.prototype.split(",")
      writer = csv.writer(csvfile, delimiter=',',
            quotechar='"', quoting=csv.QUOTE_ALL)
      for lineno in range(args.nappends):
          line = []
          for p in prototype:
              if "UUID" in p :
                  line.append(uuid.uuid1())
              else:
                  line.append(p)
          writer.writerow(line)
        
        
if __name__ == "__main__":

    #main_parser = argparse.ArgumentParser(add_help=False)
    main_parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=argparse.RawDescriptionHelpFormatter)
    main_parser.add_argument('--loglevel','-l',
                             help='loglevel NONE, NORMAL, VERBOSE, VVERBOSE, DEBUG',
                             default="NORMAL")
    
    main_parser.add_argument("--dbfile", "-d", default="nebula_stats.db")
    main_parser.set_defaults(func=None) #if none then there are  subfunctions    
    subparsers = main_parser.add_subparsers(title="subcommands",
                       description='valid subcommands',
                       help='additional help')

    #Subcommand  to extend a archimate-style CSV export file 
    #extend_parser = subparsers.add_parser('extend', help="Extend an Archimate Entity file ")
    extend_parser = subparsers.add_parser('extend', help="extend.__doc__")
    extend_parser.set_defaults(func=extend)
    extend_parser.add_argument("csv", help="csvfile to append to")
    extend_parser.add_argument("prototype", help="commaed list that is a protytype.  Use UUID for a new UUID")
    extend_parser.add_argument("--nappends", "-n", help='Number of lines to append tofile ' , type=int, default=15)

    args = main_parser.parse_args()
    
    # translate text arguement to log level.
    # least to most verbose FATAL WARN INFO DEBUG
    # level also printst things to the left of it. 
    loglevel=shlog.__dict__[args.loglevel]
    assert type(loglevel) == type(1)
    shlog.basicConfig(level=shlog.__dict__[args.loglevel])


    if not args.func:  # there are no subfunctions
        main_parser.print_help()
        exit(1)
    args.func(args)
