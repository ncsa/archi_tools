Archi_tool is a set of scripts to load information from
an archimate model resideing in the archi_tool.

The tool makes a working databse from an archimate model,
and extends that.   Gols:

- Various reports can be produced and used in day to day management tasks.
- Logical Architecture transfer  to a configuration managment tool.
- Component model to feed a financial managemetn tool.
- Component model for a first cut work breakdown structure.
- Component model for fault trees and other material.

Installation
============

Software Installation stuff.
----------------------------
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

--  Make an initial  archi_tool directory a filled with archi_tool stuff.
$ git clone https://github.com/ncsa/archi_tools.git

--update an archi_tool directory with new stuff.
$git pull origin master

Runtime Conventions
-------------------
Archi_tool allows for working with several archimate models.  Each
model is denoted by a prefix. By convention, this is a string
of capital letters followed by an underscore.  DES_  and LSST_ are
examples of conventionally formed prefixes.

Archi_tool uses the prefix to aquire, cache and identify data files
associated with a model.   Current conventions are:

0- Current working directory is the archi_tools directory produced
by the *git clone*.

1- a sqlite database is created in the current working directory,
named. <prefix>archi_tool.db, for example DEMAND_archi_tool.db
for the DEMAND_ prefix.

2- sub-directory named cache in the current working  directory,
caches of an archimate CSV export. Conventionally, you would export these
csv files in $HOME/export, e.g an export directory in your home area.  The

$archi_tool aquire

command moves these these files into the appropriate cache directory.
to obtain stable inputs for downstream tool chains.

# cd archi_tool
$ls cache/DEMAND_/
DEMAND_elements.csv     DEMAND_properties.csv   DEMAND_relations.csv

Finally (and not regular w.r.t the overall deisgn pattern you need to know
where the archimate file corresponding to the .csv files are.

oll of this is not a good practive but is where the software is.

Getting to a useable database.
==============================

Having done the above steps of export and acquire

$ ./archi_tool -p mkdb   #deletes prior database and makes a new, empty db
$ ./archi_tool -p ingest #Ingest csvs into the data and makes supplimental info
$ ./ldm -p xxx_yyy  --ingest file.archimate  # ingest information about folders

The extra tables are build on assumtions about the  modeling
methodologies and conventions used.

Modeling Conventions supported.
-------------------------------

need prose here.

Reporting
---------

Provides with archi_tool is a small python pacakge, called reports.py.

(document this)