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
    # make a request
    # This dictionary has the ID #s for the asset types inside freshservice
    asset_dict = {"Artifact": "10001075124",
                  "DataObject": "10001075342"}
    try:
        if c.get_elem_type(args, elem).endswith('Artifact'):
            vol = search_assets("asset_tag", elem)["config_items"][0]["levelfield_values"]["bytes_%s" % asset_dict['Artifact']]
        else:
            vol = search_assets("asset_tag", elem)["config_items"][0]["levelfield_values"]["bytes_%s" % asset_dict['DataObject']]
    except:
        vol = 99999
    return vol


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

    # start logging
    con_log = {}
    head_toggle = True
    os.remove("CapacityReport 2.csv")
    csv = pd.read_csv("CapacityReport.csv")

    for fire_to_node in fire_to_node_links:
        for pathway in fire_to_node:

            # create an entry for the firing element if not yet logged:
            if pathway[0] not in list(con_log.keys()):
                con_log[pathway[0]] = {}
            # create a dict entry for the target node
            if pathway[-1] not in list(con_log[pathway[0]].keys()):
                con_log[pathway[0]][pathway[-1]] = {}

            full_path = ""
            # USEFUL: get the connection that lead up to this element
            prev = None
            prev_proc = None
            for elem in pathway:
                # get element type to not make repeated requests
                e_type = c.get_elem_type(args, elem)

                if prev is not None:
                    # if there's something in prev, continue mapping
                    connection = get_connection_info(args, prev, elem)
                    full_path += ' >--' + connection[1] + ' (' + connection[0] + ')--> '  + c.get_elem_name(args, elem)
                else:
                    # if nothing is prev, that means we're looking at the first element
                    full_path = c.get_elem_name(args, elem)

                # log an artifact or data object
                if e_type.endswith('DataObject') or e_type.endswith('Artifact'):
                    # create a data obj key
                    if elem not in list(con_log[pathway[0]][pathway[-1]].keys()):
                        con_log[pathway[0]][pathway[-1]][elem] = {'Bytes':0, 'Process':''}
                    # make a byte volume request
                    if con_log[pathway[0]][pathway[-1]][elem]['Bytes'] == 0:
                        con_log[pathway[0]][pathway[-1]][elem]['Bytes'] = get_era_volume(args, elem, None)
                        print(get_calls.counter)
                    # write backtracked process
                    if con_log[pathway[0]][pathway[-1]][elem]['Process'] == '':
                        con_log[pathway[0]][pathway[-1]][elem]['Process'] = prev_proc

                    d = {"Fire": [c.get_elem_name(args, pathway[0])],
                         "Node": [c.get_elem_name(args, pathway[-1])],
                         "Data Object": [c.get_elem_name(args, elem)],
                         "Bytes": [con_log[pathway[0]][pathway[-1]][elem]['Bytes']],
                         "Process": [c.get_elem_name(args, con_log[pathway[0]][pathway[-1]][elem]['Process'])],
                         "Full Path": full_path}
                    df = pd.DataFrame(data=d, columns=["Fire", "Node", "Data Object", "Bytes", "Process", "Full Path"], index=None)
                    with open('CapacityReport 2.csv', 'a') as f:
                        df.to_csv(f, header=head_toggle, index=head_toggle)
                    # stop writing headers after the first one had been written
                    head_toggle = False


                # save the most recent process to backtrack to it later
                if e_type.endswith('Process'):
                    prev_proc = elem
                prev = elem

