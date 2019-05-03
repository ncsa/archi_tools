from reports import *

def validate_view_elements(args):

    # Find what relations exist in a search path
    # Search_term will be checked for in all folder pathways.
    # that means all matching folders and their subfolders will be checked
    Search_term = 'Service to Provisioning Map Viewpoint'


    Folders  = StanzaFactory(args,
                             """SELECT DISTINCT e.Type as Source, r.Type as Relationship, e1.Type as Target
                                FROM FOLDER f
                                INNER JOIN VIEWS v on v.Parent_folder_id = f.ID
                                INNER JOIN CONNECTIONS c on c.view_id = v.ID
                                INNER JOIN RELATIONS r on r.ID = c.relationship_id
                                INNER JOIN ELEMENTS e on e.id = r.Source
                                INNER JOIN ELEMENTS e1 on e1.id = r.Target
                                WHERE f.Depth LIKE '%R3PL4C3M3%'""".replace('R3PL4C3M3', Search_term)
    )
    Folders.add_report_segment(
        SegmentSQL("SELECT '{Source}' as Source, '{Relationship}' as Relationship, '{Target}' as Target ")
    )




    return Folders
