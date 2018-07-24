from reports import *

def plateau_report(args):



    Folders  = StanzaFactory(args,
                             "SELECT Id FID from folder"
    )
    Folders.add_report_segment(
        SegmentSQL("SELECT id, Wbs, Name, Documentation, Location, Enclave   from Folder where id = '{FID}'")
    )


    Elements = StanzaFactory(args,
                             "SELECT Element from Folder_elements  where folder= '{FID}'"
    )
    Elements.add_report_segment(
        SegmentSQL("SELECT * from Elements Where id = '{Element}'")
    )
    
    Elements.add_report_segment(
       SegmentSQL("SELECT '{PNAME}' FROM relations WHERE source = '{Plateau_id}' and Target = '{Element}'",
                   context = QueryContext(args,"SELECT id Plateau_id, name PNAME  FROM  elements WHERE type = 'Plateau' ORDER BY NAME")
        )
    )

    Folders.set_substanza (Elements)


    Folders.report({})
    return Folders
