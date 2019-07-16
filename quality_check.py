import argparse
import sqlite3
import shlog
import numpy as np


def get_all_relations(args):
    # return a relations as they appear in view found by the search_term
    shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    try:
        sql = """SELECT DISTINCT e1.Type as Source, r.Type as Relationship, e2.Type as Target
                 FROM FOLDER f
                 INNER JOIN VIEWS v on v.Parent_folder_id = f.ID
                 INNER JOIN CONNECTIONS c on c.view_id = v.Id
                 INNER JOIN RELATIONS r on r.ID = c.relationship_id
                 INNER JOIN ELEMENTS e1 on e1.Id = r.Source
                 INNER JOIN ELEMENTS e2 on e2.Id = r.Target
                 WHERE f.Depth LIKE '%F1LL3R%'""".replace('F1LL3R', args.search_term)
    except TypeError:
        shlog.error('TypeError thrown! Check if --search_term had been provided.')
        exit(0)
    shlog.verbose(sql)
    curs.execute(sql)
    rows = curs.fetchall()
    relation_list = [list(elem) for elem in rows]
    return relation_list


def get_legal_relations(args):
    # return a relations as set by the perfect view
    shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    try:
        sql = """SELECT DISTINCT e1.Type as Source, r.Type as Relationship, e2.Type as Target
                 FROM FOLDER f
                 INNER JOIN VIEWS v on v.Parent_folder_id = f.ID
                 INNER JOIN CONNECTIONS c on c.view_id = v.Id
                 INNER JOIN RELATIONS r on r.ID = c.relationship_id
                 INNER JOIN ELEMENTS e1 on e1.Id = r.Source
                 INNER JOIN ELEMENTS e2 on e2.Id = r.Target
                 WHERE f.name = 'Viewpoint Definitions' and v.Name = 'F1LL3R'""".replace('F1LL3R', args.perfect_view)
    except TypeError:
        shlog.error('TypeError thrown! Check if --perfect_view had been provided.')
        exit(0)
    shlog.verbose(sql)
    curs.execute(sql)
    rows = curs.fetchall()
    relation_list = [list(elem) for elem in rows]
    return relation_list


if __name__ == "__main__":

    main_parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter)
    main_parser.add_argument('--loglevel', '-l',
                             help='loglevel NONE, NORMAL, VERBOSE, VVERBOSE, DEBUG',
                             default="ERROR")
    main_parser.add_argument("--dbfile", "-d",
                             help='full name of the *.db file to use as data source',
                             default="LSST_archi_tool.db")
    main_parser.add_argument("--perfect_view", "-p", help="specify the name of the view to be used as an example of a "
                                                          "perfect view of its type",
                             default=None)
    main_parser.add_argument("--search_term", "-s", help="specify a search term to search in the folder hierarchy to "
                                                         "find views and check their compliance with the perfect view",
                             default=None)
    args = main_parser.parse_args()

    # shlog config
    loglevel = shlog.__dict__[args.loglevel]
    assert type(loglevel) == type(1)
    shlog.basicConfig(level=shlog.__dict__[args.loglevel])

    # get all legal relations and elements
    legal_relations = get_legal_relations(args)
    all_relations = get_all_relations(args)

    # get relations and elements found in the views found through the search_term

    # use standard python functionality to compare the two lists

    # issue a query to find where these violations had occured
    for triple in all_relations:
        if triple not in legal_relations:
            print(triple)