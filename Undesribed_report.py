from reports import *

def search_report(args):

    Search_term = 'Scope:NCOA'


    Folders  = StanzaFactory(args,
                             """select distinct d.ID as FID 
                                from FOLDER d
                                Inner join PROPERTIES p on p.id = FID
                                WHERE p.Key = '%s'
                                order by depth asc""" % Search_term
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
                             "SELECT id as Element from Elements  where ParentFolder= '{FID}'"
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


    # Folders.report({})
    return Folders
