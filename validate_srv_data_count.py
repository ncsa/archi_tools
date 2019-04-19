from reports import *

def validate_srv_data_count(args):

    # Find how many times every data object appears in SRVs and where
    AppearancesCount  = StanzaFactory(args,
                             """SELECT DISTINCT COUNT(DISTINCT v.Id) as ViewCount
                                FROM FOLDER f
                                INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
                                INNER JOIN VIEW_OBJECTS vo on vo.view_id = v.Id
                                INNER JOIN ELEMENTS e on e.Id = vo.Object_id
                                WHERE f.Depth LIKE '%Service Realization Viewpoint%' AND e.Type = 'DataObject'
                                GROUP BY vo.Object_id
                                ORDER BY ViewCount"""
    )
    AppearancesCount.add_report_segment(
        SegmentSQL("""SELECT '{ViewCount}' as Appearances, '' as Name, '' as ViewName""")
    )

    Objects = StanzaFactory(args,
                                     """SELECT vo.Object_id, COUNT(DISTINCT v.Id) as ViewCount
                                        FROM FOLDER f
                                        INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
                                        INNER JOIN VIEW_OBJECTS vo on vo.view_id = v.Id
                                        INNER JOIN ELEMENTS e on e.Id = vo.Object_id
                                        WHERE f.Depth LIKE '%Service Realization Viewpoint%' AND e.Type = 'DataObject'
                                        GROUP BY vo.Object_id
                                        HAVING COUNT(DISTINCT V.Id) = CAST('{ViewCount}' as integer)
                                        ORDER BY e.Name"""
                                     )
    Objects.add_report_segment(
        SegmentSQL("""SELECT DISTINCT '' as Blank1, e.Name
                      FROM FOLDER f
                      INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
                      INNER JOIN VIEW_OBJECTS vo on vo.view_id = v.Id
                      INNER JOIN ELEMENTS e on e.Id = vo.Object_id
                      WHERE f.Depth LIKE '%Service Realization Viewpoint%' AND e.Id = '{Object_id}'""")
    )

    AppearancesCount.set_substanza(Objects)


    Views = StanzaFactory(args,
                            """SELECT DISTINCT e.ID as Object_id, v.Id as ViewID
                               FROM FOLDER f
                               INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
                               INNER JOIN VIEW_OBJECTS vo on vo.view_id = v.Id
                               INNER JOIN ELEMENTS e on e.Id = vo.Object_id
                               WHERE f.Depth LIKE '%Service Realization Viewpoint%' AND e.Id = '{Object_id}'"""
                            )
    Views.add_report_segment(
        SegmentSQL("""SELECT '' as Blank1, '' as Blank2, v.Name as View_name
                        FROM VIEWS v
                        INNER JOIN VIEW_OBJECTS vo on vo.view_id = v.Id
                        INNER JOIN ELEMENTS e on e.Id = vo.Object_id
                        WHERE v.Id = '{ViewID}' AND e.Id = '{Object_id}'""")
    )

    Objects.set_substanza(Views)




    # AppearancesCount.report({})
    return AppearancesCount
