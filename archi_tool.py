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

def t(x):return x
def i(x):return int(x)
def r(x):return float(x)

class SQLTable:
    "lightweight support for database tables"
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
        shlog.normal ("create database table : %s" ,args.dbfile)
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
            shlog.debug("insert: %s" % row)
            #apply convertion functins
            r= ([f(item) for (item, f) in zip(row, self.hfm)])
            cur.execute(insert_statement, r ) 
        con.commit()

# Record Summmary inforation from top of CSVfile.
elementsTable = SQLTable()
elementsTable.tableName = "ELEMENTS"
elementsTable.columns = [  "ID","Type", "Name","Documentation"]
elementsTable.hfm =     [     t,     t,      t,              t]
elementsTable.hdt =     ['text','text', 'text',         'text']
elementsTable.check()


#record INgest of each CSV
ingestTable = SQLTable()
ingestTable.tableName = "INGEST"
ingestTable.columns = ['IngestTime', 'File', 'IntoTable']
ingestTable.hfm =     [           t,       t,          t]
ingestTable.hdt =     [      'text',  'text',     'text']
ingestTable.check()

#Properties table
propertiesTable = SQLTable()
propertiesTable.tableName = "PROPERTIES"
propertiesTable.columns = [  'ID','Key','Value']
propertiesTable.hfm =     [     t,    t,      t]
propertiesTable.hdt =     ['text','text','text']
propertiesTable.check()


#Relations table
relationsTable = SQLTable()
relationsTable.tableName = "RELATIONS"
relationsTable.columns = ['ID'  ,'Type','Name','Documentation','Source','Target']
relationsTable.hfm =     [     t,     t,     t,              t,       t,       t]
relationsTable.hdt =     ['text','text','text',         'text',  'text',  'text']
relationsTable.check()

def q(args, sql):
    "common query (allows for logging)"
    con = sqlite3.connect(args.dbfile)
    cur = con.cursor()
    shlog.verbose (sql)
    result  = cur.execute (sql)
    return result

###################################################################
#
#  functions for time calculations
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
#  Functions clean and compare and ingest CSV files.
#
#  Acquire files from the download area
##################################################################

VAULT_ROOT= "/Users/donaldp/archi_tool/model_vault"
DOWNLOAD_ROOT = "/Users/donaldp/export"


def acquire(args):
    import re
    # acquire files from the download area into the vault.
    # Replace sucesive generations of CSV for epochs of reporting.
    # a CSV that is larger than the one in the vault is presumed to be newer
    csvs = ["elements.csv", "properties.csv","relations.csv"]
    for c in csvs:
        filename = args.prefix + c
        download_path = os.path.join(DOWNLOAD_ROOT,filename)
        vault_path = os.path.join(VAULT_ROOT,filename)
        shlog.normal ("mv %s to %s", download_path, vault_path)
        os.rename(download_path, vault_path)

def vault_info(args, date, fn):
    path = os.path.join(VAULT_ROOT, date, fn)
    exists = os.path.isfile(path)
    return (path, exists)

def vault_ingest(args, path, date, fn):
    # ingest file 
    path = os.path.join(VAULT_ROOT, date, fn)


###################################################################
#
#  functions to make database state,  make tables, and ingest, DB info.
#
##################################################################

def mkdb (args):
    #make the schemas for the main database tables
    # the schema can be loaded with data from subsequent calls of this program.
    if args.force:
        try:
            os.remove(args.dbfile)
            shlog.normal ("removed : %s" ,args.dbfile)

        except:
            pass
    shlog.normal ("create database : %s" ,args.dbfile)
    con = sqlite3.connect(args.dbfile)
    elementsTable.mkTable(con)
    relationsTable.mkTable(con)
    propertiesTable.mkTable(con)
    ingestTable.mkTable(con)
    return

def ingest(args):
    # ingest everyting in the vault.
    # LIkely best preceeding a mkdb
    vault_files = os.path.join(VAULT_ROOT,"*.csv")
    shlog.normal("looking into vault for %s", vault_files)
    for v in glob.glob(vault_files):
        shlog.normal ("processing %s" % v)
        if "nebula" in v :ingest_usage(args, v)
        else:
            shlog.error ("Cannot identify type of %s" % v)
            exit(1)

def ingest_usage(args, csvfile):
    shlog.normal ("about to open for summary %s",csvfile)
    con = sqlite3.connect(args.dbfile)

    row = []
    with open(csvfile) as fin:
        dr = csv.reader(fin)
        (text, BeginTime, EndTime)     = next(dr)
        row.append(BeginTime)
        row.append(EndTime)

        next(dr) #drop this uuid
         
        (text, VCPUHours)              = next(dr)
        row.append(VCPUHours)
        
        (text, ActiveRamMB)            = next(dr)
        row.append(ActiveRamMB)
        
        (text, TotalMemoryUsageHours)  = next(dr)
        row.append(TotalMemoryUsageHours)
        
        (text, TotalDiskGB)           = next(dr)
        row.append(TotalDiskGB)
        
        (text, TotalDiskUsageHours)    = next(dr)
        row.append(TotalDiskUsageHours)
        
        hdr = next(dr) # strip header
        hdr = next(dr) # strip header

        summaryTable.insert(con, [row])
        ingestTable.insert(con, [[iso_now(),csvfile,'SUMMARY']])

        instances = []
        for row in dr:
            sql_row = [EndTime]
            for r in row : sql_row.append(r)
            shlog.debug("one instance: %s",sql_row)
            instances.append(sql_row)
        instanceTable.insert(con, instances)
        ingestTable.insert(con, [[iso_now(),csvfile,'INSTANCES']])
            

    
###################################################################
#
#  reports
#
##################################################################

def dbinfo(args):
    shlog.normal ("about to open %s",args.dbfile)
    l = []
    earliest_csv = "SELECT  EndTime FROM SUMMARY ORDER BY EndTime ASC  LIMIT 1"
    l.append (["Earliest Sample", q(args, earliest_csv).fetchone()[0]])

    latest_csv   = "SELECT  EndTime FROM SUMMARY ORDER BY EndTime DESC LIMIT 1"
    l.append (["Latest Sample",   q(args, latest_csv  ).fetchone()[0]])

    print tabulate.tabulate(l,["Item","Value"])
    
def list(args):
    # Dump signigifact tables (what's in the DB) 
    con = sqlite3.connect(args.dbfile)
    cur = con.cursor()
    q = "select * from SUMMARY"
    rows=[]
    for c in cur.execute (q): rows.append(c)
    print tabulate.tabulate(rows)
    q = "select * from INSTANCE"
    rows=[]
    for c in cur.execute (q): rows.append(c)
    print tabulate.tabulate(rows)



def state(args):
    # Print a report summary report for each state
    body = "MeasureTime,state,count(*),sum(VCPU),sum(RamMB),sum(DiskGB),sum(UsageHours)"
    #for s in ["Active","Error","Stopped"]:
    sql = "select %s from INSTANCE Group by MeasureTime, State Order by MeasureTime, State" % (body)
    answer =(q(args, sql))
    print tabulate.tabulate(answer, body.split(','))

    
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
    

    #Subcommand  to ingest csv to sqlite3 db file 
    mkdb_parser = subparsers.add_parser('mkdb', help="make a new, empty database")
    mkdb_parser.set_defaults(func=mkdb)
    mkdb_parser.add_argument("--force", "-f", help="remove existing db file of the same name", default=False, action='store_true')

    
    #Subcommand  to ingest csv to sqlite3 db file 
    ingest_parser = subparsers.add_parser('ingest', help="ingest CSV into database")
    ingest_parser.set_defaults(func=ingest)
    #ingest_parser.add_argument("csvfile")

    list_parser = subparsers.add_parser('list', help="List the context of the database")
    list_parser.set_defaults(func=list)
    list_parser.add_argument(   "--chr", "-c", help='Chromosome Numbers' , default='1')

    state_parser = subparsers.add_parser('state', help="summary report for machines in various states")
    state_parser.set_defaults(func=state)
    state_parser.add_argument(   "--nstates", "-n", help='N state' , type=int, default=15)
    state_parser.add_argument(   "--after",   "-s", help='after N days '     , type=int, default=1000)

    dbinfo_parser = subparsers.add_parser('dbinfo', help="print database summary info")
    dbinfo_parser.set_defaults(func=dbinfo)

    acquire_parser = subparsers.add_parser('acquire', help="Acquire CSVs from download area into the vault")
    acquire_parser.set_defaults(func=acquire)
    #acquire_parser.add_argument("--noaction", "-n", help="just say what would be done, don't do it", default=False, action='store_true')
    acquire_parser.add_argument("--prefix", "-p", help="Prefix given on archimate export", default="Study1_")

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
