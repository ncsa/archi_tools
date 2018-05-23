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


ALL = []  # hold the list of all folders.
class folderinfo :
    """
    The folderinfo class holds all data extracted from a
    folder as well as data computed per-folder using the
    folder hierarchy (e.g the wbs).  guid name and type
    of elements are collected. 
    """

    HEADER = ["wbs","name","id","documentation","units"]
    def __init__(self):
        import collections
        self.d = collections.defaultdict(lambda : "")
        self.element_list = [] # dictionary holding name, type, id
    def ingest_items(self, items):
        for name, value in items:
            self.d[name]=value
    def ingest_wbslist(self,wbslist):
        self.d["wbs"] = "WBS " + ".".join(wbslist)
    def ingest_documentation(self, documentation):
        self.d["documentation"] = documentation
    def ingest_element(self, items, element_doc, element_units):
        # provide stucture tuple of items cleaned of XML baggage
        #make a dict to handle the fact that not all things have names
        item_dict = collections.defaultdict(lambda : "")
        item_dict["documentation"] = element_doc
        item_dict["units"] = element_units
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
        for h in ["wbs","name","documentation"]: out.append(self.d[h])
        writer.writerow(out)
        for element in self.element_list:
            #Hack only report on Ndes and equiment.
            if "Node" in element["type"]  or "Equipment" in element["type"]:
                pass
            else:
                continue
            out = [self.d["wbs"]]  
            for item in ["name","documentation","units"] : out.append(element[item])
            writer.writerow(out)
    def append_excel(self, worksheet, rowno):
        col = 1
        #folder information
        for h in ["wbs","id","name","documentation"]:
            blue = "000000FF"
            worksheet.cell(row=rowno, column=col, value=self.d[h])
            worksheet.cell(row=rowno, column=col).font = Font(bold=True)
            #no mattere the RGB I set BLUE to the background renders as blacl
            #worksheet.cell(row=rowno, column=col).fill = PatternFill(bgColor=blue, fill_type = "solid")
            if "documentation" == h :
                worksheet.cell(row=rowno, column=col).alignment = Alignment(wrapText=True)
            col += 1
        rowno += 1
        #element  information
        #Hack only report on Nodes and Equipment.
        for element in self.element_list:
            col = 1
            if "Node" in element["type"]  or "Equipment" in element["type"]:
                pass
            else:
                continue
            worksheet.cell(row=rowno, column=col, value=self.d["wbs"])
            col += 1
            worksheet.cell(row=rowno, column=col, value=self.d["id"])
            col += 1
            for item in ["name","documentation","units"] :
                worksheet.cell(row=rowno, column=col, value=element[item])
                if "documentation" == item :
                    worksheet.cell(row=rowno, column=col).alignment = Alignment(wrapText=True)
                col += 1
            rowno += 1
        return rowno
        
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
    #
    # HACK Producing just Technoloy
    if  wbslist and wbslist[0] != '4' :
        return
    #Items are folderitems, like folder names 
    info.ingest_items(folder.items())
    #extract documentions (really there is just one)
    for documentation in  folder.iterchildren("documentation"):
           info.ingest_documentation(documentation.text)
    #extract archiment elements 
    for element in  folder.iterchildren("element"):
            #extract documentions (really there is just one)
        doc = ""
        for documentation in  element.iterchildren("documentation"):
           doc = documentation.text
        units = ""
        for property in element.iterchildren("property"):
            for key  in property.values():
                if "UNIT" in key : units = key 
        info.ingest_element(element.items(), doc, units)  #list of pairs of items 
    info.ingest_wbslist(wbslist)
    info.complete()
    #recurr over all folders contained in this folder.
    sibno = 1
    for sibling in folder.iterchildren("folder"):
        this_wbslist = wbslist+["%s"%sibno]
        wbs(sibling, this_wbslist, depth)  #recur over any children
        sibno += 1        

###########################################################
#
# Main program
#
############################################################
      

if __name__ == "__main__" :

    import csv
    import sys
    import shlog
    from openpyxl import Workbook
    from openpyxl.styles import Font
    from openpyxl.styles import Alignment
    from openpyxl.styles import PatternFill
    
    #main_parser = argparse.ArgumentParser(add_help=False)
    main_parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=argparse.RawDescriptionHelpFormatter,
     fromfile_prefix_chars='@')
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
    #for row in ALL: row.write_stanza(writer)
    wb = Workbook() #make workbook
    ws = wb.active  #use default sheet
    rowno = 1
    #build the workbook
    for row in ALL: rowno = row.append_excel(ws, rowno)
    #set columns to reasonable widths.
    for col in ws.columns:
        max_length = 0
        column = col[0].column # Get the column name
        for cell in col:
            try: # Necessary to avoid error on empty cells
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
            adjusted_width = (max_length + 2) * 1.2
            adjusted_width = min (adjusted_width, 60)
        ws.column_dimensions[column].width = adjusted_width
    wb.save("dog.xlsx")

