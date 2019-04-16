from reports import *

def validate_application_presence(args):


    Elem  = StanzaFactory(args,
                             """WITH AppInView(Id) AS (SELECT DISTINCT e.Id
                                FROM FOLDER f
                                INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
                                INNER JOIN VIEW_OBJECTS vo on vo.view_id = v.Id
                                INNER JOIN ELEMENTS e on e.Id = vo.Object_id
                                WHERE f.Depth like '%Service Realization Viewpoint%' 
                                AND (e.Type like 'Application%' or e.Type = 'DataObject')
                                /* AND e.Type = 'ApplicationService' */
                                )
                                SELECT e.Id as ElementID
                                FROM ELEMENTS e
                                WHERE (e.Type like 'Application%' or e.Type = 'DataObject' )
                                /* WHERE Type = 'ApplicationService'  */
                                AND e.Id NOT IN (SELECT Id FROM AppInView)"""
    )
    Elem.add_report_segment(
        SegmentSQL("""SELECT Name, Type, Documentation from ELEMENTS WHERE Id = '{ElementID}' """)
    )





    # Elem.report({})
    return Elem
