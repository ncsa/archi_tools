from reports import *

def plateau_report(args):



    Folders  = StanzaFactory(args,
                             "SELECT distinct Id as FID from folder order by depth asc limit 10"
    )
    Folders.add_report_segment(
        SegmentSQL("SELECT id, 'Folder' as Kind, Name, Documentation from Folder where id = '{FID}'")
    )
    Folders.add_report_segment(
        SegmentSQL("SELECT case Value when '' then 'yes' else value end from PROPERTIES where id = '{FID}' AND key='{Key}'",
                   context=QueryContext(args,
                                        "select distinct Key from PROPERTIES order by key desc")
                   )
    )


    Elements = StanzaFactory(args,
                             "SELECT Element from Folder_elements  where folder= '{FID}'"
    )
    Elements.add_report_segment(
        SegmentSQL("SELECT id, 'Element' as Kind, Name, Documentation from Elements Where id = '{Element}'")
    )

    Elements.add_report_segment(
        SegmentSQL(
            "SELECT case Value when '' then 'yes' else value end from PROPERTIES where id = '{Element}' AND key='{Key}'",
            context=QueryContext(args,
                                 "select distinct Key from PROPERTIES order by key desc")
            )
    )

    Folders.set_substanza (Elements)


    # Folders.report({}) #2
    return Folders #3
