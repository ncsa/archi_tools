# coding=utf-8
import sqlite3
import shlog
import networkx as nx


def get_connections(args):
    # return a list of html files to nuke
    shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    # this query returns all connections that have their paths matched with args.search_term
    if args.search_term is None:
        # get all unique relations if no search_term flag had been passed
        sql = """SELECT DISTINCT Source, Target
                 FROM RELATIONS"""
    else:
        # else, put it to good use
        sql = """SELECT DISTINCT Source, Target
                 FROM VIEWS v
                 INNER JOIN FOLDER f on f.id = v.Parent_folder_id
                 INNER JOIN CONNECTIONS c on c.view_id = v.id
                 INNER JOIN RELATIONS r on r.Id = c.relationship_id
                 INNER JOIN ELEMENTS e1 on e1.ID = r.Source
				 INNER JOIN ELEMENTS e2 on e2.ID = r.Target
                 WHERE f.Depth LIKE '%F1LL3R%' AND e1.Type <> 'Contract' AND e2.Type <> 'Contract' AND e1.Type <> 'BusinessEvent' AND e2.Type <> 'BusinessEvent' """.replace('F1LL3R', str(args.search_term))
    shlog.verbose(sql)
    curs.execute(sql)
    connection_list = curs.fetchall()
    return connection_list


def get_elements(args):
    # return a list of html files to nuke
    shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    if args.search_term is None:
        # get all relations if no search_term flag had been passed
        sql = """SELECT Id
                 FROM ELEMENTS"""
    else:
        sql = """SELECT DISTINCT Object_id as Id
                 FROM FOLDER f
                 INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
                 INNER JOIN VIEW_OBJECTS vo on v.Id = vo.View_id
                 WHERE f.Depth like '%F1LL3R%'""".replace('F1LL3R', str(args.search_term))

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

def get_elem_name(args, elem):
    # make a sql request to get element name though it's ID
    # shlog.normal("about to open %s", args.dbfile)
    if elem is None:
        return 'None'
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    # this query returns the name of the supplied element ID
    sql = """SELECT Name
             FROM ELEMENTS
             WHERE ID = 'F1LL3R'""".replace('F1LL3R', elem)
    # shlog.verbose(sql)
    curs.execute(sql)
    rows = curs.fetchall()
    # should return one element
    try:
        elem_name = rows[0][0]
    except IndexError:
        return ''
    return elem_name


def get_elem_type(args, elem):
    # make a sql request to get element name though it's ID
    # shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    # this query returns all views that have their paths matched with args.searchterm
    sql = """SELECT Type
             FROM ELEMENTS
             WHERE ID = 'F1LL3R'""".replace('F1LL3R', elem)
    # shlog.verbose(sql)
    curs.execute(sql)
    rows = curs.fetchall()
    # should return one element
    try:
        elem_type = rows[0][0]
    except IndexError:
        return ''
    return elem_type


def get_elem_eras(args, elem):
    # make a sql request to get element name though it's ID
    # shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    # this query returns all views that have their paths matched with args.searchterm
    sql = """SELECT DISTINCT p.Value
             FROM ELEMENTS e
			 INNER JOIN PROPERTIES p on p.Id = e.Id and p.Key = 'Era'
             WHERE e.ID = 'F1LL3R'""".replace('F1LL3R', elem)
    # shlog.verbose(sql)
    curs.execute(sql)
    rows = curs.fetchall()
    # should return one element
    try:
        node_list = [x[0] for x in rows]
    except IndexError:
        return ''
    return node_list


def get_all_eras(args):
    # make a sql request to get element name though it's ID
    # shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    # this query returns all views that have their paths matched with args.searchterm
    sql = """SELECT EraID
             FROM ERAS"""
    # shlog.verbose(sql)
    curs.execute(sql)
    rows = curs.fetchall()
    # should return one element
    try:
        era_list = [x[0] for x in rows]
    except IndexError:
        return ''
    return era_list


def get_era_fires(args, era):
    # make a sql request to get element name though it's ID
    # shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    # this query returns all views that have their paths matched with args.searchterm
    sql = """SELECT Fires
             FROM ERAS
             WHERE EraID = '%s'""" % era
    # shlog.verbose(sql)
    curs.execute(sql)
    rows = curs.fetchall()
    # should return one element
    try:
        fires = int(rows[0][0])
    except IndexError:
        return 0
    return fires



###########################################################
#
# Main program
#
############################################################


# init logger
loglevel = shlog.VERBOSE
assert type(loglevel) == type(1)
shlog.basicConfig(level=shlog.VERBOSE)