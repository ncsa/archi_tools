import argparse
import shlog
from xlsxwriter.workbook import Workbook
import os
import pandas as pd
from fuzzywuzzy import fuzz

class IncorrectStructure(Exception):
    pass

if __name__ == "__main__":

    main_parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter)
    main_parser.add_argument('--loglevel', '-l',
                             help='loglevel NONE, NORMAL, VERBOSE, VVERBOSE, DEBUG',
                             default="NORMAL")
    main_parser.add_argument("--tolerance", "-t",
                             help='set how similar data object names have to be (calculated by fuzz.ratio) in order '
                                  'to be listed as equals\nthe default value is 75',
                             default=75)
    main_parser.add_argument("--file", "-f",
                             help='csv input with file equivalencies',
                             default='CapacityReport 2.csv')

    args = main_parser.parse_args()
    loglevel = shlog.__dict__[args.loglevel]
    assert type(loglevel) == type(1)
    shlog.basicConfig(level=shlog.__dict__[args.loglevel])

    # remove old processed report
    try:
        os.remove(args.file[:-4] + '.xlsx')
    except OSError:
        shlog.error('Warning: ' + args.file[:-4] + '.xlsx' + ' does not exist, ignoring..')

    # fix pandas bug when writing title column names
    with open(args.file, 'r') as raw:
        data = raw.readlines()
    try:
        if data[0][0] == ',':
            data[0] = data[0][1:]
            data[1] = data[1][2:]
        if not data[0].startswith('Trigger'):
            raise IncorrectStructure
        with open(args.file, 'w') as raw:
            raw.writelines(data)
    except IndexError:
        shlog.error(args.file + ' is empty!')
        exit(0)
    except IncorrectStructure:
        shlog.error(args.file + ' does not start with a "Trigger" column and might not be compliant')

    # write all data to sheet one and give it a filter
    workbook = Workbook(args.file[:-4] + '.xlsx')
    tab1 = workbook.add_worksheet('Trigger to Node ledger')
    for r, row in enumerate(data):
        split_row = row.replace('\n','').split(',')
        for c, column in enumerate(split_row):
            tab1.write(r, c, column)
    tab1.autofilter(0, 0, len(data)-1, len(data[0].split(','))-1)

    # select all distinct data items
    p = pd.read_csv(args.file, header=0)
    unique_data = []
    temp_unique_data = p['Data Object'].unique()
    for entry in temp_unique_data:
        unique_data.append(entry.replace('\n',''))

    # make a tab with all data items in a grid fashion
    tab2 = workbook.add_worksheet('File Equivalency')
    wrap_format = workbook.add_format({'text_wrap': True})
    # write 0x axis
    i = 1
    for d, data_object in enumerate(unique_data):
        tab2.write(0, i, data_object, wrap_format)
        i += 1
    # write 0y axis
    i = 1
    for d, data_object in enumerate(unique_data):
        tab2.write(i, 0, data_object, wrap_format)
        i += 1
    tab2.freeze_panes(1, 1)

    # calculate and write fuzzy equivalence
    for r, r_data_name in enumerate(unique_data):
        for c, c_data_name in enumerate(unique_data):
            tab2.write(r+1, c+1, fuzz.ratio(r_data_name, c_data_name))

    # add conditional formatting
    match_format = workbook.add_format({'bg_color':'green', 'font_color': 'white'})
    tab2.conditional_format(1, 1, len(unique_data), len(unique_data), {'type': 'cell',
                                            'criteria': '>=',
                                            'value': int(args.tolerance),
                                            'format': match_format})

    workbook.close()