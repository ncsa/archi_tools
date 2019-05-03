from reports import *

def plateau_diff(args):

    # This report diffs two sets of views and checks plateau presence of difference
    # enter table names separated by a semicolon (no spaces)
    FirstTable = 'Data Backbone Application Behavior to Provisioning Map View'
    SecondTable = 'dummy'

    FirstIn = FirstTable.split(";")
    SecondIn = SecondTable.split(";")

    FirstTable = "'"
    for table in FirstIn:
        FirstTable += table + "', '"
    FirstTable = FirstTable[:-3]

    SecondTable = "'"
    for table in SecondIn:
        SecondTable += table + "', '"
    SecondTable = SecondTable[:-3]

    Uniques = StanzaFactory(args,
                            """/*First, we need to get ALL the elements present in EITHER view*/
                                WITH TWOVIEWS(View_id, name, Object_id) AS (SELECT DISTINCT v.id as View_id, v.name, ifnull(vo.Object_id, vo1.Object_id) AS Object_id
                                FROM VIEWS v
                                /*This is accomplished by joining the table with a view's object list twice, each time for a matching v.name (model name)*/
                                LEFT JOIN VIEW_OBJECTS vo on vo.view_id = v.id AND v.name IN (%s)
                                LEFT JOIN VIEW_OBJECTS vo1 on vo1.view_id = v.id AND v.name IN (%r)
                                /*Ignore all rows where neither of the names match*/
                                /*this results in vo.Object_id and vo1.Object_id both being NULL when an element is present in neither of the views */
                                WHERE vo1.Object_id IS NOT NULL or vo.Object_id IS NOT NULL),
                                
                                /*To get a list of elements exclusive to the first table, we self-join the TWOVIEWS table*/
                                FIRSTUNIQUE(name, Object_id) AS (SELECT t.name, t.Object_id
                                FROM TWOVIEWS t
                                /*self-join happens by Object_id and elements present in the second table are identified by the name*/
                                LEFT JOIN TWOVIEWS t1 on t1.Object_id = t.Object_id AND t1.name IN (%r) 
                                /*Now we can get 1st table exclusives by identifying it by name and removing rows where there had been no 2nd table match*/
                                WHERE t.Name IN (%s) AND t1.Object_id IS NULL),
                                
                                /*SECONDUNIQUE is similar to FIRSTUNIQUE, except the names are switched around*/
                                SECONDUNIQUE(name, Object_id) AS (SELECT t.name, t.Object_id
                                FROM TWOVIEWS t
                                LEFT JOIN TWOVIEWS t1 on t1.Object_id = t.Object_id AND t1.name IN (%s)
                                WHERE t.Name IN (%r) AND t1.Object_id IS NULL)
                                
                                /*Two tables with exclusives are combined into one*/
                                SELECT fu.Object_id, fu.Name as ModelName 
                                FROM FIRSTUNIQUE fu
                                UNION ALL
                                SELECT su.Object_id, su.Name
                                FROM SECONDUNIQUE su""".replace('%s',FirstTable).replace('%r',SecondTable)
                            )
    Uniques.add_report_segment(
        SegmentSQL("""SELECT e.id as 'Element_ID', f.Depth as 'Folder', e.Name as 'Element Name', e.Type, e.Documentation, '{ModelName}' as 'Uniquely present in'
                      FROM elements e
                      LEFT JOIN FOLDER f on f.ID = e.ParentFolder
                      WHERE e.ID='{Object_id}'""")
    )

    Uniques.add_report_segment(
        SegmentSQL(
            """SELECT 'x'
               FROM RELATIONS r
               INNER JOIN ELEMENTS e on e.ID = r.Source
               WHERE e.Name= '{PlateauName}'
               AND r.Target = '{Object_id}'
               AND r.Type = 'CompositionRelationship'""",
            context=QueryContext(args,
                                 "SELECT Name as PlateauName FROM ELEMENTS WHERE Type = 'Plateau'")
        )
    )


    return Uniques
