from reports import *

def prefill_list_data(args):

    # This is a test folder+element demo report that shows off basic functionality

    Folders  = StanzaFactory(args,
                             """SELECT DISTINCT e.Id as ElementID, e.Name
                                FROM VIEWS v
                                INNER JOIN FOLDER f on f.id = v.Parent_folder_id
                                INNER JOIN VIEW_OBJECTS vo on vo.view_id = v.Id
                                INNER JOIN ELEMENTS e on e.Id = vo.Object_id
                                WHERE f.Name like '%Data Management Viewpoint%' and (e.Type = 'DataObject' or e.Type = 'Artifact')"""
    )
    Folders.add_report_segment(
        SegmentSQL("SELECT '{ElementID}' as ID, '{Name}' as Name")
    )
    Folders.add_report_segment(
        SegmentSQL("SELECT ''",
                   context=QueryContext(args,
                                        "SELECT EraID FROM ERAS")
                   )
    )


    return Folders #3
