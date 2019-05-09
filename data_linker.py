import connector as c
import argparse
import shlog
import sqlite3
import networkx


def get_fire(args):
    # return a list of html files to nuke
    shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    # this query returns all views that have their paths matched with args.searchterm
    sql = """SELECT e.Id
             FROM ELEMENTS e
             INNER JOIN PROPERTIES p on p.ID = e.Id and p.Key = 'Fire'"""
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
    # this query returns all views that have their paths matched with args.searchterm
    sql = """SELECT ID
             FROM ELEMENTS
             WHERE Type = 'Node'"""
    shlog.verbose(sql)
    curs.execute(sql)
    rows = curs.fetchall()
    node_list = [x[0] for x in rows]
    return node_list



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
            for elem in pathway:
                print(c.get_elem_name(args, elem))
            print('\n\n')
            pass

    # print(c.link_short(args, '635bb685-bacb-43e3-b898-b7be4f94ed56', '711450b4-457b-4229-8e36-a501d464820d'))
    # print(c.link_short_all(args, '635bb685-bacb-43e3-b898-b7be4f94ed56', '711450b4-457b-4229-8e36-a501d464820d'))
    #
    #
    # a = c.link_all(args, '635bb685-bacb-43e3-b898-b7be4f94ed56', '711450b4-457b-4229-8e36-a501d464820d')
    # for entry in a:
    #     print(entry)
