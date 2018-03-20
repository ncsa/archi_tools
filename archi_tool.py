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


def t(x):return x
def i(x):return int(x)
def r(x):return float(x)

class SQLTable:
    def __init__(self):
        self.columns   = None  #list of Header keywords as if in  line 1 of CSV
        self.hfn       = None  #List of ascii converter functions eg t, i f)
        self.hdt       = None  #list of SQL types for each keyword
        self.tableName = None # name of the SQL table 

    def check(self):
        # Check that the required data items are set up consisentlu
        #shlog.normal("self.columns: %s" % self.columns)
        #shlog.normal("self.hfn: %s" % self.hfn)
        #shlog.normal("self.hdt: %s" % self.hdt)
        #shlog.normal("self.tableName %s" % self.tableName)
        assert len(self.columns) == len(self.hfm)
        assert len(self.columns) == len(self.hdt) # Bail if we have made typoss
        assert self.tableName
        
    def mkTable (self, con):
        #make the schemas for the main database tables
        # the schema can be loaded with data from subsequent calls of this program.
        cur = con.cursor()
        columns = ["%s %s" % (name, dbtype) for (name, dbtype) in zip (self.columns, self.hdt)]
        columns = (',').join(columns)
        create_statement = "create table "+ self.tableName + " (" + columns + ')'
        shlog.normal (create_statement)
        cur.execute(create_statement)
        con.commit()

        return

    def insert(self, con, rows):
        #insert rows of Ascii into the databse table
        #after applying conversion funcitons.
        insert_statement = (',').join(["?" for name in self.columns])
        insert_statement = "insert into " + self.tableName + "  values (" + insert_statement + ")"
        shlog.verbose (insert_statement)
        cur = con.cursor()
        for row in  rows:
            shlog.debug(row)
            #apply convertion functins
            r= ([f(item) for (item, f) in zip(row, self.hfm)])
            cur.execute(insert_statement, r ) 
        con.commit()


# record model ELEMENTS 
elementsTable = SQLTable()
elementsTable.tableName = "ELEMENTS"
elementsTable.columns = ['ID'  ,'Type','Name','Documentation']
elementsTable.hfm =     [     t,    t,      t,             t ]
elementsTable.hdt =     ['text','text','text',        'text' ]
elementsTable.check()

# record model relations 
relationsTable = SQLTable()
relationsTable.tableName = 'RELATIONS'
relationsTable.columns   =['ID'  ,'Type','Name','Documentation','Source','Target']
relationsTable.hfm       =[     t,     t,     t,              t,       t,       t]
relationsTable.hdt       =['text','text','text',         'text',   'text', 'text']
relationsTable.check()

# record all properties 
propertiesTable = SQLTable()
propertiesTable.tableName = 'PROPERTIES'
propertiesTable.columns   =[  'ID', 'Key','Value']
propertiesTable.hfm       =[     t,     t,     t ]
propertiesTable.hdt       =['text','text', 'text']
propertiesTable.check()

#record ingests
ingestTable = SQLTable()
ingestTable.tableName = 'INGESTs'
ingestTable.columns   =['Time','File','IngestType']
ingestTable.hfm       =[     t,    t,            t]
ingestTable.hdt       =['text', 'text',      'text']
ingestTable.check()

#Record ID's that have been ingested from CSV's to distinguich from those created.
ingestedTable = SQLTable()
ingestedTable.tableName = 'INGESTED'
ingestedTable.columns   =['Number','Type','Description']
ingestedTable.hfm       =[        t,     t,           t]
ingestedTable.hdt       =[   'text','text',      'text']
ingestedTable.check()

def q(args, sql):
    #a funnel routned for report queries, main benefit is query printing
    con = sqlite3.connect(args.dbfile)
    cur = con.cursor()
    shlog.verbose (sql)
    result  = cur.execute (sql)
    con.commit()
    return result



###################################################################
#
#  functions for time calculations -- SQLLITES can use ISO Datas
#
##################################################################


def iso_datetime(day,hour,offset_from_central_time=0):
    #convert mm/dd/yyyy to YYYY-MM-DD HH:MM:00.000
    dayhour =  day + ","  + hour
    shlog.debug(dayhour)
    #t = datetime.datetime.strptime(dayhour,"%m/%d/%Y,%I:%M %p %Z")
    t = datetime.datetime.strptime(dayhour,"%m/%d/%Y,%I:%M %p") + datetime.timedelta(hours = offset_from_central_time) 
    iso_datetime = datetime.datetime.isoformat(t)
    shlog.debug(iso_datetime)
    return iso_datetime

def iso_range(deltaDays, isoLatestDateTime=datetime.datetime.isoformat(datetime.datetime.now())):
    #return (latest, earliest) ISO date range. Latest data defaults to current time
    isoLatestDateTime = isoLatestDateTime.split('.')[0]
    t = datetime.datetime.strptime(isoLatestDateTime,"%Y-%m-%dT%H:%M:%S") + datetime.timedelta(days = -deltaDays)
    isoEarliestdatetime = datetime.datetime.isoformat(t)
    return (isoLatestDateTime, isoEarliestdatetime)


def iso_now():
    return datetime.datetime.isoformat(datetime.datetime.now())

###################################################################
#
#  functions clean and compare and ingest CSV files.
#
#  Only one pohe number is currently supported
#  Tr acquire files from the download area

##################################################################

VAULT_ROOT= "/Users/donaldp/archi_tool/cache"
DOWNLOAD_ROOT = "/Users/donaldp/export"

def csv_cleaned_rows(args, fn):
    # return rows stripped of headers and annotations, otherwise unaltered.
    # it turns out that cleaning both text and voice CSV's is the same code.
    shlog.normal ("about to open %s",fn)
    with open(fn) as fin:
        dr = csv.reader(fin)
        hdr = next(dr) # strip header
        
        # build row from csv and csv-constant information
        rows =[]
        for row in dr:
            if not row : continue  #skip blanks 
            if len(row) == 1 : continue #pesky line at end --  BRITTLE
            rows.append(row)
    return rows

def csv_info(args, fn):
    #return the number of rows and earliest of a CSV as a tuple 
    #
    # This allow for coparison and ingest of CSV for a tmobile accumupation period
    # in genreal we'd want to expunge the data of an older CSV when a newer one is available.
    rows = csv_cleaned_rows(args, fn)
    date = rows[-1][0]
    nrows = len(rows)
    return (nrows, date)


###################################################################
#
#  functions to make database state,  make tables, and ingest, DB info.
#
##################################################################

def mkdb (args):
    """Provide an empty database loaded with all schema""" 
    #make the schemas for the main database tables
    # the schema can be loaded with data from subsequent calls of this program.
    try:
        os.remove(args.dbfile)
        shlog.normal ("removed old database : %s" ,args.dbfile)
    except:
        pass
    con = sqlite3.connect(args.dbfile)
    shlog.normal ("created new database : %s" ,args.dbfile)
    elementsTable.mkTable(con)
    relationsTable.mkTable(con)
    propertiesTable.mkTable(con)
    ingestTable.mkTable(con)
    ingestedTable.mkTable(con)
    return

def ingest(args):
    """ Ingest items in the CVS_vault into databse tables """
    vault_files = os.path.join(VAULT_ROOT,"*.csv")
    shlog.normal("looking into vault for %s", vault_files)
    for v in glob.glob(vault_files):
        shlog.normal ("processing %s" % v)
        if "elements" in v :ingest_elements(args, v)
        elif "relations" in v :ingest_relations(args, v)
        elif "properties" in v :ingest_properties(args, v)
        else:
            shlog.error ("Cannot identify type of %s" % v)
            exit(1)
    
def ingest_elements(args, csvfile):
        shlog.normal ("about to open %s",csvfile)
        con = sqlite3.connect(args.dbfile)
        with open(csvfile) as fin:
            dr = csv.reader(fin)
            hdr = next(dr) # strip header
    
            # build row from csv and csv-constant information
            rows =[]
            for row in dr:
                if not row : continue  #skip blanks
                if len(row) == 1 : continue #pesky line at end --  BRITTLE
                rows.append(row)
            elementsTable.insert(con, rows)
            ingestTable.insert(con, [[iso_now(),csvfile,'CONTACTS']])
                
    
def ingest_relations(args, csvfile):
    shlog.normal ("about to open %s",csvfile)
    con = sqlite3.connect(args.dbfile)

    with open(csvfile) as fin:
        dr = csv.reader(fin)
        hdr = next(dr) # strip header
        
        # build row from csv and csv-constant information
        rows =[]
        for row in dr:
            if not row : continue  #skip blanks 
            if len(row) == 1 : continue #pesky line at end --  BRITTLE
            rows.append(row)
        relationsTable.insert(con, rows)
        ingestTable.insert(con, [[iso_now(),csvfile,'TEXTS']])

                 
def ingest_properties(args, csvfile):
    shlog.normal ("about to open %s",csvfile)
    con = sqlite3.connect(args.dbfile)

    with open(csvfile) as fin:
        dr = csv.reader(fin)
        hdr = next(dr) # strip header
        
        # build row from csv and csv-constant information
        rows =[]
        for row in dr:
            if not row : continue  #skip blanks 
            if len(row) == 1 : continue #pesky line at end --  BRITTLE
            rows.append(row)
        propertiesTable.insert(con, rows)
        ingestTable.insert(con, [[iso_now(),csvfile,'CALLS']])

    
###################################################################
#
#  reports
#
##################################################################

def dbinfo(args):
    """Print summary information about database content"""
    shlog.normal ("about to open %s",args.dbfile)
    l = []
    n_contacts   = "SELECT  count(*) FROM ELEMENTS"
    l.append (["Number of elements ",   q(args, n_contacts).fetchone()[0]])

    print (tabulate.tabulate(l,["Item","Value"]))
    
def list(args):
    """Dump a list of all TEXTS and CALLS Sorted by time """
    con = sqlite3.connect(args.dbfile)
    cur = con.cursor()
    q = "select * from ELEMENTS"
    shlog.normal(q)
    rows=[]
    for c in cur.execute (q): rows.append(c)
    print (tabulate.tabulate(rows))



        
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


def debug(args):
      import subprocess
      subprocess.call("/Applications/Archi.app/Contents/MacOS/Archi -console", shell=True,
                      stdout=sys.stdout, stdin=sys.stdin, stderr=sys.stderr)

            
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
    #Subcommand  to ingest csv to sqlite3 db file 
    mkdb_parser = subparsers.add_parser('mkdb', help=mkdb.__doc__)
    mkdb_parser.set_defaults(func=mkdb)
    mkdb_parser.add_argument("--force", "-f", help="remove existing db file of the same name", default=False, action='store_true')

    
    #Subcommand  to ingest csv to sqlite3 db file 
    ingest_parser = subparsers.add_parser('ingest', help=ingest.__doc__)
    ingest_parser.set_defaults(func=ingest)
    #ingest_parser.add_argument("csvfile")

    list_parser = subparsers.add_parser('list', help=list.__doc__)
    list_parser.set_defaults(func=list)
    list_parser.add_argument(   "--chr", "-c", help='Chromosome Numbers' , default='1')

    
    dbinfo_parser = subparsers.add_parser('dbinfo', help=dbinfo.__doc__)
    dbinfo_parser.set_defaults(func=dbinfo)

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

    #Subcommand  make an emty archiamte v1 databse.
    debug_parser = subparsers.add_parser('debug', help="debug.__doc__")
    debug_parser.set_defaults(func=debug)
    #debug_parser.add_argument("dbfile", help="name of databse file")

    
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
