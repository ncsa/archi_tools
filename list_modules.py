import os
import glob
import re
import argparse
import shlog

def show_comments(file):
    pyFile = open(file, 'r')
    for line in pyFile:
        if '# ' in line:
            print(line.replace('\n', ''))
    pyFile.close()

if __name__ == "__main__":

    main_parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    main_parser.add_argument('--loglevel', '-l',
                             help='loglevel NONE, NORMAL, VERBOSE, VVERBOSE, DEBUG',
                             default="ERROR")
    main_parser.add_argument('--ezrun', '-ez', default=None,
                             help='execute reports.py with -l VERBOSE report -s -ce REPORT_NAME flags.\nUse: r0 to run 0th report, v3 to run 3rd validation, etc.')
    args = main_parser.parse_args()

    # init the logger
    loglevel = shlog.__dict__[args.loglevel]
    assert type(loglevel) == type(1)
    shlog.basicConfig(level=shlog.__dict__[args.loglevel])

    # ez execute mode
    if args.ezrun != None:
        if re.match(r'(r|v)([0-9]+)', args.ezrun):
            if args.ezrun.startswith('r'):
                fileList = glob.glob('report/*.py')
            else:
                fileList = glob.glob('validate/*.py')
            try:
                targetPy = fileList[int(args.ezrun[1:])]
                targetPy = targetPy.replace('.py','')
                targetPy = 'python reports.py -l VERBOSE report -s -t -ce ' + targetPy
                shlog.verbose('Issuing term command: ' + targetPy)
                os.system(targetPy)
                shlog.verbose(targetPy + ' executed')
            except IndexError:
                print('Invalid module #')
        else:
            print("--ezrun " + args.ezrun + " parameter is not valid. It should start with a lowercase 'r' or 'v' and a corresponding module #")
        exit(0)

    # normal mode: list all modules
    i = 0
    print('#_______________#\nAVAILABLE REPORTS')
    for file in glob.glob('report/*.py'):
        print('#' +str(i) + ' ' + file)
        show_comments(file)
        i += 1

    i = 0
    print('#_______________#\nAVAILABLE VALIDATIONS')
    for file in glob.glob('validate/*.py'):
        print('#' + str(i) + ' ' + file)
        show_comments(file)
        i += 1
    print('\nUse the -ez parameter to quickly run a report\n')