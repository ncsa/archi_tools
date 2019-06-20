import argparse
import shlog
import sqlite3
import connector as c
import networkx
import os
import pandas as pd
from collections import OrderedDict


def get_service(args):
    # return a list of html files to nuke
    shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    # this query returns all views that have their paths matched with args.searchterm
    if args.search_term is None:
        sql = """SELECT DISTINCT e.ID
                 FROM VIEW_OBJECTS vo
                 INNER JOIN ELEMENTS e on e.ID = vo.Object_id
                 WHERE e.Type = 'ApplicationService'"""
    else:
        sql = """SELECT DISTINCT e.ID
                 FROM VIEWS v
                 INNER JOIN FOLDER f on f.Id = v.Parent_folder_id
                 INNER JOIN VIEW_OBJECTS vo on vo.View_id = v.id
                 INNER JOIN ELEMENTS e on e.ID = vo.Object_id
                 WHERE e.Type = 'ApplicationService' AND f.Depth LIKE '%F1LL3R%'""".replace('F1LL3R', str(args.search_term))
    shlog.verbose(sql)
    curs.execute(sql)
    rows = curs.fetchall()
    trigger_list = [x[0] for x in rows]
    return trigger_list


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

    source_services = get_service(args)
    target_services = get_service(args)

    source_to_target_links = []
    for target in source_services:
        for source in target_services:
            try:
                if target != source:
                    source_to_target_links.append(c.link_short_all(args, source, target, True))
                    pass
            except networkx.exception.NetworkXNoPath:
                shlog.verbose(source + ' cannot reach ' + target)


    # start logging
    con_log = {}
    head_toggle = True
    try:
        os.remove("ServiceReport.csv")
    except OSError:
        print('Warning: ServiceReport.csv does not exist, ignoring..')

    for source_to_target in source_to_target_links:
        for pathway in source_to_target:

            # stop handling this pathway if we have already sestablished a link between the source and target services
            if pathway[-1] in list(con_log.keys()) and pathway[0] in list(con_log[pathway[-1]].keys()):
                break

            # create an entry for the target element if not yet logged:
            if pathway[-1] not in list(con_log.keys()):
                con_log[pathway[-1]] = {}
            # create a dict entry for the target node
            if pathway[0] not in list(con_log[pathway[-1]].keys()):
                con_log[pathway[-1]][pathway[0]] = {}

            # log full path
            f_path = ''
            f_prev = None
            for f_elem in pathway:
                if f_prev is not None:
                    # if there's something in prev, continue mapping
                    connection = c.get_connection_info(args, f_prev, f_elem)
                    f_path += ' >--' + connection[1] + ' (' + connection[0] + ')--> ' + c.get_elem_name(args, f_elem)
                else:
                    # if nothing is prev, that means we're looking at the first element
                    f_path = c.get_elem_name(args, f_elem)
                f_prev = f_elem

            # write names and the pathway to a csv file
            d = OrderedDict()
            d["Service"] = [c.get_elem_name(args, pathway[-1])]
            d["Supported By"] = [c.get_elem_name(args, pathway[0])]
            d["Full Path"] = [f_path]
            df = pd.DataFrame(data=d, columns=list(d.keys()), index=None)
            with open('ServiceReport.csv', 'a') as f:
                df.to_csv(f, header=head_toggle, index=head_toggle)
            # stop writing headers after the first one had been written
            head_toggle = False

    with open('ServiceReport.csv', 'r') as raw:
        data = raw.readlines()
    if data[0][0] == ',':
        data[0] = data[0][1:]
        data[1] = data[1][2:]
        with open('ServiceReport.csv', 'w') as raw:
            raw.writelines(data)