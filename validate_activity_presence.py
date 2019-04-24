from reports import *

def validate_activity_presence(args):

    # This validation checks for active aka "round" elements present in Service Realization Viewpoint
    # but not in Behavior to Provisioning Maps
    Elem  = StanzaFactory(args,
                             """WITH AllViewActivity(ElementId, ViewId, Depth) AS (SELECT DISTINCT e.Id as ElementId, v.Id as ViewId, f.Depth
                                FROM FOLDER f
                                INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
                                INNER JOIN VIEW_OBJECTS vo on vo.view_id = v.Id
                                INNER JOIN ELEMENTS e on e.Id = vo.Object_id
                                WHERE e.Type like '%Function' or e.Type like '%Process' or e.Type like '%Process' or e.Type like '%Service')
                                SELECT ElementId, ViewId
                                FROM AllViewActivity 
                                WHERE Depth like '%Service Realization Viewpoint%'
                                AND ElementId not in (SELECT ElementId FROM AllViewActivity WHERE Depth like '%Behavior to Provisioning Map Viewpoint%')"""
    )
    Elem.add_report_segment(
        SegmentSQL("""SELECT Name, Type, Documentation from ELEMENTS WHERE Id = '{ElementId}' """)
    )
    Elem.add_report_segment(
        SegmentSQL("""SELECT Name, Documentation from VIEWS WHERE Id = '{ViewId}' """)
    )





    # Elem.report({})
    return Elem
