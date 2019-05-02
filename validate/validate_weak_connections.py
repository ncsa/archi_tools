from reports import *

def validate_weak_connections(args):


    # Find the weakest, straight-line connections
    Views  = StanzaFactory(args,
                             """SELECT id as view_id
                                FROM VIEWS"""
    )
    Views.add_report_segment(
        SegmentSQL("""SELECT Id as view_id, Name, Documentation
                      FROM VIEWS v
                      WHERE v.id = '{view_id}'""")
    )


    Connections  = StanzaFactory(args,
                             """SELECT Source, Target
                                FROM CONNECTIONS c
                                INNER JOIN RELATIONS r on r.ID = c.relationship_id
                                where r.type = 'AssociationRelationship'
                                AND c.view_id = '{view_id}'"""
    )
    Connections.add_report_segment(
        SegmentSQL("""SELECT ' ' as Blank, e.Name, e1.Name
                      FROM ELEMENTS e
                      INNER JOIN ELEMENTS e1 on e1.ID = '{Source}'
                      WHERE e.ID = '{Target}'""")
    )

    Views.set_substanza(Connections)

    # Views.report({})
    return Views
