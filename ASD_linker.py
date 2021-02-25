import argparse
import shlog
from connector import get_elements, get_all_relations, get_elem_name
import networkx as nx
from networkx.drawing.nx_agraph import write_dot



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
        g.add_node(node, label=get_elem_name(args, node))
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)

    # dump graph
    write_dot(g, "grid.dot")


    print("ok!")