Archi_tool is a set of scripts to load information from
an archimate model  rsting in the archi_tool.

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


