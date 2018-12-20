# Archi_Tool
Archi_tool is a set of scripts to load information from
an Archimate model database dump into an SQLite database, where the data
can then be used to achieve the following goals:

- Produce reports used in day to day management tasks.
Aspirational goals:
  - Logical Architecture transfer to a configuration management tool.
  - Component model to feed a financial management tool.
  - Component model for a first cut work breakdown structure for a change.
  - Component model for fault trees and other material.

*The tool is very much a work in progress, evolving as needed*

## Build a database to support reporting and data interchange

### Software Installation

The software is in an early state. Early users
are managers using Apple Macintosh computers. Since 2.7 is shipped with
the current MacOS, the primary version of python
used is 2.7. Efforts are made to accommodate Python 3,
but testing is not generally done on Python 3.

Also, efforts are currently made to package all the
underpinnings as copied into the archi_tool package.

However, the following packages must be installed for proper operation of the tools:

* xlsxwriter
* openpyxl
* lxml

At the current level of development, the archi_tool software is
run from the directory holding the software.  Archi_tool software
is distributed via git as follows:

```shell
#Make an initial  archi_tool directory a filled with archi_tool stuff.
$ git clone https://github.com/ncsa/archi_tools.git
```

Update from the current git master branch.

```shell
#update an archi_tool directory with new stuff.
$git pull origin master
```

### Run-time Conventions

Archi_tool allows for working with several Archimate models.  Each model is stored in the Archi database export, along with all of its elements, folders, and connections.

Archi_tool uses the prefix/model name to retrieve the elements relevant to the model.   Current conventions are:

1. The current working directory is the archi_tools directory produced
by the *git clone*.

1. All Archi database exports are located in the *archi_tools/cache* folder.

### Generating a usable database.

1. Having done all of the above,
```shell
$ ./archi_tool -p DEMAND mkdb   #deletes prior database and makes a new, empty database
$ ./archi_tool -p DEMAND ingest #ingest csv into the data and makes supplemental info
```

Extra tables are built on assumptions about the modeling
methodologies and conventions used.  The currently supported
conventions are defined and implemented in conventions.py


## Hierarchical Report Generator

reports.py is a small python report generator provided with archi_tools.
An individual report is specified by coding a small python subroutine
which declares objects and relates them to a master object, and
returns the master object as the function returned.

The basic steps are:
- Work with the default set in the archi_tools directory
- Compose a report as a python file, conventionally named `<topic>_report.py` in the Archimate directory
- run `$ ./reports.py` to make a report as an excel file (optionally automatically running excel to display the report).

Example:

```shell
# cd archi_tool
# Assimtion You have built the databse for a a archi
$ ./reports.py -p DEMAND report plateau_report.py
```
### Report Specification



#### StanzaFactory
A stanza defines a line in a report. A stanzaFactory is an object that creates many stanzas base on SQL queries. Three types of SQL queries define a stanza.  All of these queries relate to a single subject.  A line about a particular subject may optionally be followed by a substanza where each line contains information about a different sort of subject.

The idea directories and files is an intuitive example that illustrates the concept. The tool can generate a report about each folder in a directory tree.  Each Stanza of the report would contain a line about some particular directory, after that lines, there would be additional lines about the files in each folder.  The high-level stanzas are about the subject of *folders*, each report line about a folder contains a report line about a *file* in a directory.

###  Example report

```Python
from reports import *

def plateau_report(args):

    ### The top-level organization of this report is done by folder.
    ### Write a query getting the folders, and let FID be a name know to archi_tool...
    ###  ... as a name referring to each folder as it is processed.
    Folders  = StanzaFactory(args,
                             "SELECT Id FID from folder"
    )

    ###  For each folder, print the output of this select statement...
    ###  ... in distinct columns of the report.
    Folders.add_report_segment(
        SegmentSQL("SELECT id, Wbs, Name, Documentation, Location, Enclave   from Folder where id = '{FID}'")
    )

    ####
    #   Below a line for a folder, make additional lines, one for each element in the folder
    ####

    # Let each element in the folder be known as ELE as it is processed.
    Elements = StanzaFactory(args,
                             "SELECT Element ELE from Folder_elements  where folder= '{FID}'"
    )

    # The left-most columns for the elements are all the attributes of the element itself.
    Elements.add_report_segment(
        SegmentSQL("SELECT * from Elements Where id = '{ELE}'")
    )

    #additional column for each element reports on whether there is a plateau associated with the element
    #making a kind of matrix.
    Elements.add_report_segment(
       SegmentSQL("SELECT '{PNAME}' FROM relations WHERE source = '{Plateau_id}' and Target = '{Element}'",
                   context = QueryContext(args,"SELECT id Plateau_id, name PNAME  FROM  elements WHERE type = 'Plateau' ORDER BY NAME")
        )
    )

    # Tell the report engine that after elven folder, make the report about the elements in that folder.
    Folders.set_substanza (Elements)


    return Folders

```
#### Subject Query
A subject query defines an ordered list of subjects that are to be reported on. The Query yield parameters needed to identify a subject for each line in a report. The subject Query is passed to a constructor of a StanzaFactory object in its constructor.


```python
        Folders = StanzaFactory("SELECT id FROM Folders ORDER BY folder_number")
        ```

In the above example, The StanzaFactory eventually generates a report where there is a line for each folder.  Evidently, the returned *id* is sufficient to locate the particular folder for a particular line in a report.

#### Queries to Generate a Report about a Specific Subject
Reports about a specific subject are realized in a row of a report. It may take more than one SQL query to generate the information needed in a report of a specific subject. The results of each such query are called a segment. These ideas are implemented in the following way: Each Stanzafacory object reports about a given row.  The rows are composed of one or more segments. Each segment is defined by the output of a segment query. The segment queries use the SQL parameters emitted by the subject query, discussed above, to identify the specific subject for the row current being generated.

Segment queries are stored in a list. Segments are generated in left to right order, with the first added report segment being the left-most segment of the report. Each returned item from the select statement is rendered as its own internal cell.  I.e., each selected item would be in its own cell in a report rendered as a spreadsheet.

```python
     Folders.add_report_segment(
         SegmentSQL("SELECT id, depth from Folders where id = '%s'")
     )
```
In the above example, the internal database ID, depth of folder in a hierarchy, and the name of the folder are reported. To generate a specific line, the %s is replaced with the id produced by the Subject query, described in the previous section.

### Additional Context for a Segment Query.

Often an SQL query to generate a report needs more information than the parameters that describe the subject of a row. Also, sometimes the precise number of cells in a segment can vary. In each case, additional case context is needed. A query supporting additional context can be supplied the *SegmentSQL* object constructor by the optional *context* argument.

```python
    Folders.add_report_segment("....",
        vcontext = QueryContext(args,"select ID from Parameters")
   )
```
When the context is supplied, the SegmentSQL is repeated for each row returned by the context query.  The context query, above, causes a row to be generated for each parameter. For each such column, the ID is the parameter is available as well as the parameters defining the subject of a row.

### Substanzas
```python
     Folders  = StanzaFactory(args,
         "SELECT Id from folders order by DEPTH"
     )
    Contents = StanzaFactory(args,
        "SELECT id from Contents where FolderId= '%s'
     )
     Folders.set_substanza (Contents)                                                                                         ```


TO BE CONTINUED
                                                                                                                             