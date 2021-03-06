# coding=utf-8
import sqlite3
import shlog
import networkx as nx


def get_connections(args):
    # return a list of html files to nuke

    # this query returns all connections that have their paths matched with args.search_term
    if args.search_term is None:
        # get all unique relations if no search_term flag had been passed
        sql = """SELECT DISTINCT /* CASE handling for Node -> Artifact and Reads relations to switch them around */
				 CASE 
							WHEN e1.Type = 'Node' AND e2.Type='Artifact' THEN Target 
							WHEN r.Name = 'Read' THEN Target
							ELSE Source 
				 END as Source, 
				 CASE 
							WHEN e1.Type = 'Node' AND e2.Type='Artifact' THEN Source 
							WHEN r.Name = 'Read' THEN Source
							ELSE Target 
				 END as Target
                 FROM RELATIONS r
				 INNER JOIN ELEMENTS e1 on e1.ID = r.Source
				 INNER JOIN ELEMENTS e2 on e2.ID = r.Target
				 WHERE e1.Type <> 'Contract' AND e2.Type <> 'Contract'
				 """
    else:
        # else, put it to good use
        sql = """SELECT DISTINCT /* CASE handling for Node -> Artifact and Reads relations to switch them around */
				 CASE 
							WHEN e1.Type = 'Node' AND e2.Type='Artifact' THEN Target 
							WHEN r.Name = 'Read' THEN Target
							ELSE Source 
				 END as Source, 
				 CASE 
							WHEN e1.Type = 'Node' AND e2.Type='Artifact' THEN Source 
							WHEN r.Name = 'Read' THEN Source
							ELSE Target 
				 END as Target
                 FROM VIEWS v
                 INNER JOIN FOLDER f on f.id = v.Parent_folder_id
                 INNER JOIN CONNECTIONS c on c.view_id = v.id
                 INNER JOIN RELATIONS r on r.Id = c.relationship_id
                 INNER JOIN ELEMENTS e1 on e1.ID = r.Source
				 INNER JOIN ELEMENTS e2 on e2.ID = r.Target
                 WHERE f.Depth LIKE '%F1LL3R%' AND e1.Type <> 'Contract' AND e2.Type <> 'Contract'""".replace('F1LL3R', str(args.search_term))

    connection_list = mini_q(args, sql)
    return connection_list


def mini_q(args, sql):
    # i've learned to code better
    # so this exists
    shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    shlog.verbose(sql)
    curs.execute(sql)
    return curs.fetchall()


def get_all_relations(args):
    # return a list of html files to nuke

    sql = """SELECT Source, Target FROM RELATIONS"""

    rows = mini_q(args, sql)
    element_list = [[x[0], x[1]] for x in rows]
    return element_list


def get_elements(args):
    # return a list of html files to nuke

    if args.search_term is None:
        # get all relations if no search_term flag had been passed
        sql = """SELECT Id
                 FROM ELEMENTS"""
    else:
        sql = """SELECT DISTINCT Object_id as Id
                 FROM FOLDER f
                 INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
                 INNER JOIN VIEW_OBJECTS vo on v.Id = vo.View_id
                 WHERE f.Depth like '%{}%'""".format(str(args.search_term))


    rows = mini_q(args, sql)
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


def link_short_all(args, start, end, directional=False):
    # prepare Graph
    elements = get_elements(args)
    connections = get_connections(args)

    # get all connections as tuples
    if directional:
        g = nx.DiGraph()
    else:
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

    # this query returns the name of the supplied element ID
    sql = """SELECT Name
             FROM ELEMENTS
             WHERE ID = '{}'""".format(elem)
    #
    rows = mini_q(args, sql)
    # should return one element
    try:
        elem_name = rows[0][0]
    except IndexError:
        return ''
    return elem_name


def get_elem_type(args, elem):
    # make a sql request to get element name though it's ID
    # shlog.normal("about to open %s", args.dbfile)

    # this query returns all views that have their paths matched with args.searchterm
    sql = """SELECT Type
             FROM ELEMENTS
             WHERE ID = 'F1LL3R'""".replace('F1LL3R', elem)
    #
    rows = mini_q(args, sql)
    # should return one element
    try:
        elem_type = rows[0][0]
    except IndexError:
        return ''
    return elem_type


def get_elem_eras(args, elem):
    # make a sql request to get element name though it's ID
    # shlog.normal("about to open %s", args.dbfile)

    # this query returns all views that have their paths matched with args.searchterm
    sql = """SELECT DISTINCT p.Value
             FROM ELEMENTS e
			 INNER JOIN PROPERTIES p on p.Id = e.Id and p.Key = 'Era'
             WHERE e.ID = 'F1LL3R'""".replace('F1LL3R', elem)
    #
    rows = mini_q(args, sql)
    # should return one element
    try:
        node_list = [x[0] for x in rows]
    except IndexError:
        return ''
    return node_list


def get_all_eras(args):
    # make a sql request to get element name though it's ID
    # shlog.normal("about to open %s", args.dbfile)

    # this query returns all views that have their paths matched with args.searchterm
    sql = """SELECT EraID
             FROM ERAS"""
    #
    rows = mini_q(args, sql)
    # should return one element
    try:
        era_list = [x[0] for x in rows]
    except IndexError:
        return ''
    return era_list


def get_era_triggers(args, era):
    # make a sql request to get element name though it's ID
    # shlog.normal("about to open %s", args.dbfile)

    # this query returns all views that have their paths matched with args.searchterm
    sql = """SELECT Fires
             FROM ERAS
             WHERE EraID = '%s'""" % era
    #
    rows = mini_q(args, sql)
    # should return one element
    try:
        triggers = int(rows[0][0])
    except IndexError:
        return 0
    return triggers

def get_connection_info(args, source, target):
    # make a sql request to get info about the relation
    # make a sql request to get volume of information passed in an era
    # shlog.normal("about to open %s", args.dbfile)

    # this query returns all views that have their paths matched with args.searchterm
    sql = """SELECT Type, Name
             FROM RELATIONS
             WHERE (Source = 'F1LL3R1' AND Target = 'F1LL3R2')
             or (Source = 'F1LL3R2' AND Target = 'F1LL3R1')
             LIMIT 1""".replace('F1LL3R1', source).replace('F1LL3R2', target)
    #
    rows = mini_q(args, sql)
    # should return one element
    try:
        volume = rows[0]
    except IndexError:
        return 0
    return volume

###########################################################
#
# Main program
#
############################################################


# init logger
loglevel = shlog.VERBOSE
assert type(loglevel) == type(1)
shlog.basicConfig(level=shlog.VERBOSE)