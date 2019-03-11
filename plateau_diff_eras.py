from reports import *

def plateau_diff_eras(args):

    # enter table names separated by a semicolon (no spaces)
    FirstTable = 'Era:Dec2019'
    SecondTable = 'WBS:Spring2019'

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
                                WITH TWOVIEWS(View_id, name, Object_id, Key) AS (SELECT DISTINCT v.id as View_id, v.name, vo.Object_id, ifnull(p.Key, p1.Key) as Key
                                FROM VIEWS v
                                INNER JOIN VIEW_OBJECTS vo on vo.view_id = v.id
                                /*This is accomplished by joining the property table twice, each time for a matching p.Key*/
                                LEFT JOIN PROPERTIES p on p.id=v.id AND p.Key IN (%s)
                                LEFT JOIN PROPERTIES p1 on p1.id=v.id AND p1.Key IN (%r)
                                /*Ignore all rows where neither of the names match*/
                                /*this results in vo.Object_id and vo1.Object_id both being NULL when an element is present in neither of the views */
                                WHERE p.id IS NOT NULL or p1.id IS NOT NULL),

                                /*To get a list of elements exclusive to the first table, we self-join the TWOVIEWS table*/
                                FIRSTUNIQUE(name, Object_id, View_id) AS (SELECT t.name, t.Object_id, t.View_id
                                FROM TWOVIEWS t
                                /*self-join happens by Object_id and elements present in the second table are identified by its p.key value*/
                                LEFT JOIN TWOVIEWS t1 on t1.Object_id = t.Object_id AND t1.Key IN (%r)
                                /*Now we can get 1st table exclusives by identifying it by key and removing rows where there had been no 2nd table match*/
                                WHERE t.Key IN (%s) AND t1.Object_id IS NULL),
                                                                
                                /*SECONDUNIQUE is similar to FIRSTUNIQUE, except the keys are switched around*/
                                SECONDUNIQUE(name, Object_id, View_id) AS (SELECT t.name, t.Object_id, t.View_id
                                FROM TWOVIEWS t
                                LEFT JOIN TWOVIEWS t1 on t1.Object_id = t.Object_id AND t1.Key IN (%s) 
                                WHERE t.Key IN (%r) AND t1.Object_id IS NULL)
                                
                                /*Two tables with exclusives are combined into one*/
                                SELECT fu.Object_id, fu.Name as ModelName, fu.View_id
                                FROM FIRSTUNIQUE fu
                                UNION ALL
                                SELECT su.Object_id, su.Name as ModelName, su.View_id
                                FROM SECONDUNIQUE su""".replace('%s',FirstTable).replace('%r',SecondTable)
                            )
    Uniques.add_report_segment(
        SegmentSQL("""SELECT e.id as 'Element ID', f.Depth as 'Folder', e.Name as 'Element Name', e.Type, e.Documentation, '{ModelName}' as 'Uniquely present in', p.Key as 'Era'
                      FROM elements e
                      INNER JOIN PROPERTIES p on p.id = '{View_id}' AND (p.Key IN (%s) OR p.Key IN (%r))
                      LEFT JOIN FOLDER f on f.ID = e.ParentFolder
                      WHERE e.ID='{Object_id}'""".replace('%s',FirstTable).replace('%r',SecondTable))
    )


    # Folders.report({})
    return Uniques
