from reports import *

def responsibility_report(args):


    Groupings  = StanzaFactory(args,
                             """SELECT DISTINCT e1.Name, e1.ID, e1.Documentation as Docs
                                FROM ELEMENTS e1
                                WHERE e1.Type = 'Grouping'"""
    )
    Groupings.add_report_segment(
        SegmentSQL("SELECT '{Name}' as 'Role', ' ' as 'Object Name', ' ' as Type, '{Docs}' as Documentation")
    )


    Elements = StanzaFactory(args, """SELECT DISTINCT e.Name as EName, e.Type, e.Documentation
                                      FROM RELATIONS r
                                      INNER JOIN ELEMENTS e on e.ID = r.Target
                                      WHERE r.Source = '{ID}'"""
    )
    Elements.add_report_segment(
        SegmentSQL("""SELECT ' ' as Blank, '{EName}' as Name, '{Type}' as Type, '{Documentation}' as Documentation""")
    )

    Groupings.set_substanza (Elements)


    return Groupings
