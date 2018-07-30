Archi_tool is a set of scripts to load information from
an archimate model int a sqlite databse, where the data
can hten be used to achieve the following goals::

- Produce  reports used in day to day management tasks.
- Logical Architecture transfer to aconfiguration management tool.
- Component model to feed a financial management tool.
- Component model for a first cut work breakdown structure.
- Component model for fault trees and other material.

*The tools is very much a work in progress, evolving weekly*

Software Installation
=====================

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

```
#Make an initial  archi_tool directory a filled with archi_tool stuff.
$ git clone https://github.com/ncsa/archi_tools.git
```

Update from the current git master branch. 

```
#update an archi_tool directory with new stuff.
$git pull origin master
```

#Run-time Conventions

Archi_tool allows for working with several archimate models.  Each
model is denoted by a prefix. By convention, this is a string
of capital letters followed by an underscore.  DES_  and LSST_ are
examples of conventionally formed prefixes.

Archi_tool uses the prefix to acquire, cache and identify data files
associated with a model.   Current conventions are:

1. The current working directory is the archi_tools directory produced
by the *git clone*.

1. Archi_tools corrently depends on Exporets of Archi .csv files. The
suported convention is to:
         1.  Export the CSV files into $HOME/Export
         1.  Export the files wiht a meaningful prefix, ending in an underscore, e.g. DES_

1. To provide a directory in the default directory named *cache*. Achi_tool copies working files there.

1. After suitable invocations of archi_tool, An sqlite database is created in the current working directory, named. <prefix>archi_tool.db, for example DEMAND_archi_tool.db
for the DEMAND_ prefix.

```
$archi_tool -p <prefix> acquire  <archimate file>
```

moves the exported .csv files and the .archimate file into the cache
directory named by the prefix.  These files provide stable inputs for
downstream tool chains.  If you update achimate, and want the updates
to propagate to the databse, you mush re-acquire the relevant files.

```
#example 
#cd archi_tool get the stuff exported from archi
$ archi_tool -p DEMAND_ acquire  /usr/donaldp..../demand.archimate
# look at the files that were acquired
$ ls cache/DEMAND_ 
DEMAND_elements.csv     DEMAND_properties.csv   DEMAND_relations.csv
ingested.archimate
```

All of this is not a good practice but is where the software is.

#Getting to a usable database.

Having done the above steps of export and acquire
`
$ ./archi_tool -p DEMAND_ mkdb   #deletes prior database and makes a new, empty db
$ ./archi_tool -p DEMAND_ ingest #ingest csv into the data and makes supplemental info
$ ./ldm -p DEMAND  --ingest file.archimate #ingest information about folders
`
Extra tables are built on assumptions about the  modeling
methodologies and conventions used.  The currently supported
conventions are defiend and implemented in conventions.py 


# Heirarchical Report Generator

reports.py is small python report generator provided with archi_tools.
An individual report is specified by coding a small python subroutine
which declares objects and relates them to a master object, and
returns the master object as the function returned.



### StanzaFactory
A stanza defines a line in a report. A stanzaFactory is an object tha creates many stanzas base on SQL queries. In fact, A stanza is defined by three types of SQL queries.  All of these queries relate to a single subject.  A line about a particular subject may optionally be followed by a substanza  where each line contains inforamation about a different sort of subject.

The idea directories and files is an intuitive example that illustrates the concept.  the tool can generte a report about each folder in a directory tree.  Each Stanza of the report would contain a line about some particular directory,after that lines, there would be additional lines about the files in each folder.  The high-level stanzas are about the subject of *folders*, each report line about a folder containes a report line about a *file* in a directory.

#### Subject Query
A subject query defines an ordered list of subjects that are to be reported on. The Quaery yield parameters needed to identify a subject for each line in a report. The subjet Query is passed to a contructor of a StanzaFactory object in its constructor.


```python
        Folders = StanzaFactory("SELECT id FROM Folders ORDER BY folder_number")
        ```

In the above example, The StanzaFactory eventually generates a report where there is a line for each folder.  Evidently the returned *id* will be sufficient to locate the particular folder for a particular line in a report.

#### Queries to Generate a Report about a Specifc Subject
Reports about a specifc subect are realized in a row of a report. It may take more than one SQL query to generate the information needed in a report of a specfic subject. The results of each such query is called a segment. These ideas are implemented in the following way: Each Stanzafacory object reports about a given row.  The rows are composed by one of more segments. Each segment is defined by the output of a segment query. The segment queries use the sql parameters emitted by the subject query, discussed above, to identify the specifc subject for the row current being generated.

Segment queries are stored in a list. Segments are generated in left to right order, with the first added report segment being the left-most segement of the report. Each returned item frem the select statement is rendered as its own internal cell.  I.e each slected itme would be in its own cell in a report rendered as a spreadsheet.

```python
     Folders.add_report_segment(
         SegmentSQL("SELECT id, depth from Folders where id = '%s'")
     )
```
In the above example, the internal database ID, depth of folder in a heirarcy, and name of folder are reported. To generate a specifinc line the %s is replaces wth the id produced by the Subject query, describe in the previous section.

### Additional Context for a Segment Query.

Often an SQL query to generate a report needs more information that that the parameters that  describe the subject of a row. Also, sometiems the precise number of cells in a segment can vary. In each case, case additional context is needed. A query supporting additional context can be supplied the the *SegmentSQL* object constructor by the optional *context* argument.

```python
    Folders.add_report_segment("....",
        vcontext = QueryContext(args,"select ID from Parameters")
   )
```
When context is supplied, the SegmentSQL is repeated for each row returned by the context query.  The context query, above, causes a rwo to be genertes for each pararmeter. for each such colum the ID is the paratmeter is available as well as the parameters defining the subject of a row.     More later....

### Substanzas
```python
     Folders  = StanzaFactory(args,
         "SELECT Id from folders order by DEPTH"
     )
    Contents = StanzaFactory(args,
        "SELECT id from Contents where FolderId= '%s'
     )
     Folders.set_substanza (Contents)                                                                                         ```
                                                                                                                             