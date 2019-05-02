from reports import *

def validate_no_description_elements(args):

    # This validation find all elements in the tree that do not have a description and lists them in a tree-like fashion
    Folders  = StanzaFactory(args,
                             """SELECT DISTINCT f.ID as FolderID
                                FROM ELEMENTS e
                                INNER JOIN FOLDER f on f.id=e.ParentFolder
                                WHERE (e.Documentation IS NULL or e.Documentation = '')
                                ORDER BY f.Depth"""
    )
    Folders.add_report_segment(
        SegmentSQL("""SELECT f.ID, f.Name, 'Folder' as Type, f.Documentation
                      FROM FOLDER f
                      WHERE f.ID = '{FolderID}'""")
    )


    Elements = StanzaFactory(args,
                             """SELECT e.ID as ElementID
                                FROM ELEMENTS e
                                WHERE (e.Documentation IS NULL or e.Documentation = '') AND e.ParentFolder = '{FolderID}'
                                ORDER BY e.Name ASC"""
    )
    Elements.add_report_segment(
        SegmentSQL("""SELECT ' ' as ID, Name, 'Element' as Type, e.Documentation
                      FROM ELEMENTS e
                      WHERE e.ID = '{ElementID}'""")
    )

    Folders.set_substanza (Elements)


    # Folders.report({})
    return Folders
