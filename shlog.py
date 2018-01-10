#!/usr/bin/env python3
"""
This module implments a subset of logging I use for interactive commands.

by default,  not suppressed are NORMAL, WARN and ERROR, meaning:
    NORMAL is comport messages for the user.
    WARNING is for messages where someting not normal has occurred, but the program continues
    ERROR is for something that is "contract violating" and the program likely needs to termainate

all meassages, including the trio NORMAL, WARNING and ERROR are suppressed by setting 
the logging level to "NONE" It is not suported that the trio of NORMAL, WARNING and 
ERROR  are  suppressed individually.

Concetually orthognal to  the triple of NORMAL, WARN and ERROR is verbosity. 
This modules provides for  three levels of verbosity.
    VERBOSE
    VVERBOSE 
    DEBUG.

By default no verbosity related message  are printed to stderr.

Configuratons other than default can be obtained by...
Setting LOGLEVEL to NONE. This suppresses all log messages.
Setting the level to VERBOSE. This enables VERBOSE to be output in addition to messages when NORMAL is configured. 
Setting the level to VVERBOSE, This  enables VVERBOSE messages in addition to messages when  VERBOSE is configured.
Setting the level to DEBUG. This  enables DEBUG messages to be genrated in addition to mesabges when VVERBOSE is generated.

Progess dots:

Certain application benefit from progress dots.  These are dots (or other symbols) printed to standard 
error wihtoug newlines that denote progress in a long computataion. shlog.dot() and shlog.newline 
are not implemented using the underlying python logging mechansim  They are implemented using writes to stdout. 

Logging of DOTS is currently not suppressible. 


"""
import logging
#
# redefine log level text and sugar functions apropos for shell commands, not servers. 
NONE=55
NORMAL=logging.FATAL+1
DOTS=logging.FATAL
VERBOSE=logging.WARNING
VVERBOSE=logging.INFO
DEBUG=logging.DEBUG

LEVELDICT = {"NONE": 55,
             "ERROR" : logging.FATAL,
             "WARN": logging.FATAL,
             "NORMAL": logging.FATAL,
             "DOTS" : logging.FATAL-1,
             "VERBOSE": logging.WARNING , "VVERBOSE": logging.INFO,
             "DEBUG": logging.DEBUG}
for (levelname, levelno) in LEVELDICT.items():
    logging.addLevelName(levelno, levelname)

# re-using the standard logging gives all the sugar features of the logging modues
normal = logging.fatal
verbose = logging.warning
vverbose = logging.info
debug = logging.debug

def warn(msg, *args, **kwargs):
    logging.log(LEVELDICT["WARN"], msg, *args, **kwargs)
def error(msg, *args, **kwargs):
    logging.log(LEVELDICT["ERROR"], msg, *args, **kwargs)

ROOTLOGGER=None
def dot(symbol="."):
    #log progress dots, by default doat are a period (.)
    import sys
    print symbol,
    
def newline():
    #just a newline, useful if last dot is known
    import sys
    print

def basicConfig(**kwargs):
    global ROOTLOGGER
    ROOTLOGGER = logging.basicConfig(**kwargs)
    return ROOTLOGGER

helptext = "NONE, NORMAL, NODOTS, VERBOSE, VVERBOSE, DEBUG"

if __name__ == "__main__":

    import argparse
    
    #main_parser = argparse.ArgumentParser(add_help=False)
    main_parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=argparse.RawDescriptionHelpFormatter)
    main_parser.add_argument('loglevel',
                             help=helptext,
                             default="NORMAL")
     
    args = main_parser.parse_args()

    basicConfig(level=LEVELDICT[args.loglevel])

    #generate an outout for each maessage
    normal("normal message")
    warn("WARN")
    error("ERROR")
    for r in range (1,20): dot()
    newline()
    verbose("verbose message")
    vverbose("verboser message")
    debug("debug message")
 
