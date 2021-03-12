import argparse
import shlog
from connector import get_elements, get_all_relations, get_elem_name, get_elem_type, mini_q
import networkx as nx
from networkx.drawing.nx_agraph import write_dot
from networkx_query import search_nodes
from collections import OrderedDict
import pandas as pd
import os


def get_tech_nodes(G):
    tech_traits = ["Technology", "SystemSoftware", "Node", "Device"]
    findings = []
    for trait in tech_traits:
        search = list(search_nodes(G, {"contains": ["type", trait]}))
        for s in search:
            findings.append(s)
    return findings


def get_global_business(args):
    sql = """SELECT distinct r.Target
FROM FOLDER f
INNER JOIN VIEWS v on f.id = v.Parent_folder_id
INNER JOIN CONNECTIONS c on c.view_id = v.id
INNER JOIN RELATIONS r on c.relationship_id = r. id
inner join ELEMENTS e on e.id = r.Target 
WHERE f.Depth like '%3. Global Business Service Realziation View%'"""
    return [x[0] for x in mini_q(args, sql)]



if __name__ == "__main__":

    main_parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter)
    main_parser.add_argument("--dbfile", "-d",
                                 help='full name of the *.db file to use as data source',
                                 default="NCSA Services_db.db")
    main_parser.add_argument("--search_term", "-s", help="specify a search term to search in the folder hierarchy to "
                                                         "ingest connections only form a desired set of view",
                             default=None)
    args = main_parser.parse_args()

    nodes = get_elements(args)
    edges = get_all_relations(args)

    # build graph
    # get all connections as tuples
    g = nx.DiGraph()
    for node in nodes:
        g.add_node(node, label=get_elem_name(args, node), type=get_elem_type(args, node))
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)

    # get global business
    business_nodes = get_global_business(args)
    # get tech
    tech_nodes = get_tech_nodes(g)


    # loop de loop through business nodes X tech nodes
    # without storing anything in memory. just write straight to csv
    head_toggle = True
    try:
        os.remove("ASD Report.csv")
    except OSError:
        pass
    for business_node in business_nodes:
        for tech_node in tech_nodes:
            try:
                # prep a dict to write
                d = OrderedDict()
                d["Service"] = get_elem_name(args, business_node)
                d["Technology"] = get_elem_name(args, tech_node)
                d["Reason"] = ' --> '.join(get_elem_name(args, x) for x in nx.shortest_path(g, tech_node, business_node))

                # turn into pd and write it
                df = pd.DataFrame.from_records([d])
                with open('ASD Report.csv', 'a') as f:
                    df.to_csv(f, header=head_toggle, index=False)
                head_toggle = False  # stop writing headers after the first one had been written

                # dependencies[business_node][tech_node] = nx.shortest_path(g, tech_node, business_node)
                shlog.normal('linked {} and {}'.format(d["Service"], d["Technology"]))
            except nx.exception.NetworkXNoPath:
                shlog.normal('no path between {} and {}!'.format(d["Service"], d["Technology"]))




    # dump graph
    # write_dot(g, "grid.dot")