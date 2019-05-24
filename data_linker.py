import connector as c
import argparse
import shlog
import sqlite3
import networkx
import requests
import json

api_key = "sekrit"

domain = "ncsa-at-illinois"


def search_assets(field_param, query_param):
    """Search items in the freshservice CMDB

    Parameters
    ----------
    field_param: str
        Specifies which field should be used to search for an asset. Allowed parameters
        are 'name', 'asset_tag', or 'serial_number'.
    query_param: str
        What you would like to search for based off of the field_param. For example,
        field_param="name", query_param="andrea".
    """
    headers = {'Content-Type': 'application/json'}
    search = requests.get(
        "https://{domain}.freshservice.com/cmdb/items/list.json?field={field_param}&q={query_param}".replace('{domain}',
                                                                                                             domain).replace(
            '{field_param}', field_param).replace('{query_param}', query_param), headers=headers,
        auth=(api_key, "1234"))
    return json.loads(search.content)


def get_fire(args):
    # return a list of html files to nuke
    shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    # this query returns all views that have their paths matched with args.searchterm
    if args.search_term is None:
        sql = """SELECT e.Id
                 FROM ELEMENTS e
                 INNER JOIN PROPERTIES p on p.ID = e.Id and p.Key = 'Fire'"""
    else:
        sql = """SELECT DISTINCT Object_id as Id
                 FROM FOLDER f
                 INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
                 INNER JOIN VIEW_OBJECTS vo on v.Id = vo.View_id
				 INNER JOIN ELEMENTS e on e.Id = vo.Object_id
                 INNER JOIN PROPERTIES p on p.ID = e.Id and p.Key = 'Fire'
				 WHERE f.Depth like '%F1LL3R%'""".replace('F1LL3R', str(args.search_term))
    shlog.verbose(sql)
    curs.execute(sql)
    rows = curs.fetchall()
    fire_list = [x[0] for x in rows]
    return fire_list

def get_nodes(args):
    # return a list of html files to nuke
    shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    if args.search_term is None:
        # this query returns all views that have their paths matched with args.searchterm
        sql = """SELECT ID
                 FROM ELEMENTS
                 WHERE Type = 'Node'"""
    else:
        sql = """SELECT DISTINCT Object_id as Id
                 FROM FOLDER f
                 INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
                 INNER JOIN VIEW_OBJECTS vo on v.Id = vo.View_id
				 INNER JOIN ELEMENTS e on e.Id = vo.Object_id
				 WHERE f.Depth like '%F1LL3R%' and e.Type = 'Node'""".replace('F1LL3R', str(args.search_term))
    shlog.verbose(sql)
    curs.execute(sql)
    rows = curs.fetchall()
    node_list = [x[0] for x in rows]
    return node_list


def get_era_volume(args, elem, era):
    # make a sql request to get volume of information passed in an era
    # shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    # this query returns all views that have their paths matched with args.searchterm
    sql = """SELECT DISTINCT p.Value
             FROM ELEMENTS e
			 INNER JOIN PROPERTIES p on p.Id = e.Id and p.Key = 'PL4C4H0L'
             WHERE e.ID = 'F1LL3R'""".replace('F1LL3R', elem).replace('PL4C4H0L', era)
    # shlog.verbose(sql)
    curs.execute(sql)
    rows = curs.fetchall()
    # should return one element
    try:
        volume = int(rows[0][0])
    except IndexError:
        return 0
    return volume


def get_connection_info(args, source, target):
    # make a sql request to get info about the relation
    # make a sql request to get volume of information passed in an era
    # shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    # this query returns all views that have their paths matched with args.searchterm
    sql = """SELECT Type, Name
             FROM RELATIONS
             WHERE (Source = 'F1LL3R1' AND Target = 'F1LL3R2')
             or (Source = 'F1LL3R2' AND Target = 'F1LL3R1')
             LIMIT 1""".replace('F1LL3R1', source).replace('F1LL3R2', target)
    # shlog.verbose(sql)
    curs.execute(sql)
    rows = curs.fetchall()
    # should return one element
    try:
        volume = rows[0]
    except IndexError:
        return 0
    return volume


if __name__ == "__main__":

    main_parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter)
    main_parser.add_argument("--dbfile", "-d",
                                 help='full name of the *.db file to use as data source',
                                 default="LSST_archi_tool.db")
    main_parser.add_argument("--search_term", "-s", help="specify a search term to search in the folder hierarchy to "
                                                         "ingest connections only form a desired set of view",
                             default=None)
    args = main_parser.parse_args()

    fire_sources = get_fire(args)
    target_nodes = get_nodes(args)

    fire_to_node_links = []
    # loop through elements and calculate possible routes between them and nodes
    for fire in fire_sources:
        for node in target_nodes:
            link_checker = []
            try:
                link_checker = [c.link_short_all(args, fire, node)]
                pass
            except networkx.exception.NetworkXNoPath:
                shlog.verbose(fire + ' cannot reach ' + node)
            if link_checker != []:
                fire_to_node_links.append(link_checker[0])
    for fire_to_node in fire_to_node_links:
        for pathway in fire_to_node:
            print('Source: ' + c.get_elem_name(args, pathway[0]) + ' // Target: ' + c.get_elem_name(args, pathway[-1]))

            # USEFUL: generate empty dict for eras
            era_dict = {}
            for i in c.get_all_eras(args):
                era_dict[i] = []

            # USEFUL: get the connection that lead up to this element
            prev = None
            for elem in pathway:


                # USEFUL: get the connection that lead up to this element
                if prev is not None:
                    connection = get_connection_info(args, prev, elem)
                    print('>>> ' + connection[1] + ' (' + connection[0] + ') >>>')
                # prepare for the next connection loop
                prev = elem

                print(c.get_elem_name(args, elem))

                e_type = c.get_elem_type(args, elem)

                # USEFUL: catch processes and their types
                if e_type.endswith('Process'):
                    print('Process detected. ')
                    # USEFUL: get all eras associated with the activity
                    # can make calls and separate
                    for i in c.get_elem_eras(args, elem):
                        print('Era Detected: ' + i)

                # Useful: catch artifacts and Data objectCONNECTIONS
                if e_type.endswith('DataObject') or e_type.endswith('Artifact'):
                    print('Data detected')
                    for era in list(era_dict.keys()):
                        era_vol = get_era_volume(args, elem, era)
                        era_dict[era].append(era_vol)
                        print(era + ': ' + str(era_vol))

            for era in list(era_dict.keys()):
                total = 0
                for volume in era_dict[era]:
                    total += volume
                print('Bytes collected in Era ' + era + ': ' + str(total * c.get_era_fires(args, era)))



            print('\n\n')
            pass

    # print(c.link_short(args, '635bb685-bacb-43e3-b898-b7be4f94ed56', '711450b4-457b-4229-8e36-a501d464820d'))
    # print(c.link_short_all(args, '635bb685-bacb-43e3-b898-b7be4f94ed56', '711450b4-457b-4229-8e36-a501d464820d'))
    #
    #
    # a = c.link_all(args, '635bb685-bacb-43e3-b898-b7be4f94ed56', '711450b4-457b-4229-8e36-a501d464820d')
    # for entry in a:
    #     print(entry)
