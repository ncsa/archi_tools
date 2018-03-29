#!/usr/bin/env python
"""
Handle arcimate interfaces.

Concerns:

1) Maintenance of Cache Directory structure.
2) Ingest CSV files exported frmo  Archimate to CSV cache.
3) Run Archimate in console log mode.
4) Clean the Archicamate XML fie taht remembers every Archimate file you ever opened.

Future -- Move CSVs to import area,

Retain some CSV manupulation functions for archimate
CSV files.

"""
import argparse
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


###########################################################
#
# Support for acquisition and caching of files so as
# to gain a stable working environment, as well as
# moving files to animport back for re-importing
# into Archi.
#
############################################################


DOWNLOAD_ROOT = "/Users/donaldp/export"   # hack for now
VAULT_ROOT= "/Users/donaldp/archi_tool/cache"  # hack for now

def cachepath(args):
    """return a path to cache dir appropriate for export prefix

       e.g for prefix DES_ make a cache/DES_ directory if needed
       and return that path to the caller.
    """
    directory = os.path.join(VAULT_ROOT, args.prefix)
    try:
            os.stat(directory)
    except:
            os.mkdir(directory)
            shutil.normal("made directory %s" % directory)
    return directory

def acquire(args):
      """Copy CSV files from the export area to the local cache"""
      for file in ["elements.csv","relations.csv","properties.csv"]: 
            ffrom = os.path.join(args.export_area,args.prefix + file)
            fto = os.path.join(cachepath(args),args.prefix + file)
            shutil.copyfile(ffrom, fto)
            shlog.normal("cached: %s" % fto)
      
###########################################################
#
# Support for running archi in obscure modes.
#
############################################################
            
def debug(args):
      """run archi with the logger console visible"""
      import subprocess
      subprocess.call("/Applications/Archi.app/Contents/MacOS/Archi -console", shell=True,
                      stdout=sys.stdout, stdin=sys.stdin, stderr=sys.stderr)

def forget(args):
    """Clean the file that remembers all the archimate files you ever opened"""
    file = os.path.join(os.environ["HOME"],
                        "Library/Application Support/Archi4/models.xml")

    if os.path.isfile(file):
        shlog.normal("deleting: %s" % file)
        os.remove(file)
    else:
        shlog.normal("%s did not exist" %  file)
###########################################################
#
# Support for Legacy CSV maniputipns. in
# Case I need them.....
#
############################################################


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


###########################################################
#
# Declarw Parser for command line visible routines
#
############################################################
      
def parsers(subparsers):

    #Subcommand  make an emty archiamte v1 databse.
    debug_parser = subparsers.add_parser('debug', description=debug.__doc__)
    debug_parser.set_defaults(func=debug)
    #debug_parser.add_argument("dbfile", help="name of databse file")

    
    #Acquire files from the working area to the cache
    acquire_parser = subparsers.add_parser('acquire', description=acquire.__doc__)
    acquire_parser.set_defaults(func=acquire)
    acquire_parser.add_argument("--export_area", "-e",
              help="export directory",default="/Users/donaldp/export/" )
    acquire_parser.add_argument("--cache", "-c",
              help="working cache directory",default="/Users/donaldp/archi_tool/cache/" )

    #Forget all Archimate modles, allow for a clean start of archiante
    forget_parser = subparsers.add_parser('forget', description=forget.__doc__)
    forget_parser.set_defaults(func=forget)

