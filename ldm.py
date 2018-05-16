#!/usr/bin/env python
"""
Process an archi .archimate xml into
material needed for re-costing. 

This is a stand-alone tool to generate a
wbs from a .archimate file.

The current processing extracts information from the
folder hierarchy, including descriptions associated
with the folder.

Additional information is generated from information
latent in the folder hierarchy. (e.g. wbs numbers)

It would be preferable to process an archimate
standard openexchange file instead of the
archi-version-specific .arcimante file. However,
The .archimate xml file is processed instead of the
arichimate standard openexchange file because the
descriptions associated with folders did not seem
to be exported via the openexcahange format.
Exporting descriptions seem to quite useful in
artifacts generated for downstream tool chains.

"""

import lxml.etree as ET
import argparse

prefix='{http://www.opengroup.org/xsd/archimate/3.0/}'
#tree = ET.parse('LSST.xml')


ALL = []  # hoild the list of all folders.
class folderinfo :
    """
    The folderinfo class holds all data extracted from a
    folder as well as data computed per-folder using the
    folder hierarchy (e.g the wbs).  guid name and type
    of elements are collected. 
    """

    HEADER = ["wbs","name","id","documentation"]
    def __init__(self):
        import collections
        self.d = collections.defaultdict(lambda : "")
        self.element_list = [] # id, name, type
    def ingest_items(self, items):
        for name, value in items:  self.d[name]=value
    def ingest_wbslist(self,wbslist):
        self.d["wbs"] = ".".join(wbslist)
    def ingest_documentation(self, documentation):
        self.d["documentation"] = documentation
    def ingest_element(self, id, name, type):
        self.element_list.append(self, [id, name, type])
    def get_line(self):
        out = []
        for h in self.HEADER: out.append(self.d[h])
        return out
    def complete(self):
        if len(ALL) == 0 : ALL.append(self.HEADER)
        ALL.append(self.get_line())
    

def wbs(folder, wbslist, depth):
    """
    Parse archimate for records related to folders and append
    per-folder folderinfo class objects to the global ALL list.

    Data Model supported:

    In the current archimante (4.2.0) version 
    Each top level archimate folder is is a <folder>
    just under the xml root.  <folders> may contain
    <folders>,  Folders man contain an optional
    <documentation> entity. <folders> contain
    items id and name. e.g.

    <folder name="foldername" id="guid">

"""
    sibno = 1
    depth=depth+1
    for sibling in folder.iterchildren("folder"):
        info = folderinfo()
        for documentation in  folder.iterchildren("documentation"):
            info.ingest_documentation(documentation.text)
        for element in  folder.iterchildren("element"):  pass
        this_wbslist = wbslist+["%s"%sibno]
        info.ingest_wbslist(this_wbslist)
        info.ingest_items(sibling.items())
        info.complete()
        wbs(sibling, this_wbslist, depth)  #recur over any children
        sibno += 1

#
# Start the recursive parse
#
        

#
#
#

if __name__ == "__main__" :

    import csv
    import sys

    #main_parser = argparse.ArgumentParser(add_help=False)
    main_parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=argparse.RawDescriptionHelpFormatter)
    main_parser.add_argument('--loglevel','-l',
                             help='loglevel NONE, NORMAL, VERBOSE, VVERBOSE, DEBUG',
                             default="ERROR")
    main_parser.add_argument("--prefix", "-p", default="LSST_")    
    main_parser.add_argument("archimatefile")
    args = main_parser.parse_args()

    
    tree = ET.parse(args.archimatefile)
    root = tree.getroot()
    wbs(root,[], 0)
    writer = csv.writer (sys.stdout)
    for row in ALL: writer.writerow (row)


