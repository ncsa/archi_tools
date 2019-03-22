from reports import *

def validate_view_elements(args):

    Search_term = 'Service Data Management Viewpoint'


    Folders  = StanzaFactory(args,
                             """SELECT DISTINCT e.Type
                                FROM FOLDER f
                                INNER JOIN VIEWS v on v.Parent_folder_id = f.ID
                                INNER JOIN VIEW_OBJECTS vo on vo.View_id = v.ID
                                INNER JOIN ELEMENTS e on e.ID = vo.Object_id
                                WHERE f.Depth LIKE '%R3PL4C3M3%'""".replace('R3PL4C3M3', Search_term)
    )
    Folders.add_report_segment(
        SegmentSQL("SELECT '{Type}' as Type ")
    )




    # Folders.report({})
    return Folders
