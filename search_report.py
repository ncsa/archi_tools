from reports import *

def search_report(args):

    Search_term = 'Scope:NCOA'


    Folders  = StanzaFactory(args,
                             """WITH RECURSIVE depths(id, name, depth) AS (
    SELECT id, Name, 0
    FROM FOLDER
    WHERE parent_id IS NULL
    UNION ALL
    SELECT FOLDER.id, FOLDER.Name, depths.depth + 1
    FROM FOLDER
    JOIN depths ON FOLDER.parent_id = depths.id
)
select d.ID as FID 
from depths d
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

    #
    # Elements = StanzaFactory(args,
    #                          "SELECT Element from Folder_elements  where folder= '{FID}'"
    # )
    # Elements.add_report_segment(
    #     SegmentSQL("SELECT id, 'Element' as Kind, Name, Documentation from Elements Where id = '{Element}'")
    # )
    #
    # Elements.add_report_segment(
    #     SegmentSQL(
    #         "SELECT case Value when '' then 'yes' else value end from PROPERTIES where id = '{Element}' AND key='{Key}'",
    #         context=QueryContext(args,
    #                              "select distinct Key from PROPERTIES order by key desc")
    #         )
    # )
    #
    # Folders.set_substanza (Elements)


    Folders.report({})
    return Folders
