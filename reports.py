#!/usr/bin/env python
from __future__ import print_function
import shlog
import argparse
import sqlite3
import db
import sys
from datetime import datetime

#  do not worry yet about rows that are composite.


def q(args, sql):
    con = sqlite3.connect(args.dbfile)
    cur = con.cursor()
    shlog.verbose(sql)
    result  = cur.execute (sql)
    con.commit()
    return result


def qtranspose(args, sql):
    shlog.verbose(sql)
    results = []
    rets = q(args,sql).fetchall()
    if not rets:
        return [[],[]]
    for result in rets :
        results.append(result)
    return zip(*results)


def qd(args, sql, passed_stanza):
    # return results of query as a list of dictionaries,
    # one for each row.
    con = sqlite3.connect(args.dbfile)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    shlog.verbose(sql)
    results = cur.execute (sql)
    shlog.debug(results)
    # header collection handling
    # 0th call to qd() is from contexts
    # the one that follows it directly is the one we can snatch column names from
    if passed_stanza.left_column_collections == 1:
        try:
            passed_stanza.left_columns_collector = list(map(lambda x: x[0], cur.description))
            shlog.verbose("Logged left columns to the second stanza (%s) passed: %s" % (passed_stanza,passed_stanza.left_columns_collector))
            passed_stanza.left_column_collections += 1
        except:
            pass
    return results


class Workspace:
    """ Provde an in-memory workslae that can be rendered into excel, etc..."""
    def __init__(self, args):
        # one-based index beacause you know, excel...:
        self.row = 0
        self.col = 0
        self.col_max = 0
        self.args = args
        self.content={}
        self.args=args
        # header value that will be passed by stanza for integration into excel object
        self.header = []

    def next_row(self):
        self.row = self.row+1
        self.content[self.row] = {}
        self.col = 1

    def max_chars(self, colno):
        # return the max characters in any cell within a column, 0 for empty column
        max_chars = 0
        for rowno in range(self.row):
            if rowno in self.content.keys() and colno in self.content[rowno].keys():
                # use python string as a proxy for numeric columns.
                max_chars = max(max_chars,len("%s" % self.content[rowno][colno]))
            # special header handling
            # if rowno is 0, that means we are looking at the first passed header row
            # due to the way content vs header are implemented, self.header is offset by 1 unlike colno
            # for example, B2 value (colno 1 rowno 0) is located in self.header[0]. hence, colno-1 is implemented
            if rowno == 0 and colno > 0:
                try:
                    max_chars = max(max_chars, len("%s" % self.header[colno-1]))
                except:
                    # if an exception is thrown, it's most likely the IndexError: list index out of range
                    # meaning there's multiple (sub)stanzas with eneven number of contexts. ignore and move on
                    pass
        shlog.debug("XXX %s %s" %  (colno, max_chars*2)) 
        return max_chars

    def add_element(self, content_element):
        # add populate the curent celle on the current row.
        self.content[self.row][self.col] = content_element
        shlog.verbose("content: (%s,%s):%s" % (self.row, self.col, self.content[self.row][self.col]))
        self.col_max = max(self.col_max, self.col)
        self.col += 1

    def catenate_workspace(self, workspace_to_catenate):
        for n in range(1, workspace_to_catenate.row):
            self.row += 1
            shlog.verbose("catenting row %s" % self.row)
            columns_from_other = workspace_to_catenate.content[n]
            self.content[self.row] = columns_from_other
            self.col_max = max(self.col_max,workspace_to_catenate.col_max)

    def dump(self):
        # provide a crude dump of the workspace
        for r in range(1,self.row):print (self.content[r])

    def excel(self):
        # write the output to an excel file.  @ optionally pop up execl to see ot
        import xlsxwriter
        import os
        workbook = xlsxwriter.Workbook(self.args.excelfile)
        worksheet = workbook.add_worksheet()
        # have to say bold to work to make wrap to work, hmm
        x = workbook.add_format({"text_wrap" : True,  "bold" : True })
        # write header
        for h in range(0, len(self.header)):
            worksheet.write(0, h+1, self.header[h], x)
        # write collected content
        for r in range(1,self.row+1):
            shlog.debug("content:%s", self.content)
            shlog.debug("writing excel row: %s" % r)
            keys = self.content[r].keys()
            for c in keys:
                worksheet.write(r, c, self.content[r][c], x)

        for c in range(self.col_max+1):
                maxc = min(self.max_chars(c), 60)
                maxc = max(maxc, 1) # at least one char
                worksheet.set_column(c,c, maxc)
        # but, there's one more thing...
        worksheet.freeze_panes(1, 0)
        workbook.close()
        if self.args.show : os.system('open -a "Microsoft Excel" %s' % self.args.excelfile)
             

class Header:
    def __init__(self, args, header_list):
        self.args = args
        self.header_list = header_list
    def report (self, _dummy):
        pass


class Padr:
    def __init__(self, args, ncells):
        self.args = args
        self.ncells = ncells
    def report (self, _dummy):
        pass


class QueryContext:
    # a query contest is an array of dictionary that provides
    # additional information to a query.  The keys in the dictionary
    # are teh names in the select statement
    # e.g Deleac a, b...dog from,,,,   a and dog would be keys
    # a distinct dictionary is made for every line returned.
    # the primary internal data structure is a list of these
    # dictionaries.
    #
    # All of this supports a stanza repeating itself on a row,
    # Each time using a line from the SQL query to generate new
    # outputs.
    #
    # Capitalization Names capitalised as known to the database.

    def __init__(self, args, sql):
        self.context_list = []
        if sql== None:  # shim to support no context... Fix afer getting the chain to work.
            self.context_list= [{}]
            return
        con = sqlite3.connect(args.dbfile)
        cur = con.cursor()
        shlog.verbose(sql)
        self.results = [r for r in  cur.execute (sql)]
        self.names = [d[0] for d in cur.description]
        shlog.debug("context list generated with names %s" % self.names)
        for row in self.results: 
            d = {}
            for (key, item) in zip(self.names, row):
                 d[key] = item
            self.context_list.append(d)
        shlog.verbose("new query context: %s", self.context_list)


class SegmentSQL:
        def __init__(self, segment_sql, one_to_one=True, context=QueryContext(None,None)):
            self.segment_sql = segment_sql
            self.one_to_one = one_to_one
            self.context = context  # an object


class StanzaFactory:
   # recipe for 0...n terminal rows
    def __init__(self, args, element_sql):
        self.args = args
        # The element  query yields information on identifying
        # things on rows. e.g list the elementsid asscociated
        # with a folder id.
        # e.g. SELECT node_id from ELEMENT_FOLDER where  folder_id = '%s"
        self.element_sql = element_sql
        # the report sql tells what to print on a report line
        # for an element, e.g. report on an element.
        # e.g. SELECT * from element where id = `%s`
        self.report_segments = []
        # the substanza object is called to make sub stanza after each report line.
        # e.g self.substanza.report(element_id)
        self.workspace = Workspace(self.args)
        self.substanza = None
        # context header names will be collected into context_collector
        self.context_collector = []
        # non-dynamic column names will be harvested from the second operation in qd
        self.left_columns_collector = []
        self.left_column_collections = 0

    def add_report_segment(self, segment_sql):
        self.report_segments.append(segment_sql)

    def set_substanza(self, substanza):
        self.substanza = substanza
        
    def report(self, element_sql_params):
        # Outer loop -- this query givee query paremater to ideniify the subject of a row
        # pass arguments, sql and the stanza itself so the header can be passed on
        for row_query_sql_params in qd(self.args, self.element_sql.format(**element_sql_params), self) :
            self.workspace.next_row()
            for segment in self.report_segments:
                unformatted_row_query_sql = segment.segment_sql
                contexts = segment.context.context_list
                for context in contexts:
                    #import pdb; pdb.set_trace()
                    merged_dict = {}
                    merged_dict.update(row_query_sql_params)
                    merged_dict.update(context)
                    # header collection: collect the context to be used as a header
                    if context.values() not in self.context_collector:
                        shlog.verbose("Collecting dynamic (right) header value: %s" % context.values())
                        self.context_collector.append(context.values())
                    shlog.debug("formating: %s:%s" %(unformatted_row_query_sql, merged_dict.keys()))
                    row_query_sql = unformatted_row_query_sql.format(**merged_dict)
                    shlog.debug(row_query_sql)
                    row_query_sql = row_query_sql.format(**context)
                    if segment.one_to_one:
                        self.generate_one_to_one_segment(row_query_sql)
                    else:
                        self.generate_one_to_many_segment(row_query_sql)
                    # done bulding this row, now build any substanza
            if self.substanza:
                self.substanza.workspace = self.workspace
                self.substanza.report(row_query_sql_params)
        return self.workspace
    
    def generate_one_to_one_segment(self,segment_sql):
        # left_column_collections adds one one every pass. qd() will snatch the columns from sql on the second calling
        # from generate_one_to_one_segment
        self.left_column_collections += 1
        # perform query and then populate successive cells in the
        # workspace row with the result
        # pass arguments, sql command and the stanza itself so we can retrieve static column names
        segment_result = qd(self.args, segment_sql, self).fetchone()
        if segment_result:
            for s in segment_result:
                self.workspace.add_element(s)
        else:
            # For this row nothing satifies the query
            # Pad out for each parameter which would have
            # had a return
            for d in db.qdescription(self.args, segment_sql):
                self.workspace.add_element("")
            
    def generate_one_to_many_segment(self,segment_sql):
        # perform query and then catenate the list of results
        # insert into rightmost cell of the workspace
        answer = []
        segment_result = q(self.args, segment_sql).fetchall()
        for result in segment_result:
            # make a string from each returned row.
            s = ' '.join(result)  
            answer.append(s)
        # separate the data from each row wiht a delimiter
        # put data in the next column of the row.
        delimiter = ':::'
        delimiter = '\n'
        self.workspace.add_element(delimiter.join(answer))
        

if __name__ == "__main__":

    main_parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    main_parser.add_argument('--loglevel','-l',
                             help=shlog.LOGHELP,
                             default="NORMAL")
    
    main_parser.add_argument("--dbfile", "-d", default="LSST_archi_tool.db")
    main_parser.set_defaults(func=None) # if none then there are  subfunctions
    subparsers = main_parser.add_subparsers(title="subcommands",
                       description='valid subcommands',
                       help='additional help')
    

    # Subcommand to make a report
    report_parser = subparsers.add_parser('report')
    report_parser.add_argument("--show" , "-s", help="show result in excel", default=False, action='store_true')
    report_parser.add_argument("--closeexcel", "-ce", action='store_true',
                             help="kill all instances of Excel upon execution")
    report_parser.add_argument("--function" , "-f", help="def: modulename",default=None)
    report_parser.add_argument("--excelfile" , "-e", help="def: modulename.xslx",default=None)
    report_parser.add_argument("module" , help="obtain report definition from this module")
    report_parser.add_argument("--timestamp", "-t", help="Add timestamp to output file name", default=False,
                               action='store_true')

  
    args = main_parser.parse_args()


    # translate text arguement to log level.
    # least to most verbose FATAL WARN INFO DEBUG
    # level also printst things to the left of it. 
    loglevel=shlog.__dict__[args.loglevel]
    assert type(loglevel) == type(1)
    shlog.basicConfig(level=shlog.__dict__[args.loglevel])
    shlog.normal("Database is %s" % args.dbfile)
    if ".py" in args.module:
        shlog.error("Module names do not contain the .py suffix")
        exit(1)
    if not args.function: args.function = args.module
    if not args.excelfile or '.xlsx' not in args.excelfile: args.excelfile = args.module + ".xlsx"
    if args.timestamp: args.excelfile = args.excelfile[:-5] + datetime.now().strftime("_%m.%d.%Y_%H:%M") + '.xlsx'

    # add report/validate folders to PATH
    sys.path.insert(0, './validate/')
    sys.path.insert(0, './report/')
    # remove the actual path from args
    args.module = args.module.replace('validate/','').replace('report/','')
    args.function = args.function.replace('validate/','').replace('report/','')
    print(args.module)
    module = __import__(args.module)
    if args.function not in module.__dict__.keys():
        shlog.error("%s is not a function within module %s" % (args.function, args.module))
        exit(2)
    rpt = module.__dict__[args.function](args) #1
    shlog.verbose('Executing passed report: %s' % rpt.args.function)
    rpt.report({})
    # print(rpt.args.function)
    import os #4
    if args.closeexcel:
        shlog.normal("Terminating Excel")
        os.system("""osascript -e 'tell application "Microsoft Excel"' -e 'close (every window whose name contains "%s") saving no' -e 'end tell'""" % rpt.args.function)
    # compile header row names into rpt.context_collector
    try:
        rpt.context_collector.remove([])
    except:
        rpt.context_collector = []
    for i in rpt.context_collector:
        rpt.left_columns_collector.append(i[0])
    rpt.workspace.header = rpt.left_columns_collector
    rpt.workspace.excel()
    exit(0)

