from reports import *

def validate_process_provis(args):

    ViewName = 'Data Backbone Application Behavior to Provisioning Map View'
    ProvisioningFolderName = 'Service to Provisioning Map Viewpoint'


    Processes = StanzaFactory(args,
                            """SELECT e.Id as Element
                               FROM VIEWS v
                               INNER JOIN VIEW_OBJECTS vo on vo.view_id = v.ID
                               INNER JOIN ELEMENTS e on e.Id = vo.Object_id
                               WHERE v.Name = '%s'
                               AND e.Type LIKE '%Process%'""".replace('%s', ViewName)
                            )
    Processes.add_report_segment(
        SegmentSQL("""SELECT e.Id, e.Name, e.Type, e.Documentation
                      FROM ELEMENTS e
                      WHERE e.Id = '{Element}'""")
    )

    Processes.add_report_segment(
        SegmentSQL(
            """SELECT 'x'
               FROM VIEWS v
               INNER JOIN VIEW_OBJECTS vo on vo.view_id = v.Id
               WHERE v.name = '{ViewName}'
               AND vo.Object_id = '{Element}'""",
            context=QueryContext(args,
                                 """SELECT v.Name as ViewName
                                    FROM VIEWS v
                                    INNER JOIN FOLDER f on f.Id = v.Parent_folder_id
                                    WHERE f.Name = '%s'""" % ProvisioningFolderName)
        )
    )


    # Folders.report({})
    return Processes
