from graphviz import Digraph
from graphviz import backend
import argparse
import shlog
import os
import pandas as pd


if __name__ == "__main__":
    main_parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    main_parser.add_argument('--loglevel', '-l',
                             help=shlog.LOGHELP,
                             default="NORMAL")

    # options: target db file and name of drawing
    main_parser.add_argument("--dbfile", "-d", required=True)
    main_parser.add_argument("--view","-v",required=True)

    args = main_parser.parse_args()
    loglevel = shlog.__dict__[args.loglevel]
    assert type(loglevel) == type(1)
    shlog.basicConfig(level=shlog.__dict__[args.loglevel])

# generate two temp python files:
# one with graphviz_nodes
nodes_report = '''from reports import *
def graphviz_nodes(args):
    # Get a list of nodes for graphviz
    Nodes  = StanzaFactory(args,
                             """SELECT e.ID, e.Name
                                FROM VIEWS v
                                INNER JOIN VIEW_OBJECTS vo on vo.View_id = v.Id
                                INNER JOIN ELEMENTS e on e.ID = vo.Object_id
                                WHERE v.Name = '%s'"""
    )
    Nodes.add_report_segment(
        SegmentSQL("SELECT '{ID}' as ID, '{Name}' as Name")
    )
    return Nodes #3''' % args.view
with open('graphviz_nodes.py', 'w') as f:
    f.write(nodes_report)

# one with graphviz_edges
edges_report = '''from reports import *
def graphviz_edges(args):
    # Get a list of edges for graphviz
    Edges  = StanzaFactory(args,
                             """SELECT r.Source, r.Target, COALESCE(NULLIF(r.Name,''), r.Type) as Name
                                FROM main.VIEWS v
                                INNER JOIN CONNECTIONS c on c.view_id = v.Id
                                INNER JOIN RELATIONS r on r.ID = c.relationship_id
                                WHERE v.Name = '%s'"""
    )
    Edges.add_report_segment(
        SegmentSQL("SELECT '{Source}' as Source, '{Target}' as Target, '{Name}' as Name")
    )
    return Edges #3''' % args.view
with open('graphviz_edges.py', 'w') as f:
    f.write(edges_report)


# run a report on the specified drawing
# report 1: all elements
targetPy = 'python reports.py -d ' + args.dbfile + ' -l VERBOSE report '
nodesPy = targetPy + 'graphviz_nodes'
shlog.verbose('Issuing term command: ' + nodesPy)
os.system(nodesPy)
shlog.verbose(nodesPy + ' executed')

# report 2: all connections
edgesPy = targetPy + 'graphviz_edges'
shlog.verbose('Issuing term command: ' + edgesPy)
os.system(edgesPy)
shlog.verbose(edgesPy + ' executed')



# load excel output into a pandas frame
nodes = pd.read_excel('graphviz_nodes.xlsx', sheet_name='Sheet1', index_col=0)
edges = pd.read_excel('graphviz_edges.xlsx', sheet_name='Sheet1', index_col=0)

# load it into a graphviz object
g = Digraph('G', filename=args.view + '.dot')
for index, row in nodes.iterrows():
    g.node(row["ID"], label=row["Name"])
for index, row in edges.iterrows():
    g.edge(row["Source"], row["Target"], label=row["Name"])
pass

# clean up the *.py and *.xlsx files
os.remove('graphviz_nodes.py')
os.remove('graphviz_edges.py')
os.remove('graphviz_nodes.pyc')
os.remove('graphviz_edges.pyc')
os.remove('graphviz_nodes.xlsx')
os.remove('graphviz_edges.xlsx')

# save the object into a file
g.render(filename=args.view + '.dot')



