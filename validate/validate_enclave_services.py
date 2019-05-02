from reports import *

def validate_enclave_services(args):

    # This validation lists all Services within their respective enclaves
    # if you want more: e.Type like '%Function' or e.Type like '%Process' or e.Type like '%Process' or e.Type like '%Service'
    Enclaves  = StanzaFactory(args,
                             """SELECT DISTINCT Enclave_id
                                FROM ENCLAVE_CONTENT ec
                                INNER JOIN ELEMENTS e on e.Id=ec.Object_id
                                WHERE e.Type like '%Service'"""
    )
    Enclaves.add_report_segment(
        SegmentSQL("""SELECT e.Name || " @ " || e.Location as Enclave, '' as Element, '' as Description
                        FROM ENCLAVES e 
                        WHERE e.Id = '{Enclave_id}' """)
    )


    EnclaveContent = StanzaFactory(args, """SELECT DISTINCT e.Id as Element_id
                                            FROM ENCLAVE_CONTENT ec
                                            INNER JOIN ELEMENTS e on e.Id=ec.Object_id
                                            WHERE e.Type like '%Service'
                                            AND ec.Enclave_id = '{Enclave_id}'""")
    EnclaveContent.add_report_segment(
        SegmentSQL(
            """SELECT '' as Blank, Name, Documentation FROM ELEMENTS WHERE Id = '{Element_id}' """)
    )

    Enclaves.set_substanza(EnclaveContent)



    # Enclaves.report({})
    return Enclaves
