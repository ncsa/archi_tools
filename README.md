Archi_tool is a set of scripts to load information from
an archimate model resideing in the archi_tool.

The tool makes a working databse from an archimate model,
and extends that.   Gols:

- Various reports can be produced and used in day to day management tasks.
- Logical Architecture transfer  to a configuration managment tool.
- Component model to feed a financial managemetn tool.
- Component model for a first cut work breakdown structure.
- Component model for fault trees and other material.

Software Configuration stuff.
============================
The software is in an early state. Early users
are managers using macs. Since 2.7 is shipped with
the current macos, The primary version of python
used is 2.7, Efforts are made to accomidate python 3,
but testing is not normally done on python 3.

Also, efforts are current made to package all the
underpinnings as copied into the archi_tool pacakge. 

At the current level of development the archi_tool softeare is
run from the directory holding the software.  Archi_tool software
is distributed via git as follows:

# Make an initial  archi_tool directory a filled with archi_tool stuff.
$ git clone https://github.com/ncsa/archi_tools.git

#update an archi_tool directory with new stuff.
git pull origin master

Runtime Configuration stuff.
============================
Archi_tool allows for worin with several archimate modles.  Each
model is denoted by a prefix. By convention  this is a string
of capital letters followed by an underscore.  DES_  and LSST_ are
examples of conventionally formed prefixes.

Archi_tool uses the prefix to identify data files assocaited with a
model.   Current conventions are:

1 - a sqlite databse is created in the current working directory,
named. <prefix>archi_tool.db, for example DEMAND_archi_tool.db
for the DEMAND_ prefix.

2 - Underneath a sub-directory named cache in the current working  directory,
archtool caches  CSV export. Conventionally, these files are given the
prefix qwhen exported from archimate in an export direcory

# cd archi_tool
$ls cache/DEMAND_/
DEMAND_elements.csv     DEMAND_properties.csv   DEMAND_relations.csv

Finally (and not regular w.r.t the overall deisgn pattern you need to know
where the archimate file corresponign to the .csv files are.  This is known to be not good,  and woudl be addressed in a future upgrade.

Getting to a useable database.
==============================

<enough for now)

The primary functions implemented in teh tool are:

1) acquire -- loads .csv files exported by archi into a cache
directory. for subsequent use.

2) mkdb -- makes an empty sqllite database

3) Ingests the .csv files into analogous databse tables and genrated
extra tabels that are useful for toolchains and reporting.

The extra tables are build on assumtions about the  modeling
methodologies and conventions used.

Modeling Conventions supported.
===============================
-The archimate ApplicationComponent is used to represent a service
-Services talk to Services via an ApplicationInterface.
-Services realize a requirement via the RealizationRelationship
-A Requirement may have sub-requirements via CompositionRelationship

Database Tables
===============

  CREATE TABLE ELEMENTS (ID text,Type text,Name text,Documentation text);
  CREATE TABLE RELATIONS (ID text,Type text,Name text,Documentation text,Source text,Target text);
  CREATE TABLE PROPERTIES (ID text,Key text,Value text);
  CREATE TABLE INGESTS (Time text,File text,IngestType text);
  CREATE TABLE INGESTED (Number text,Type text,Description text);
  CREATE TABLE requirements(
    Reference_name TEXT,
    Reference_id TEXT,
    Detail_name TEXT,
    Detail_id TEXT
   );

  CREATE TABLE Serving(
    Served_Name TEXT,     -- the supporting service name
    Served_ID TEXT,       -- the GUID of the supporting service
    Serving_name TEXT,    -- the relying serice
    Serving_ID TEXT       -- tre ID GUID of the relyign service.
 );
                


Supplimentary function provide information about teh database and ingest.


