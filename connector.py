import sqlite3
import shlog
import networkx as nx

def get_connections(args):
    # return a list of html files to nuke
    shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    # this query returns all views that have their paths matched with args.searchterm
    sql = """SELECT DISTINCT Source, Target
             FROM RELATIONS"""
    shlog.verbose(sql)
    curs.execute(sql)
    connection_list = curs.fetchall()
    return connection_list


def get_elements(args):
    # return a list of html files to nuke
    shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    # this query returns all views that have their paths matched with args.searchterm
    sql = """SELECT Id
             FROM ELEMENTS"""
    shlog.verbose(sql)
    curs.execute(sql)
    rows = curs.fetchall()
    element_list = [x[0] for x in rows]
    return element_list


def link_short(args, start, end):
    # prepare Graph
    elements = get_elements(args)
    connections = get_connections(args)

    # get all connections as tuples
    g = nx.Graph()
    g.add_nodes_from(elements)
    g.add_edges_from(connections)

    # get connection between two shortest
    return nx.shortest_path(g, start, end)

def link_short_all(args, start, end):
    # prepare Graph
    elements = get_elements(args)
    connections = get_connections(args)

    # get all connections as tuples
    g = nx.Graph()
    g.add_nodes_from(elements)
    g.add_edges_from(connections)

    # get connection between two shortest
    return [p for p in nx.all_shortest_paths(g, start, end)]


def link_all(args, start, end):
    # prepare Graph
    elements = get_elements(args)
    connections = get_connections(args)

    # get all connections as tuples
    g = nx.Graph()
    g.add_nodes_from(elements)
    g.add_edges_from(connections)

    # get connection between two shortest
    return [p for p in nx.all_simple_paths(g, start, end)]

###########################################################
#
# Main program
#
############################################################


# init logger
loglevel = shlog.VERBOSE
assert type(loglevel) == type(1)
shlog.basicConfig(level=shlog.VERBOSE)