from reports import *

def validate_find_services(args):

    # This validation lists all Services for documentation improvement purposes
    ServiceList  = StanzaFactory(args,
                             """SELECT e.Name, p.Key, e.Documentation
                                FROM ELEMENTS e
                                LEFT JOIN PROPERTIES p on p.ID = e.ID and p.Key like 'Enc:%'
                                WHERE e.Type LIKE '%Service'"""
    )
    ServiceList.add_report_segment(
        SegmentSQL("""SELECT '{Name}' as InternalService, '{Key}' as Enclave, "{Documentation}" as Description """)
    )





    return ServiceList
