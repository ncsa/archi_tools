from reports import *

def contact_points_report(args):

    # enter view and enclave names separated by semicolumns, without spaces
    view_names = 'Spectrograph Archiving Service Data Management'
    EnclaveSetOne = 'Enc:NCSA'
    EnclaveSetTwo = 'Enc:L1;Scope:NCOA'

    view_split = view_names.split(";")
    EnclaveOneSplit = EnclaveSetOne.split(";")
    EnclaveTwoSplit = EnclaveSetTwo.split(";")

    views = "'"
    for table in view_split:
        views += table + "', '"
    views = views[:-3]

    EnclaveOne = "'"
    for enclave in EnclaveOneSplit:
        EnclaveOne += enclave + "', '"
    EnclaveOne = EnclaveOne[:-3]

    EnclaveTwo = "'"
    for enclave in EnclaveTwoSplit:
        EnclaveTwo += enclave + "', '"
    EnclaveTwo = EnclaveTwo[:-3]



    ViewList  = StanzaFactory(args,
                             """SELECT id as View_id
                                FROM VIEWS v
                                WHERE v.name in (%s)""" % views
    )
    ViewList.add_report_segment(
        SegmentSQL("""SELECT Name
                      FROM VIEWS v
                      WHERE v.id='{View_id}'""")
    )



    SourceObjects = StanzaFactory(args, """SELECT DISTINCT vo.Object_id as SourceObject, e.Name as SourceName, p.Key as SourceKey
                                      FROM VIEW_OBJECTS vo
                                      INNER JOIN VIEWS v on v.id = vo.View_id
                                      INNER JOIN RELATIONS r on r.source = vo.Object_id
                                      INNER JOIN VIEW_OBJECTS vo1 on vo1.Object_id = r.Target
                                      INNER JOIN VIEWS v1 on v1.id = vo1.View_id
                                      INNER JOIN PROPERTIES p on p.id=vo.Object_id AND (p.key IN (%s) or p.key IN (%r))
                                      INNER JOIN PROPERTIES p1 on p1.id=vo1.Object_id AND (p1.key IN (%s) or p1.key IN (%r))
                                      INNER JOIN ELEMENTS e on e.id =r.source 
                                      WHERE v.Name in (%l) AND v1.Name in (%l)
                                            AND p.Key <> p1.Key""".replace('%l', views).replace('%s', EnclaveOne).replace('%r', EnclaveTwo)
    )
    SourceObjects.add_report_segment(
        SegmentSQL("SELECT '{SourceObject}' AS SourceObject, '{SourceName}' AS SourceName, '{SourceKey}' as Key ")
    )

    ViewList.set_substanza(SourceObjects)

    TargetObjects = StanzaFactory(args, """SELECT r.Type, r.Name as RelationshipName, e.Name, p.Key as TargetKey
                                           FROM VIEW_OBJECTS vo
                                           INNER JOIN VIEWS v on v.id = vo.View_id
                                           INNER JOIN RELATIONS r on r.source = vo.Object_id
                                           INNER JOIN PROPERTIES p on p.id=r.Target AND p.Key <> '{SourceKey}'
                                           INNER JOIN ELEMENTS e on e.id = r.Target
                                           WHERE v.Name in (%l) AND r.Source = '{SourceObject}'""".replace('%l', views)
                                  )
    TargetObjects.add_report_segment(
        SegmentSQL("SELECT ' ' as Blank, '{Type}' AS Type, '{RelationshipName}' AS Relationship, '{Name}' as ObjectName, '{TargetKey}' as TargetKey ")
    )

    SourceObjects.set_substanza(TargetObjects)



    # ViewList.report({})
    return ViewList
