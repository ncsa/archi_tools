import argparse
import sqlite3
import shlog
import os
import glob
from bs4 import BeautifulSoup as bs

def delete_list(args):
    # return a list of html files to nuke
    shlog.normal("about to open %s", args.dbfile)
    con = sqlite3.connect(args.dbfile)
    curs = con.cursor()
    # this query returns all views that have their paths matched with args.searchterm
    sql = """SELECT v.Id
             FROM FOLDER f
             INNER JOIN VIEWS v on v.Parent_folder_id = f.Id
             WHERE f.Depth like '%PL4C3H0LD%'""".replace('PL4C3H0LD', args.searchterm)
    shlog.verbose(sql)
    curs.execute(sql)
    rows = curs.fetchall()
    view_list = [x[0] for x in rows]
    return view_list

def index_cleaner(args):
    # delete matching folder class from html
    shlog.verbose('Parsing ' + args.apache + 'index.html')
    soup = bs(open(args.apache + 'index.html'), "html.parser")

    spans = soup.findAll('span')
    shlog.verbose('Found ' + str(spans.__len__()) + ' spans')

    for match in spans:
        if args.searchterm in match.text:
            shlog.normal('Deleting ' + str(match))
            match.decompose()

    shlog.normal('Writing censored html to ' + args.apache + 'index.html')
    with open(args.apache + 'index.html', "w") as file:
        file.write(str(soup))
    return

###########################################################
#
# Main program
#
############################################################


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
    main_parser.add_argument("--apache", "-a",
                             help='apache server html folder',
                             default="/var/www/html/")
    main_parser.add_argument("--modelID", "-m",
                             help='ID of the model to purge. Use --modlist ot get a list of models',
                             default="80fb683b-9e14-426e-b074-e3169fffb08f")
    main_parser.add_argument("--searchterm", "-s",
                             help='term to search for in the folder hierarchy for deletion',
                             default="Draft Viewpoints")
    main_parser.add_argument("--modlist", "-ml", action='store_true',
                             help='list model IDs in the Apache server folder')
    main_parser.set_defaults(func=None)  # if none then there are  subfunctions

    args = main_parser.parse_args()

    loglevel = shlog.__dict__[args.loglevel]
    assert type(loglevel) == type(1)
    shlog.basicConfig(level=shlog.__dict__[args.loglevel])
    shlog.normal("Database is %s" % args.dbfile)

    if args.modlist:
        # model lister mode
        shlog.verbose('Listing model IDs located at ' + args.apache)
        shlog.normal(glob.glob(args.apache + '*-*-*-*'))
    else:
        # purger mode
        views = delete_list(args)
        shlog.normal('Got view ID list with ' + str(views.__len__()) + ' objects')
        for v in views:
            shlog.verbose('Searching for files matching ' + v)
            del_candidate = args.apache + args.modelID + '/views/' + v + '.html'
            try:
                shlog.verbose('Attempting to remove ' + del_candidate)
                os.remove(del_candidate)
            except Exception as ex:
                template = "Exception {0} thrown on deletion: {1!r}"
                shlog.verbose(template.format(type(ex).__name__, ex.args))
        # remove mentions from html
        index_cleaner(args)





