from reports import *

search = 'HSCCam Processing Data Managment View'

def cmdb_export_elements(args):

    # This report will identify all elements due for export in the specified view
    Elements  = StanzaFactory(args,
                             """SELECT DISTINCT e.ID, e.Type, e.Name, e.Documentation
                                FROM VIEWS v
                                INNER JOIN VIEW_OBJECTS vo on vo.View_id = v.Id
                                INNER JOIN ELEMENTS e on e.ID = vo.Object_id
                                WHERE v.Name = 'F1LL3R'
                                and (e.Type = 'Node' or e.Type like 'Application%' or e.Type like 'Technology%' or e.Type = 'Artifact')""".replace('F1LL3R', search)
    )
    Elements.add_report_segment(
        SegmentSQL("""SELECT '{ID}' as ID, '{Type}' as Type, '{Name}' as Name, '{Documentation}' as Documentation""")
    )



    return Elements
