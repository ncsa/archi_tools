from reports import *

def undescribed_report(args):



    Folders  = StanzaFactory(args,
                             """SELECT ID
                                FROM RELATIONS
                                WHERE Type = 'AssociationRelationship'"""
    )
    Folders.add_report_segment(
        SegmentSQL("SELECT '{OutputType}' as OutputType, '{Total}' as Total, '{Undescribed}' as Undescribed, '{PercentUndescribed}' as PercentUndescribed ")
    )




    # Folders.report({})
    return Folders
