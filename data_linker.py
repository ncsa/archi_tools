import connector as c
import argparse
import shlog
import sqlite3
import networkx
import requests
import json
import pandas as pd
import os

# freshservice api settings
api_key = "sekrit"
api_key = 'TNerBTBFAK7fdJSKEh'
domain = "ncsa-at-illinois"

def get_calls():
   """Returns number of API calls made in Python session
   """
   get_calls.counter += 1


get_calls.counter = 0

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
    if search.status_code == 403:
        print(search.content)
        input("Continue?")
    get_calls()
    return json.loads(search.content)

def get_fire(args):
    # return a list of html files to nuke
    shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    # this query returns all views that have their paths matched with args.searchterm
    if args.search_term is None:
        sql = """SELECT Source as Id
                 FROM RELATIONS r
                 INNER JOIN ELEMENTS e1 on e1.ID = Source
                 INNER JOIN ELEMENTS e2 on e2.ID = Target
                 WHERE e1.Type = 'BusinessEvent' AND e2.Type = 'ApplicationProcess' AND r.Type = 'TriggeringRelationship'"""
    else:
        sql = """WITH triggers(Id) AS (SELECT Source as Id
                 FROM RELATIONS r
                 INNER JOIN ELEMENTS e1 on e1.ID = Source
                 INNER JOIN ELEMENTS e2 on e2.ID = Target
                 WHERE e1.Type = 'BusinessEvent' AND e2.Type = 'ApplicationProcess' AND r.Type = 'TriggeringRelationship')
                 SELECT DISTINCT Object_id as Id
                 FROM FOLDER f
                 INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
                 INNER JOIN VIEW_OBJECTS vo on v.Id = vo.View_id
				 INNER JOIN triggers t on t.Id = vo.Object_id
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


def get_era_volume(args, elem):
    # make a request
    # This dictionary has the ID #s for the asset types inside freshservice
    try:
        asset = search_assets("asset_tag", "f_" + elem)
        volumes_list = asset["config_items"][0]["levelfield_values"]
    except:
        # return false byte values if we couldn't retrieve
        for era in c.get_all_eras(args):
            volumes_list[era] = u'0'
    return volumes_list


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


def node_hop_check(args, path):
    """Checks if any node hopping accurs in a pathway
       Returns True and False"""
    for elem in path:
        if c.get_elem_type(args, elem) == 'Node' and elem != path[-1]:
            # print(c.get_elem_name(args, elem) + ' is not ' + c.get_elem_name(args, path[-1]))
            return True
    # if we got here, that means that the node check had not failed once.
    return False


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
            no_node_hoppers = []
            try:
                link_checker = [c.link_short_all(args, fire, node, True)]
                for path in link_checker[0]:
                    if node_hop_check(args, path) == False:
                        no_node_hoppers.append(path)
            except networkx.exception.NetworkXNoPath:
                shlog.verbose(fire + ' cannot reach ' + node)
            if no_node_hoppers != []:
                fire_to_node_links.append(no_node_hoppers)

    # start logging
    con_log = {}
    head_toggle = True
    try:
        os.remove("CapacityReport 2.csv")
    except OSError:
        print('Warning: CapacityReport 2.csv does not exist, ignoring..')

    for fire_to_node in fire_to_node_links:
        for pathway in fire_to_node:

            # create an entry for the firing element if not yet logged:
            if pathway[0] not in list(con_log.keys()):
                con_log[pathway[0]] = {}
            # create a dict entry for the target node
            if pathway[-1] not in list(con_log[pathway[0]].keys()):
                con_log[pathway[0]][pathway[-1]] = {}

            # debug: actual full path under investigation
            d_path = ''
            d_prev = None
            for d_elem in pathway:
                if d_prev is not None:
                    # if there's something in prev, continue mapping
                    connection = get_connection_info(args, d_prev, d_elem)
                    d_path += ' >--' + connection[1] + ' (' + connection[0] + ')--> ' + c.get_elem_name(args, d_elem)
                else:
                    # if nothing is prev, that means we're looking at the first element
                    d_path = c.get_elem_name(args, d_elem)
                d_prev = d_elem


            full_path = ""
            # USEFUL: get the connection that lead up to this element
            prev = None
            prev_proc = None
            for elem in pathway:
                # get element type to not make repeated requests
                e_type = c.get_elem_type(args, elem)
                # full path logging happens here
                if prev is not None:
                    # if there's something in prev, continue mapping
                    connection = get_connection_info(args, prev, elem)
                    full_path += ' >--' + connection[1] + ' (' + connection[0] + ')--> '  + c.get_elem_name(args, elem)
                else:
                    # if nothing is prev, that means we're looking at the first element
                    full_path = c.get_elem_name(args, elem)
                prev = elem

                # save the most recent process to backtrack to it later
                if e_type.endswith('Process'):
                    prev_proc = elem

                # cancel any further handling (which is all about data) if the fire, node, object, and process match
                # this will eliminate duplicates, but will result in only the very first path being listed and credited
                try:
                    if pathway[0] in list(con_log.keys()) and pathway[-1] in list(con_log[pathway[0]].keys()) \
                            and con_log[pathway[0]][pathway[-1]][elem]['Process'] == prev_proc \
                            and elem in list(con_log[pathway[0]][pathway[-1]].keys()):
                        break
                except KeyError:
                    # KeyError is caused by con_log[pathway[0]][pathway[-1]][elem]['Process'], namely [elem] not
                    # being present. Continue as normal.
                    pass

                # log an artifact or data object
                if e_type.endswith('DataObject') or e_type.endswith('Artifact'):
                    # create a data obj key
                    if elem not in list(con_log[pathway[0]][pathway[-1]].keys()):
                        con_log[pathway[0]][pathway[-1]][elem] = {'Process':''}
                    # make a byte volume request
                    # if con_log[pathway[0]][pathway[-1]][elem]['Bytes'] == 0:
                    #     con_log[pathway[0]][pathway[-1]][elem]['Bytes'] = get_era_volume(args, elem, None)
                    #     print(get_calls.counter)
                    # write backtracked process
                    if con_log[pathway[0]][pathway[-1]][elem]['Process'] == '':
                        con_log[pathway[0]][pathway[-1]][elem]['Process'] = prev_proc

                    # entries are written in three parts to allow for a dynamic dict size
                    # write fire, node, data object to the dict
                    d = {"Fire": [c.get_elem_name(args, pathway[0])],
                         "Node": [c.get_elem_name(args, pathway[-1])],
                         "Data Object": [c.get_elem_name(args, elem)]
                         # "Bytes": [con_log[pathway[0]][pathway[-1]][elem]['Bytes']],
                         }
                    # write bytes
                    volumes = get_era_volume(args, elem)
                    for era in list(volumes.keys()):
                        if 'bytes' in era or 'era' in era:
                            d[era] = [volumes[era]]
                    print('API calls made: ' + str(get_calls.counter))
                    # write full path
                    d["Process"] = [c.get_elem_name(args, con_log[pathway[0]][pathway[-1]][elem]['Process'])]
                    # d["Full Path"] = full_path
                    d["Full Path"] = d_path

                    df = pd.DataFrame(data=d, columns=list(d.keys()), index=None)
                    with open('CapacityReport 2.csv', 'a') as f:
                        df.to_csv(f, header=head_toggle, index=head_toggle)
                    # stop writing headers after the first one had been written
                    head_toggle = False


