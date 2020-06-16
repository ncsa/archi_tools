from reports import *

search = [
          'FY2025 CMB-S4 Transient Detection Offline Data Management View',
          'FY2025 CMB-S4 Transient Detection Online Data Management View',
          'FY2026 CMB-S4 Transient Detection Offline Data Management View',
          'FY2026 CMB-S4 Transient Detection Online Data Management View '
         ]

def cmdb_WBS(args):
    Views  = StanzaFactory(args,
"""SELECT v.ID as vID
FROM VIEWS v
WHERE 
v.Name like '%s' 
or v.Name like '%s'
or v.Name like '%s'
or v.Name like '%s'
""" % (search[0],
       search[1],
       search[2],
       search[3]
      )
)

    Views.add_report_segment(
        SegmentSQL(
            "SELECT '' as DeleteThisRow, '' as Drawing, '' as WBS, '' as Component, '' as Description")
    )


    

    Elements = StanzaFactory(args,
"""SELECT v.Name as Drawing, gr.Name as WBS, e.Name as Component, e.Documentation as Description
FROM VIEWS v
INNER JOIN VIEW_OBJECTS vo on v.Id = vo.View_id
INNER JOIN ELEMENTS e on e.ID = vo.Object_id
INNER JOIN ELEMENTS gr on gr.ID = vo.Container_id
WHERE v.ID = '{vID}'
and e.Type not like 'Grouping'"""
                             )
    Elements.add_report_segment(
        SegmentSQL("SELECT '' as blah, '{Drawing}' as Drawing, '{WBS}' as WBS, '{Component}' as Component, '{Description}' as Description")
    )

    Views.set_substanza(Elements)


    return Views
