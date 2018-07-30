Archi_tool is a set of scripts to load information from
an archimate model int a sqlite databse, where the data
can hten be used to achieve the following goals::

- Produce  reports used in day to day management tasks.
- Logical Architecture transfer to aconfiguration management tool.
- Component model to feed a financial management tool.
- Component model for a first cut work breakdown structure.
- Component model for fault trees and other material.

*The tools is very much a work in progress, evolving weekly*

#Installation

##Software Installation stuff.

The software is in an early state. Early users
are managers using macs. Since 2.7 is shipped with
the current macos, The primary version of python
used is 2.7, Efforts are made to accommodate python 3,
but testing is not normally done on python 3.

Also, efforts are current made to package all the
underpinnings as copied into the archi_tool package.

However, you wil need to install the following packages

* xlsxwriter
* openpyxl
* lxml

At the current level of development the archi_tool software is
run from the directory holding the software.  Archi_tool software
is distributed via git as follows:

> #Make an initial  archi_tool directory a filled with archi_tool stuff.
> $ git clone https://github.com/ncsa/archi_tools.git

Update afro mthe current master.

> #update an archi_tool directory with new stuff.
> $git pull origin master

#Run-time Conventions

Archi_tool allows for working with several archimate models.  Each
model is denoted by a prefix. By convention, this is a string
of capital letters followed by an underscore.  DES_  and LSST_ are
examples of conventionally formed prefixes.

Archi_tool uses the prefix to acquire, cache and identify data files
associated with a model.   Current conventions are:

1. The eurrent working directory is the archi_tools directory produced
by the *git clone*.

1. Archi_tools corrently depends on Exporets of Archi .csv files. The
suported convention is to:
         1.  Export the CSV files into $HOME/Export
         1.  Export the files wiht a meaningful prefix, ending in an underscore, e.g. DES_

1. To provide a directory in the default directory named *cache*. Achi_tool copies working files there.

1. After suitable invocations of archi_tool, An sqlite database is created in the current working directory, named. <prefix>archi_tool.db, for example DEMAND_archi_tool.db
for the DEMAND_ prefix.

>
> $archi_tool -p <prefix> acquire  <archimate file>
>

moves the expoerted .csvfiles and the .archiment file  into the appropriate cache directory.
These files provide stable inputs for downstream tool chains.  IF you update achimate, and want the updates to propagate to the databse, you mush re-acquire the relevant files. 

> #example 
> $archi_tool -p DEMAND_ acquire  /usr/donaldp..../demand.archimate
> #cd archi_tool
> $ls cache/DEMAND_/
> DEMAND_elements.csv     DEMAND_properties.csv   DEMAND_relations.csv
> ingested.archimate

All of this is not a good practice but is where the software is.

#Getting to a usable database.

Having done the above steps of export and acquire

>  ./archi_tool -p DEMAND_ mkdb   #deletes prior database and makes a new, empty db
>  ./archi_tool -p DEMAND_ ingest #ingest csv into the data and makes supplemental info
>  ./ldm -p DEMAND  --ingest file.archimate #ingest information about folders

The extra tables are built on assumptions about the  modeling
methodologies and conventions used.  The -l flag 


#Reporting

reports.py is small python report generator provided with archi_tools.
An individual report is specified by coding a small python subroutine
which declares objects and relates them to a master object, and
returns the master object as the function returned.


(document this)