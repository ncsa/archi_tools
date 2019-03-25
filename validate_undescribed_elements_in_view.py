from reports import *

def validate_undescribed_elements(args):

    View = 'Non L1 Base View'


    Views  = StanzaFactory(args,
                             """SELECT id as view_id
                                FROM VIEWS
                                WHERE name = '%s' """ % View
    )
    Views.add_report_segment(
        SegmentSQL("""SELECT Id as view_id, Name, Documentation
                      FROM VIEWS v
                      WHERE v.id = '{view_id}'""")
    )


    Connections  = StanzaFactory(args,
                             """SELECT e.Name
                                FROM VIEW_OBJECTS vo
                                INNER JOIN ELEMENTS e on e.ID = vo.Object_id
                                WHERE vo.view_id = '{view_id}'
                                AND (e.Documentation IS NULL OR e.Documentation = '')"""
    )
    Connections.add_report_segment(
        SegmentSQL("""SELECT ' ' as Blank, '{Name}' as Name
					  """)
    )

    Views.set_substanza(Connections)

    # Views.report({})
    return Views
