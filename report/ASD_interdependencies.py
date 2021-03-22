from reports import *

def ASD_interdependencies(args):

    # Identify view objects that appear in multiple Service Teams
    Objects  = StanzaFactory(args,
                             """WITH qualified_views(Id) AS (SELECT v.Id
FROM FOLDER f
INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
WHERE f.Depth like '%. %')

SELECT vo.Name as NAM, Object_id as OBJ, count(DISTINCT SUBSTR(v.Name,1,INSTR(v.Name,' ') -1)) as cnt
FROM VIEW_OBJECTS as vo
inner join views v on v.id = vo.view_id
WHERE Object_id is not NULL and vo.view_id in (SELECT Id FROM qualified_views)
GROUP BY vo.Name
HAVING cnt > 1
ORDER BY cnt DESC
"""
    )

    # Print Name and add an empty column for title
    Objects.add_report_segment(
        SegmentSQL("SELECT '{NAM}' as Name, '' as Appearance")
    )

    # substanza defined below
    
    # Get views where this object appears
    SuspectViews = StanzaFactory(args,
                             """WITH qualified_views(Id) AS (SELECT v.Id
FROM FOLDER f
INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
WHERE f.Depth like '%. %')

SELECT v.Id as VIE
FROM VIEW_OBJECTS vo
INNER JOIN VIEWS v on v.Id = vo.view_id
WHERE Object_id = '{OBJ}' and vo.view_id in (SELECT Id FROM qualified_views)"""
    )

    # Fetch view Names
    SuspectViews.add_report_segment(
        SegmentSQL("""SELECT ' ' as  Buffer,  Name
FROM VIEWS
WHERE Id = '{VIE}'
        """)
    )


    # Tell the report engine that the aforementioned stana is a substanza
    Objects.set_substanza (SuspectViews)


    return Objects