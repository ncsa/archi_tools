from reports import *

def contact_points_report(args):


    ViewList  = StanzaFactory(args,
                             """SELECT DISTINCT v.id as View_id
                                /* Get all relations that exist in views */
								FROM VIEWS v
                                INNER JOIN CONNECTIONS c on c.view_id = v.id
                                INNER JOIN RELATIONS r on r.id = c.relationship_id
								/* Get first round of enclaves */
								INNER JOIN ENCLAVE_CONTENT ec on r.Source = ec.Object_id
								/* Get second round of enclaves */
								INNER JOIN ENCLAVE_CONTENT ec1 on r.Target = ec1.Object_id
                                WHERE ec.Enclave_id <> ec1.Enclave_id"""
    )
    ViewList.add_report_segment(
        SegmentSQL("""SELECT Name as ViewName, '' as SourceName, '' as TargetName, '' as Enclave, '' as Relation, '' as Description
                      FROM VIEWS v
                      WHERE v.id='{View_id}'""")
    )



    SourceObjects = StanzaFactory(args, """SELECT DISTINCT r.Source as SourceObject, e.Name as SourceName, en.Name as SourceEnclave, ec.Enclave_id as SourceEnclaveID, v.id as View_id, e.Documentation as SourceDoc
                                           FROM VIEWS v
                                           INNER JOIN CONNECTIONS c on c.view_id = v.id
                                           INNER JOIN RELATIONS r on r.id = c.relationship_id
                                           INNER JOIN ELEMENTS e on e.id = r.Source
										   /* Get first round of enclaves */
										   INNER JOIN ENCLAVE_CONTENT ec on r.Source = ec.Object_id
										   INNER JOIN ENCLAVES en on en.Id = ec.Enclave_id
										   /* Get second round of enclaves */
										   INNER JOIN ENCLAVE_CONTENT ec1 on r.Target = ec1.Object_id
										   INNER JOIN ENCLAVES en1 on en1.Id = ec1.Enclave_id
                                           WHERE v.id = '{View_id}'
                                           AND ec.Enclave_id <> ec1.Enclave_id"""
    )
    SourceObjects.add_report_segment(
        SegmentSQL("""SELECT ' ' as Blank0, '{SourceName}' AS SourceName, ' ' as Blank1, '{SourceEnclave}' as SourceEnclave, ' ' as Blank2, "{SourceDoc}" as SourceDoc """)
    )

    ViewList.set_substanza(SourceObjects)

    TargetObjects = StanzaFactory(args, """SELECT DISTINCT r.Type, r.Name as RelationshipName, e.Name, en.Name as TargeetEnclaveName, e.Documentation as TargetDoc
                                          FROM VIEWS v
                                          INNER JOIN CONNECTIONS c on c.view_id = v.id
                                          INNER JOIN RELATIONS r on r.id = c.relationship_id
                                          INNER JOIN ELEMENTS e on e.id = r.Target
										  INNER JOIN ENCLAVE_CONTENT ec on r.Target = ec.Object_id AND ec.Enclave_id <> '{SourceEnclaveID}'
										  INNER JOIN ENCLAVES en on en.Id = ec.Enclave_id
                                          WHERE v.id = '{View_id}' AND r.Source = '{SourceObject}'"""
                                  )
    TargetObjects.add_report_segment(
        SegmentSQL("""SELECT ' ' as Blank1, ' ' as Blank0, '{Name}' as ObjectName, '{TargeetEnclaveName}' as TargeetEnclaveName, '{RelationshipName}' as Relationship, "{TargetDoc}" as TargetDoc """)
    )

    SourceObjects.set_substanza(TargetObjects)



    # ViewList.report({})
    return ViewList
