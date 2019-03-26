from reports import *

def contact_points_report(args):


    ViewList  = StanzaFactory(args,
                             """SELECT DISTINCT v.id as View_id
                                FROM VIEWS v
                                INNER JOIN CONNECTIONS c on c.view_id = v.id
                                INNER JOIN RELATIONS r on r.id = c.relationship_id
                                INNER JOIN PROPERTIES p on p.id=r.Source AND (p.key LIKE 'Enc:%')
                                INNER JOIN PROPERTIES p1 on p1.id=r.Target AND (p1.key LIKE 'Enc:%')
                                WHERE p.Key <> p1.Key"""
    )
    ViewList.add_report_segment(
        SegmentSQL("""SELECT Name as ViewName, '' as SourceName, '' as TargetName, '' as Enclave, '' as Relation, '' as Description
                      FROM VIEWS v
                      WHERE v.id='{View_id}'""")
    )



    SourceObjects = StanzaFactory(args, """SELECT DISTINCT r.Source as SourceObject, e.Name as SourceName, p.Key as SourceKey, v.id as View_id, e.Documentation as SourceDoc
                                           FROM VIEWS v
                                           INNER JOIN CONNECTIONS c on c.view_id = v.id
                                           INNER JOIN RELATIONS r on r.id = c.relationship_id
                                           INNER JOIN PROPERTIES p on p.id=r.Source AND (p.key LIKE 'Enc:%')
                                           INNER JOIN PROPERTIES p1 on p1.id=r.Target AND (p1.key LIKE 'Enc:%')
                                           INNER JOIN ELEMENTS e on e.id = r.Source
                                           WHERE v.id = '{View_id}'
                                           AND p.Key <> p1.Key"""
    )
    SourceObjects.add_report_segment(
        SegmentSQL("""SELECT ' ' as Blank0, '{SourceName}' AS SourceName, ' ' as Blank1, '{SourceKey}' as Key, ' ' as Blank2, "{SourceDoc}" as SourceDoc """)
    )

    ViewList.set_substanza(SourceObjects)

    TargetObjects = StanzaFactory(args, """SELECT DISTINCT r.Type, r.Name as RelationshipName, e.Name, p.Key as TargetKey, e.Documentation as TargetDoc
                                          FROM VIEWS v
                                          INNER JOIN CONNECTIONS c on c.view_id = v.id
                                          INNER JOIN RELATIONS r on r.id = c.relationship_id
                                          INNER JOIN PROPERTIES p on p.id=r.Target AND p.Key <> '{SourceKey}'
                                          INNER JOIN ELEMENTS e on e.id = r.Target
                                          WHERE v.id = '{View_id}' AND r.Source = '{SourceObject}'"""
                                  )
    TargetObjects.add_report_segment(
        SegmentSQL("""SELECT ' ' as Blank1, ' ' as Blank0, '{Name}' as ObjectName, '{TargetKey}' as TargetKey, '{RelationshipName}' as Relationship, "{TargetDoc}" as TargetDoc """)
    )

    SourceObjects.set_substanza(TargetObjects)



    # ViewList.report({})
    return ViewList
