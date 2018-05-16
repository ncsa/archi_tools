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
import collections

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
        self.element_list = [] # dictionary holding name, type, id
    def ingest_items(self, items):
        for name, value in items:
            self.d[name]=value
    def ingest_wbslist(self,wbslist):
        self.d["wbs"] = ".".join(wbslist)
    def ingest_documentation(self, documentation):
        self.d["documentation"] = documentation
    def ingest_element(self, items):
        # provide stucture tuple of items cleaned of XML baggage
        #make a dict to handle the fact that not all things have names
        item_dict = collections.defaultdict(lambda : "")
        for item in items:
            #handle like this ('{http://www.w3.org/2001/XMLSchema-instance}type', 'archimate:ApplicationComponent')
            if  "type" in item[0]:
                item_dict["type"] = item[1].split(":")[1]
            #handle  this ('name', 'Overall Base AA and ITSEC'),
            elif  "name"  == item[0]:  
                item_dict["name"] = item[1]
            #handle guid like this  ('id', '25c8d1c1-818....')
            elif "id" == item[0]:
                item_dict["id"] = item[1]
        self.element_list.append(item_dict)
    def write_stanza(self, writer):
        out = []
        for h in self.HEADER: out.append(self.d[h])
        writer.writerow(out)
        for element in self.element_list:
            writer.writerow(["ELEMENT",self.d["wbs"],element["name"],element["type"]])
    def complete(self):
        ALL.append(self)
    

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
    info = folderinfo()
    depth=depth+1
    #extract documentions (really there is just one)
    for documentation in  folder.iterchildren("documentation"):
           info.ingest_documentation(documentation.text)
    #extract archiment elements 
    for element in  folder.iterchildren("element"):
        info.ingest_element(element.items())  #list of pairs of items 
    info.ingest_wbslist(wbslist)
    #Items are folderitems, like folder names 
    info.ingest_items(folder.items())
    info.complete()
    #recurr over all folders contained in this folder.
    sibno = 1
    for sibling in folder.iterchildren("folder"):
        this_wbslist = wbslist+["%s"%sibno]
        wbs(sibling, this_wbslist, depth)  #recur over any children
        sibno += 1        

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
    for row in ALL: row.write_stanza(writer)


