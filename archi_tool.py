#!/usr/bin/env python
"""
A variety of Tools to assist wiht Archimate Maintenance.

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
import shutil
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

def header(args):
      """make a csv file with Just a header"""
      #import pdb; pdb.set_trace()
      types = ["elements", "properties","relations"]
      if args.csvtype not in types :
            shlog.error("%s is not one of %s" % (args.csvtype, types))
            exit(1)
      if args.csvtype == "elements":
            hdr = '"ID","Type","Name","Documentation"'
      elif args.csvtype == "properties":
            hdr = '"ID","Key","Value"'
      else:
            #relations
            hdr = '"ID","Type","Name","Documentation","Source","Target"'
      csvfile = open(args.prefix + args.csvtype + ".csv", 'w')
      csvfile.write(hdr + '\n')
      csvfile.close()

def acquire(args):
      """Copy CSV files from the export area to the local cache"""
      for file in ["elements.csv","relations.csv","properties.csv"]:
            ffrom = os.path.join(args.export_area,args.prefix + file)
            fto = os.path.join(args.cache,args.prefix + file)
            shutil.copyfile(ffrom, fto)

        
if __name__ == "__main__":

    #main_parser = argparse.ArgumentParser(add_help=False)
    main_parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=argparse.RawDescriptionHelpFormatter)
    main_parser.add_argument('--loglevel','-l',
                             help='loglevel NONE, NORMAL, VERBOSE, VVERBOSE, DEBUG',
                             default="ERROR")
    
    main_parser.add_argument("--dbfile", "-d", default="nebula_stats.db")
    main_parser.add_argument("--prefix", "-p", default="LSST_")
    main_parser.set_defaults(func=None) #if none then there are  subfunctions    
    subparsers = main_parser.add_subparsers(title="subcommands",
                       description='valid subcommands',
                       help='additional help')

    #Subcommand  to extend a archimate-style CSV export file 
    extend_parser = subparsers.add_parser('extend', help="extend.__doc__")
    extend_parser.set_defaults(func=extend)
    extend_parser.add_argument("csv", help="csvfile to append to")
    extend_parser.add_argument("prototype", help="command list that is a protytype.  Use UUID for a new UUID")
    extend_parser.add_argument("--nappends", "-n", help='Number of lines to append tofile ' , type=int, default=15)

    #Subcommand  make an archmate style empty (header only) CSV file
    header_parser = subparsers.add_parser('header', help="header.__doc__")
    header_parser.set_defaults(func=header)
    header_parser.add_argument("csvtype", help="type of csvfile to make")

    #Acquire files from the working area to the cache
    acquire_parser = subparsers.add_parser('acquire', help="acquire.__doc__")
    acquire_parser.set_defaults(func=acquire)
    acquire_parser.add_argument("--export_area", "-e",
              help="export directory",default="/Users/donaldp/export/" )
    acquire_parser.add_argument("--cache", "-c",
              help="working cache directory",default="/Users/donaldp/archi_tool/cache/" )

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
