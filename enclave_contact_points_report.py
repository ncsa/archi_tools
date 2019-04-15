from reports import *

def enclave_contact_points_report(args):


    ObjectList  = StanzaFactory(args,
                             """SELECT vo.Object_id, COUNT(DISTINCT vo.Container_id) as EncCount
                                FROM FOLDER f
                                INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
                                INNER JOIN VIEW_OBJECTS vo on vo.view_id = v.Id
                                /* Leave only the enclave containers */
                                INNER JOIN ENCLAVES en on en.Id = vo.Container_id
                                WHERE f.Depth like '%Service Realization Viewpoint%'
                                GROUP BY vo.Object_id
                                HAVING COUNT(DISTINCT vo.Container_id) >1
                                ORDER BY EncCount asc"""
    )
    ObjectList.add_report_segment(
        SegmentSQL("""SELECT e.Name as ElementName, '{EncCount}' as UniqueEnclaves, '' as ViewName, '' as EnclaveName
                      FROM ELEMENTS e
                      WHERE e.id='{Object_id}'""")
    )



    ViewsOfInterest = StanzaFactory(args, """SELECT '' as Blank1, '' as Blank2, v.Name AS ViewName, en.Name as EnclaveName
                                          FROM FOLDER f
                                          INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
                                          INNER JOIN VIEW_OBJECTS vo on vo.view_id = v.Id
                                          /* Leave only the enclave containers */
                                          INNER JOIN ENCLAVES en on en.Id = vo.Container_id
                                          WHERE vo.Object_id = '{Object_id}'"""
    )
    ViewsOfInterest.add_report_segment(
        SegmentSQL("""SELECT '{Blank1}' as Blank1, '{Blank2}' as Blank2, '{ViewName}' as ViewName, '{EnclaveName}' as EnclaveName """)
    )

    ObjectList.set_substanza(ViewsOfInterest)



    # ObjectList.report({})
    return ObjectList
