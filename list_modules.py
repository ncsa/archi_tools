import os
import shlog
import argparse

def show_comments(dir, file):
    pyFile = open(dir + file, 'r')
    for line in pyFile:
        if '# ' in line:
            shlog.normal(line.replace('\n', ''))
    pyFile.close()

if __name__ == "__main__":

    main_parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    main_parser.add_argument('--loglevel', '-l',
                             help=shlog.LOGHELP,
                             default="NORMAL")
    args = main_parser.parse_args()

    # translate text arguement to log level.
    # least to most verbose FATAL WARN INFO DEBUG
    # level also printst things to the left of it.
    loglevel = shlog.__dict__[args.loglevel]
    assert type(loglevel) == type(1)
    shlog.basicConfig(level=shlog.__dict__[args.loglevel])

    i = 0
    shlog.normal('AVAILABLE REPORTS')
    for file in os.listdir('report/'):
        if file.endswith('.py'):
            shlog.normal('#' +str(i) + ' ' + file)
            show_comments('report/', file)
            i += 1

    i = 0
    shlog.normal('AVAILABLE VALIDATIONS')
    for file in os.listdir('validate/'):
        if file.endswith('.py'):
            shlog.normal('#' + str(i) + ' ' + file)
            show_comments('validate/', file)
            i += 1