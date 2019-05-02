from reports import *

def validate_undescribed_elements(args):


    # FInd what % of all elements are undescribed
    Folders  = StanzaFactory(args,
                             """WITH ViewIDs(ID) AS (SELECT r.Source as ID
                                FROM RELATIONS r
                                
                                UNION ALL

                                SELECT r.Target  as ID
                                FROM RELATIONS r),
                                
                                UniqueIDs(ID) AS (SELECT DISTINCT ID 
                                FROM ViewIDs
                                ),
                                
                                ElementIDs (Total, Undescribed) AS (SELECT 
                                count(e.ID) as Total,
                                SUM(CASE e.Documentation
                                    WHEN NULL THEN 1
                                    WHEN '' THEN 1
                                    ELSE 0
                                END) as Undescribed
                                FROM ELEMENTS e)
                                
                                SELECT 'All Elements' as OutputType, * , '=D2/C2' as PercentUndescribed
                                FROM ElementIDs
                                
                                UNION ALL
                                
                                SELECT 'Elements used in views' as OutputType, count(e.ID) as Total,
                                SUM(CASE e.Documentation
                                    WHEN NULL THEN 1
                                    WHEN '' THEN 1
                                    ELSE 0
                                END) as Undescribed, '=D3/C3' as PercentUndescribed
                                FROM ELEMENTS e
                                INNER JOIN UniqueIDs u on u.ID=e.ID"""
    )
    Folders.add_report_segment(
        SegmentSQL("SELECT '{OutputType}' as OutputType, '{Total}' as Total, '{Undescribed}' as Undescribed, '{PercentUndescribed}' as PercentUndescribed ")
    )




    # Folders.report({})
    return Folders
