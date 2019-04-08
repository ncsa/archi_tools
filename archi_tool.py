#!/usr/bin/env python
"""
Enable reporting and use of archimate data by Load an archimate
csv export into a SQLLITE database.

Archimate CSV exports consist of three csv files placed into
an Export area. the CSV's are prefined with an arbitraty prefiix
(e.g DES_") that is specified within archimate when exporting.

This tool suports
- Acquiring the csv export in a cached  diretory specific
to the export prefix,
- Ingesting the csv files  into a sqliite database specific
to the export prefix.
- Dervice some tables in the database to faciltate the reporting
and tool chain use.
- Produce a variety of reports.


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
import archi_interface
import conventions

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
elementsTable.columns = ['ID'  ,'Type','Name','Documentation','ParentFolder']
elementsTable.hfm =     [     t,    t,      t,             t,              t]
elementsTable.hdt =     ['text','text','text',        'text',         'text']
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
ingestTable.tableName = 'INGESTS'
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

#Record ID's that have been folder from CSV's to distinguich from those created.
folderTable = SQLTable()
folderTable.tableName = 'FOLDER'
folderTable.columns   =['Id'  ,'Parent_id'  ,'Type','Name','Documentation','Depth']
folderTable.hfm       =[     t,            t,     t,     t,              t,      t]
folderTable.hdt       =['text',       'text','text','text',         'text', 'text']
folderTable.check()

#Record ID's that have been dual from CSV's to distinguich from those created.
dualTable = SQLTable()
dualTable.tableName = 'DUAL'
dualTable.columns   =['Dummy']
dualTable.hfm       =[     t ]
dualTable.hdt       =['text']
dualTable.check()

#Record ID's that have been folder from CSV's to distinguich from those created.
viewsTable = SQLTable()
viewsTable.tableName = 'VIEWS'
viewsTable.columns   =['Id'  ,'Type'  ,'Name','Documentation','Viewpoint','Parent_folder_id']
viewsTable.hfm       =[     t,       t,     t,              t,          t,                 t]
viewsTable.hdt       =['text',  'text','text',         'text',     'text',            'text']
viewsTable.check()

#Record ID's that have been folder from CSV's to distinguich from those created.
viewobjectsTable = SQLTable()
viewobjectsTable.tableName = 'VIEW_OBJECTS'
viewobjectsTable.columns   =['View_id','Object_id','Class', 'Name', 'Content']
viewobjectsTable.hfm       =[        t,          t,      t,      t,         t]
viewobjectsTable.hdt       =['text'   ,     'text', 'text', 'text',    'text']
viewobjectsTable.check()

#Record ID's that have been folder from CSV's to distinguich from those created.
connectionsTable = SQLTable()
connectionsTable.tableName = 'CONNECTIONS'
connectionsTable.columns   =['connection_id','view_id','relationship_id']
connectionsTable.hfm       =[              t,         t,               t]
connectionsTable.hdt       =['text'         ,    'text',          'text']
connectionsTable.check()

# this is the Enclave tbale
enclaveTable = SQLTable()
enclaveTable.tableName = 'ENCLAVES'
enclaveTable.columns   =['Id'  ,'Name','Documentation', 'Location']
enclaveTable.hfm       =[     t,     t,              t,          t]
enclaveTable.hdt       =['text','text',         'text',     'text']
enclaveTable.check()

def q(args, sql):
    #a funnel routned for report queries, main benefit is query printing
    con = sqlite3.connect(args.dbfile)
    con.text_factory = lambda x: x.decode("utf-8")
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
    folderTable.mkTable(con)
    viewsTable.mkTable(con)
    viewobjectsTable.mkTable(con)
    connectionsTable.mkTable(con)
    enclaveTable.mkTable(con)
    dualTable.mkTable(con)
    q(args,"insert into dual values ('X')")
    return

def ingest(args):
    """ Ingest items in the CVS_vault into databse tables """
    vault_files = os.path.join(archi_interface.cachepath(args), "*.sqlite")
    shlog.normal("looking into vault for %s", vault_files)
    for v in glob.glob(vault_files):
        shlog.normal ("processing %s" % v)
        ingest_elements(args, v)
        ingest_relations(args, v)
        ingest_properties(args, v)
        ingest_folders(args, v)
        ingest_views(args, v)
        ingest_view_objects(args, v)
        ingest_connections(args, v)
        ingest_enclaves(args, v)
        # else:
        #     shlog.error ("Cannot identify type of %s" % v)
        #     exit(1)
            
    #make tables from other modules
    conventions.mkTables(args)  #modeling conventions
        
def ingest_elements(args, sqldbfile):
        shlog.normal ("about to open %s",sqldbfile)
        con = sqlite3.connect(args.dbfile)
        con_temp = sqlite3.connect(sqldbfile)
        c_temp = con_temp.cursor()
        # the ingest_elements query retrieves relevant elements from the archidump database
        sql = """/*Retrieve id and the most recent version of a model matched by name*/
                 /*desired_model should return one single row*/
                 WITH desired_model(id, version, created_on) AS (SELECT id, version, max(created_on) FROM models m WHERE m.name='%s' GROUP BY id),
                 /*Model stores all elements that ever existed in all the models, regardless of they exist in the recent versions*/
				 /*That's why we retrieve elements that match the model id+model version from desired_model*/
				 desired_model_elements(element_id, element_version, parent_folder_id) AS (SELECT element_id, element_version, parent_folder_id
                 FROM elements_in_model eim
                 INNER JOIN desired_model dm on dm.version=eim.model_version AND dm.id=eim.model_id)
                 /*With the correct element ids+versions identified, we can retrieve the matches from the elements table that has all the properties*/
				 SELECT e.id, e.class as Type, e.name, e.documentation, dme.parent_folder_id as ParentFolder
                 FROM elements e
                 INNER JOIN desired_model_elements dme on dme.element_id=e.id AND dme.element_version=e.version
                 """ % args.prefix
        shlog.verbose(sql)
        c_temp.execute(sql)
        rows = c_temp.fetchall()

        elementsTable.insert(con, rows)
        ingestTable.insert(con, [[iso_now(),sqldbfile,'ELEMENTS']])
        con_temp.close()
                
    
def ingest_relations(args, sqldbfile):
    shlog.normal ("about to open %s",sqldbfile)
    con = sqlite3.connect(args.dbfile)
    con_temp = sqlite3.connect(sqldbfile)
    c_temp = con_temp.cursor()
    # the ingest_relations query retrieves relevant relations from the archidump database
    sql = """/*Retrieve id and the most recent version of a model matched by name*/
             /*desired_model should return one single row*/
             WITH desired_model(id, version, created_on) AS (SELECT id, version, max(created_on) FROM models m WHERE m.name='%s' GROUP BY id),
             /*Model stores all relations that ever existed in all the models, regardless of they exist in the recent versions*/
			 /*That's why we retrieve relations that match the model id+model version from desired_model*/
             desired_model_relations(relationship_id, relationship_version) AS (SELECT relationship_id, relationship_version
             FROM relationships_in_model rim
             INNER JOIN desired_model dm on dm.version=rim.model_version AND dm.id=rim.model_id
             /* Hotfix: remove relationship_id not found in views */
			 WHERE relationship_id in (SELECT DISTINCT relationship_id FROM views_connections))
             /*With the correct relations ids+versions identified, we can retrieve the matches from the relations table that has all the properties*/
             SELECT r.id, r.class as Type, r.name, r.documentation, r.source_id as source, r.target_id as Target
             FROM relationships r
             INNER JOIN desired_model_relations dmr on dmr.relationship_id=r.id AND dmr.relationship_version=r.version
             """ % args.prefix
    shlog.verbose(sql)
    c_temp.execute(sql)
    rows = c_temp.fetchall()
    relationsTable.insert(con, rows)
    ingestTable.insert(con, [[iso_now(),sqldbfile,'RELATIONS']])

                 
def ingest_properties(args, sqldbfile):
    shlog.normal ("about to open %s",sqldbfile)
    con = sqlite3.connect(args.dbfile)
    con_temp = sqlite3.connect(sqldbfile)
    c_temp = con_temp.cursor()
    # the ingest_properties query retrieves properties from the archidump database
    sql = """/*Retrieve the most recent versions of all properties*/
             /*Properties for elements and folder that no longer exist will not be retrieved in report queries as long as INNER JOIN is used*/
             WITH properties_prep(parent_ID, name, max_parent_version) as (SELECT parent_ID, name, max(parent_version) as max_parent_version
             FROM properties
             GROUP BY parent_ID)
             SELECT pp.parent_ID, pp.name, p.value
             FROM properties p
			 INNER JOIN properties_prep pp on pp.max_parent_version = p.parent_version and pp.name=p.name and pp.parent_id = p.parent_id
             """
    shlog.verbose(sql)
    c_temp.execute(sql)
    rows = c_temp.fetchall()
    propertiesTable.insert(con, rows)
    ingestTable.insert(con, [[iso_now(),sqldbfile,'PROPERTIES']])

def ingest_folders(args, sqldbfile):
    shlog.normal ("about to open %s",sqldbfile)
    con = sqlite3.connect(args.dbfile)
    con_temp = sqlite3.connect(sqldbfile)
    c_temp = con_temp.cursor()
    # the ingest_folders query retrieves relevant folders from the archidump database
    sql = """/*Retrieve id and the most recent version of a model matched by name*/
             /*desired_model should return one single row*/
             WITH desired_model(id, version, created_on) AS (SELECT id, version, max(created_on) FROM models m WHERE m.name='%s' GROUP BY id),
             
             /*Model stores all folders that ever existed in all the models, regardless of they exist in the recent versions*/
			 /*That's why we folders elements that match the model id+model version from desired_model*/
			 /*In addition, a folder CTE is needed for looped joins*/
             allfolders(id, parent_id, type, Name, Documentation) AS (SELECT folder_id as id, parent_folder_id as parent_id, type, Name, Documentation
             FROM folders_in_model fim
             INNER JOIN desired_model dm on dm.version=fim.model_version AND dm.id=fim.model_id
			 INNER JOIN folders f on f.id=fim.folder_id AND f.version=fim.folder_version),
			 
             /*Assign depth levels in a recursive CTE*/
             depths(id, name, depth) AS (
             SELECT id, Name, type as depth
             FROM allfolders
             WHERE parent_id IS NULL
             
             UNION ALL
                    
             SELECT allfolders.id, allfolders.Name, cast(depths.depth as text)|| ' >' || cast(allfolders.name as text) as depth
             FROM allfolders
             JOIN depths ON allfolders.parent_id = depths.id
             ) 
             /*Return contents of the recursive CTE*/
             SELECT af.id, af.parent_id, af.type, af.Name, af.Documentation, d.depth
             FROM allfolders as af
             INNER JOIN depths as d on d.id=af.id
             """ % args.prefix
    shlog.verbose(sql)
    c_temp.execute(sql)
    rows = c_temp.fetchall()
    folderTable.insert(con, rows)
    ingestTable.insert(con, [[iso_now(),sqldbfile,'FOLDER']])

def ingest_views(args, sqldbfile):
    shlog.normal ("about to open %s",sqldbfile)
    con = sqlite3.connect(args.dbfile)
    con_temp = sqlite3.connect(sqldbfile)
    c_temp = con_temp.cursor()
    # the ingest_properties query retrieves properties from the archidump database
    sql = """/*Retrieve id and the most recent version of a model matched by name*/
             /*desired_model should return one single row*/
             WITH desired_model(id, version, created_on) AS (SELECT id, version, max(created_on) FROM models m WHERE m.name='%s' GROUP BY id),
             /*Model stores all views that ever existed in all the models, regardless of they exist in the recent versions*/
             /*That's why we retrieve the views that match the model id+model version from desired_model*/
             desired_views(view_id, view_version, parent_folder_id) AS (SELECT view_id, view_version, parent_folder_id
             FROM views_in_model vim
             INNER JOIN desired_model dm on dm.version=vim.model_version AND dm.id=vim.model_id)
             /*With the correct view ids+versions identified, we can retrieve the matches from the relations table that has all the properties*/
             SELECT v.id, v.class as Type, v.name, v.documentation, v.viewpoint, dvo.parent_folder_id
             FROM views v
             INNER JOIN desired_views dvo on dvo.view_id=v.id AND dvo.view_version=v.version
             """ % args.prefix
    shlog.verbose(sql)
    c_temp.execute(sql)
    rows = c_temp.fetchall()
    viewsTable.insert(con, rows)
    ingestTable.insert(con, [[iso_now(),sqldbfile,'VIEWS']])

def ingest_view_objects(args, sqldbfile):
    shlog.normal ("about to open %s",sqldbfile)
    con = sqlite3.connect(args.dbfile)
    con_temp = sqlite3.connect(sqldbfile)
    c_temp = con_temp.cursor()
    # the ingest_properties query retrieves properties from the archidump database
    sql = """/*Retrieve id and the most recent version of a model matched by name*/
             /*desired_model should return one single row*/
             WITH desired_model(id, version, created_on) AS (SELECT id, version, max(created_on) FROM models m WHERE m.name='%s' GROUP BY id),
             /*Model stores all objects that ever existed in all the models, regardless of they exist in the recent versions*/
             /*That's why we retrieve the view objects that match the model id+model version from desired_model*/
             desired_views(view_id, view_version) AS (SELECT view_id, view_version
             FROM views_in_model vim
             INNER JOIN desired_model dm on dm.version=vim.model_version AND dm.id=vim.model_id),
             /*objects are versioned as well, so we get their ids too*/
             objects_in_view(view_id, view_version, object_id, object_version) AS (SELECT DISTINCT dv.view_id, dv.view_version, voiv.object_id, voiv.object_version
             FROM desired_views dv
             INNER JOIN views_objects_in_view voiv on voiv.view_id=dv.view_id AND voiv.view_version=dv.view_version
             )
             /*With the correct view object ids+versions identified, we can retrieve the matches from the views_objects table that has all the properties*/
             SELECT oiv.view_id, vo.element_id, vo.class, vo.name, vo.content
             FROM objects_in_view oiv
             INNER JOIN views_objects vo on vo.container_id=oiv.view_id AND vo.id=oiv.object_id AND vo.version=oiv.object_version
             """ % args.prefix
    shlog.verbose(sql)
    c_temp.execute(sql)
    rows = c_temp.fetchall()
    viewobjectsTable.insert(con, rows)
    ingestTable.insert(con, [[iso_now(),sqldbfile,'VIEW_OBJECTS']])


def ingest_connections(args, sqldbfile):
    shlog.normal ("about to open %s",sqldbfile)
    con = sqlite3.connect(args.dbfile)
    con_temp = sqlite3.connect(sqldbfile)
    c_temp = con_temp.cursor()
    # the ingest_properties query retrieves properties from the archidump database
    sql = """/*Retrieve id and the most recent version of a model matched by name*/
             /*desired_model should return one single row*/
             WITH desired_model(id, version, created_on) AS (SELECT id, version, max(created_on) FROM models m WHERE m.name='%s' GROUP BY id),
             /*Model stores all views that ever existed in all the models, regardless of they exist in the recent versions*/
             /*That's why we retrieve the views that match the model id+model version from desired_model*/
             desired_views(view_id, view_version, parent_folder_id) AS (SELECT view_id, view_version, parent_folder_id
             FROM views_in_model vim
             INNER JOIN desired_model dm on dm.version=vim.model_version AND dm.id=vim.model_id),
			 /* Now that we have the most recent view versions from the most recent model, we can get the most recent connections */
			 desired_connections(connection_id, connection_version, view_version, view_id) AS (SELECT DISTINCT vciv.connection_id, vciv.connection_version, vciv.view_version, vciv.view_id 
			 FROM desired_views dv
			 INNER JOIN views_connections_in_view vciv on vciv.view_id = dv.view_id AND vciv.view_version = dv.view_version)
			 SELECT vc.id as connection_id, dc.view_id, vc.relationship_id
			 FROM views_connections vc
			 INNER JOIN desired_connections dc on vc.id=dc.connection_id AND vc.version = dc.connection_version""" % args.prefix
    shlog.verbose(sql)
    c_temp.execute(sql)
    rows = c_temp.fetchall()
    connectionsTable.insert(con, rows)
    ingestTable.insert(con, [[iso_now(),sqldbfile,'CONNECTIONS']])


def ingest_enclaves(args, sqldbfile):
    shlog.normal ("about to open %s",args.dbfile)
    con = sqlite3.connect(args.dbfile)
    # note: ingest_enclaves connects to the same DB for source and output data
    con_temp = sqlite3.connect(args.dbfile)
    c_temp = con_temp.cursor()
    # the ingest_properties query retrieves properties from the archidump database
    sql = """SELECT DISTINCT e.Id, e.Name, e.Documentation, e1.Name as Location
          /* Get all groupings  from the Enclave FOLDER*/
          FROM FOLDER f
          INNER JOIN ELEMENTS  e on e.ParentFolder = f.Id and e.Type = 'Grouping'
          /* Get all locations by linking relations and then elements again*/
          INNER JOIN RELATIONS r on r.Target = e.Id
          INNER JOIN ELEMENTS e1 on e1.ID = r.Source
          WHERE f.Name = 'Enclaves' AND e1.Type = 'Location'"""
    shlog.verbose(sql)
    c_temp.execute(sql)
    rows = c_temp.fetchall()
    enclaveTable.insert(con, rows)
    ingestTable.insert(con, [[iso_now(),args.dbfile,'ENCLAVES']])
    
###################################################################
#
#  reports
#
##################################################################

def dbinfo(args):
    """Print summary information about database content"""
    shlog.normal ("about to open %s",args.dbfile)
    l = []
    sqls = [
        ["Number of Elements"  ,"Select count(*) from ELEMENTS"],
        ["Number of Relations" ,"Select count(*) from RELATIONS"],
        ["Number of Properties","Select count(*) from PROPERTIES"],
        ]
    for item, sql in sqls:
        l.append ([item,   q(args, sql).fetchone()[0]])

    # now ingest infor from CSV's
    sql = "Select * from INGESTS"
    for result in q(args, sql):
        l.append(["sqlite",result])

    print (tabulate.tabulate(l,["Item","Value"]))

def list(args):
    """ """
    con = sqlite3.connect(args.dbfile)
    cur = con.cursor()
    q = "select * from ELEMENTS"
    shlog.normal(q)
    rows=[]
    for c in cur.execute (q): rows.append(c)
    print (tabulate.tabulate(rows))


def like(args):
    """print Model elements with a name matching an SQL LIKE string"""
    sql = """select Id, Type, Name 
             from ELEMENTS where name  like '%s'
           """ % args.pattern
    l = []
    for (id, type, name) in q(args, sql):
        name = name.strip()
        l.append([type, name])
    print (tabulate.tabulate(l,["Type", "Name"]))

    
def modelinfo(args):
    """ Print summry content of the model -- to recall names etc."""
    
    sql = """select distinct Type, Count(Type)
             from ELEMENTS
             Group by Type Order by Type
           """
    print (tabulate.tabulate(q(args,sql),["Element Type","Count"]))

    sql = """select distinct Type, Count(Type)
             from RELATIONS
             group by Type Order by Type
           """
    print (tabulate.tabulate(q(args,sql),["Relation Type","Count"]))

    sql = """select distinct Key, Value, Count(Value)
             from PROPERTIES
             group by Key, Value Order by Key
           """
    print (tabulate.tabulate(q(args,sql),["Key","Value","Count"]))
     
        
def extend(args):
      """
      Extend an archimate CSV file for re-import by repliating a prototype line nappend times.

      Code UUID in ther prototype for elements for the cell to be ne a newly generated UUID
      """
      sqldbfile = open(args.csv, 'ab') 
      prototype = args.prototype.split(",")
      writer = csv.writer(sqldbfile, delimiter=',',
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
      sqldbfile = open(args.prefix + args.csvtype + ".csv", 'w')
      sqldbfile.write(hdr + '\n')
      sqldbfile.close()

###########################################################
#
# Main program
#
############################################################
      
            
if __name__ == "__main__":

    #main_parser = argparse.ArgumentParser(add_help=False)
    main_parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=argparse.RawDescriptionHelpFormatter)
    main_parser.add_argument('--loglevel','-l',
                             help='loglevel NONE, NORMAL, VERBOSE, VVERBOSE, DEBUG',
                             default="ERROR")
    
    main_parser.add_argument("--dbfile", "-d", default="archi_tool.db")
    main_parser.add_argument("--prefix", "-p", default="LSST_")
    main_parser.set_defaults(func=None) #if none then there are  subfunctions    
    subparsers = main_parser.add_subparsers(title="subcommands",
                       description='valid subcommands',
                       help='additional help')
    #Subcommand  to ingest csv to sqlite3 db file 
    mkdb_parser = subparsers.add_parser('mkdb', description=mkdb.__doc__)
    mkdb_parser.set_defaults(func=mkdb)
    mkdb_parser.add_argument("--force", "-f", help="remove existing db file of the same name", default=False, action='store_true')

    
    #Subcommand  to ingest csv to sqlite3 db file 
    ingest_parser = subparsers.add_parser('ingest', description=ingest.__doc__)
    ingest_parser.set_defaults(func=ingest)
    #ingest_parser.add_argument("sqldbfile")

    list_parser = subparsers.add_parser('list', description=list.__doc__)
    list_parser.set_defaults(func=list)
    list_parser.add_argument(   "--chr", "-c", help='Chromosome Numbers' , default='1')

    
    dbinfo_parser = subparsers.add_parser('dbinfo', description=dbinfo.__doc__)
    dbinfo_parser.set_defaults(func=dbinfo)

    # reasonably detailed list of model summary information
    modelinfo_parser = subparsers.add_parser('modelinfo', description=modelinfo.__doc__)
    modelinfo_parser.set_defaults(func=modelinfo)

    # reasonably detailed list of model summary information
    like_parser = subparsers.add_parser('like', description=like.__doc__)
    like_parser.set_defaults(func=like)
    like_parser.add_argument("pattern", help="SQL pattern for matching")

    #Subcommand  to extend a archimate-style CSV export file 
    # extend_parser = subparsers.add_parser('extend', description=extend.__doc__)
    # extend_parser.set_defaults(func=extend)
    # extend_parser.add_argument("csv", help="csv to append to")
    #extend_parser.add_argument("prototype", help="command list that is a protytype.  Use UUID for a new UUID")
    #extend_parser.add_argument("--nappends", "-n", help='Number of lines to append tofile ' , type=int, default=15)

    #Subcommand  make an archmate style empty (header only) CSV file
    # header_parser = subparsers.add_parser('header', description=header.__doc__)
    # header_parser.set_defaults(func=header)
    # header_parser.add_argument("csvtype", help="type of sqldbfile to make")

    archi_interface.parsers(subparsers)
    conventions.parsers(subparsers)

    args = main_parser.parse_args()

    # tag the dbfile with the prefix so that we can work on
    # various models without collision
    args.dbfile = args.prefix+ '_' +args.dbfile
    
    # translate text argument to log level.
    # least to most verbose FATAL WARN INFO DEBUG
    # level also printst things to the left of it. 
    loglevel=shlog.__dict__[args.loglevel]
    assert type(loglevel) == type(1)
    shlog.basicConfig(level=shlog.__dict__[args.loglevel])


    if not args.func:  # there are no subfunctions
        main_parser.print_help()
        exit(1)
    args.func(args)
