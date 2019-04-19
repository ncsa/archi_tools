from reports import *

def validate_services_vs_interfaces(args):

    # Find all interfaces
    ViewList  = StanzaFactory(args,
                             """SELECT DISTINCT v.id as View_id
                                FROM VIEWS v
                                INNER JOIN VIEW_OBJECTS vo on vo.view_id = v.id
                                INNER JOIN ELEMENTS e on e.ID = vo.Object_id
                                WHERE e.Type LIKE '%Interface'"""
    )
    ViewList.add_report_segment(
        SegmentSQL("""SELECT Name as ViewName, '' as ElementName, '' as ElementType, '' as Documentation
                      FROM VIEWS v
                      WHERE v.id='{View_id}'""")
    )



    SourceObjects = StanzaFactory(args, """SELECT ' ' as ViewName, e.Name as ElementName, e.Type as ElementType, e.Documentation
                                           FROM VIEW_OBJECTS vo
                                           INNER JOIN ELEMENTS e on e.ID = vo.Object_id
                                           WHERE vo.view_id = '{View_id}' 
                                           AND (e.Type LIKE '%Interface')"""
    )
    SourceObjects.add_report_segment(
        SegmentSQL("""SELECT '{ViewName}' as ViewName, '{ElementName}' as ElementName, '{ElementType}' as ElementType, "{Documentation}" as Documentation  """)
    )

    ViewList.set_substanza(SourceObjects)



    # ViewList.report({})
    return ViewList
