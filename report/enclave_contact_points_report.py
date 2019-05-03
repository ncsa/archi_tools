from reports import *

def enclave_contact_points_report(args):

    # This report finds elements that belong to multiple enclaves
    SearchTerm ='Service Realization Viewpoint'

    ObjectList  = StanzaFactory(args,
                             """SELECT vo.Object_id, COUNT(DISTINCT vo.Container_id) as EncCount
                                FROM FOLDER f
                                INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
                                INNER JOIN VIEW_OBJECTS vo on vo.view_id = v.Id
                                /* Leave only the enclave containers */
                                INNER JOIN ENCLAVES en on en.Id = vo.Container_id
                                WHERE f.Depth like '%F1LL3R%'
                                GROUP BY vo.Object_id
                                HAVING COUNT(DISTINCT vo.Container_id) >1
                                ORDER BY EncCount asc""".replace('F1LL3R', SearchTerm)
    )
    ObjectList.add_report_segment(
        SegmentSQL("""SELECT e.Name as ElementName, e.Type as ElementType, '{EncCount}' as UniqueEnclaves, '' as ViewName, '' as EnclaveName, '' as Relation, '' as RelatedElement
                      FROM ELEMENTS e
                      WHERE e.id='{Object_id}'""")
    )



    ViewsOfInterest = StanzaFactory(args, """SELECT v.Name AS ViewName, en.Name as EnclaveName, v.Id as View_id, vo.Object_id
                                          FROM FOLDER f
                                          INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
                                          INNER JOIN VIEW_OBJECTS vo on vo.view_id = v.Id
                                          /* Leave only the enclave containers */
                                          INNER JOIN ENCLAVES en on en.Id = vo.Container_id
                                          WHERE vo.Object_id = '{Object_id}' AND f.Depth like '%F1LL3R%'""".replace('F1LL3R', SearchTerm)
    )
    ViewsOfInterest.add_report_segment(
        SegmentSQL("""SELECT '' as Blank1, '' as Blank2, '' as Blank3, '{ViewName}' as ViewName, '{EnclaveName}' as EnclaveName, '' as Blank4, '' as Blank5 """)
    )

    ObjectList.set_substanza(ViewsOfInterest)


    # Comment the enxt stanza out to disable related element lookup
    Connections = StanzaFactory(args, """WITH TargetList(RelName, ElementId) AS (SELECT CASE r.Name WHEN '' THEN r.Type ELSE r.Name || ' - ' || r.Type END as RelName, r.Source as ElementId
                                            FROM FOLDER f
                                            INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
                                            INNER JOIN CONNECTIONS c on c.view_id = v.Id
                                            INNER JOIN RELATIONS r on r.ID = c.relationship_id
                                            WHERE v.Id = '{View_id}' AND r.Target = '{Object_id}' AND r.Type <> 'CompositionRelationship')
                                            
                                            SELECT CASE r.Name WHEN '' THEN r.Type ELSE r.Name || ' - ' || r.Type END as RelName, r.Target as ElementId
                                            FROM FOLDER f
                                            INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
                                            INNER JOIN CONNECTIONS c on c.view_id = v.Id
                                            INNER JOIN RELATIONS r on r.ID = c.relationship_id
                                            WHERE v.Id = '{View_id}' AND r.Source = '{Object_id}' AND r.Type <> 'CompositionRelationship'
                                            
                                            UNION ALL
                                            
                                            SELECT RelName, ElementId FROM TargetList"""
                                    )
    Connections.add_report_segment(
        SegmentSQL(
            """SELECT '' as Blank1, '' as Blank2, '' as Blank3, '' as Blank4, '' as Blank5, '{RelName}' as RelName, e.Name as ElementName 
                FROM ELEMENTS e
                WHERE e.Id = '{ElementId}'""")
    )

    ViewsOfInterest.set_substanza(Connections)


    return ObjectList
