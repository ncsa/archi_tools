from reports import *

search = 'HSCCam Processing Data Managment View'

def cmdb_export_relations(args):

    # This report will identify all relations due for export in the specified view
    Relations  = StanzaFactory(args,
                             """SELECT DISTINCT c.connection_id, r.Type, r.Name, r.Documentation, r.Source, r.Target
                                FROM VIEWS v
                                INNER JOIN VIEW_OBJECTS vo on vo.View_id = v.Id
                                INNER JOIN CONNECTIONS c on c.view_id = v.Id
                                INNER JOIN RELATIONS r on r.ID = c.relationship_id
                                /* join elements both to source and target to leave in only compliant elements and their relations */
                                INNER JOIN ELEMENTS e1 on e1.ID = r.Source
                                INNER JOIN ELEMENTS e2 on e2.ID = r.Target
                                WHERE v.Name = 'F1LL3R'
                                and (e1.Type = 'Node' or e1.Type like 'Application%' or e1.Type like 'Technology%' or e1.Type = 'Artifact')
                                and (e2.Type = 'Node' or e2.Type like 'Application%' or e2.Type like 'Technology%' or e2.Type = 'Artifact')""".replace('F1LL3R', search)
    )
    Relations.add_report_segment(
        SegmentSQL("""SELECT '{connection_id}' as ID, '{Type}' as Type, '{Name}' as Name, '{Documentation}' as Documentation, '{Source}' as Source, '{Target}' as Target """)
    )



    return Relations
