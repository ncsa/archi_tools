#!/usr/bin/env python3
"""
This module implments a subset of logging I use for interactive commands.

by default,  not suppressed are NORMAL, WARN and ERROR, meaning:
    NONE: Produce no output
    WARNING is for messages where someting not normal has occurred, but the program continues
    ERROR is for something that is "contract violating" and the program likely needs to termainate


all meassages, including the trio NORMAL, WARNING and ERROR are suppressed by setting 
the logging level to "NONE" It is not suported that the trio of NORMAL, WARNING and 
ERROR  are  suppressed individually.

Conceptually orthognal to  the triple of NORMAL, WARN and ERROR is verbosity. 
This modules provides for  three levels of verbosity. the Verbosity levels
help a user understand the program. DEBUG may produce an overwhelming amount
of output, perahpsmroe useful for a bug report. 
    VERBOSE
    VVERBOSE 
    DEBUG.

Progess dots:

Certain application benefit from progress dots.  These are dots (or other symbols) printed to standard 
error wihtoug newlines that denote progress in a long computataion. shlog.dot() and shlog.newline 
are not implemented using the underlying python logging mechansim  They are implemented using writes to stdout. 

"""
from __future__ import print_function
import logging
#import exception

class NotConfigured(Exception):
    pass
    

#
# redefine log level text and sugar functions apropos for shell commands, not servers.
# The underlying scheme is that higher the number the more silent the cose will be.
#
CONFIGURED=False
# the normal default for a use program shoudl be normal.
NONE=55                  # Progams go not log at NONE user command lines use this to silence the logging facility
ERROR=logging.FATAL      # Programs indicate contract violation; uses slines  normal and error messaging to jsut see error 
WARNING=logging.WARNING  # Programs indicate this to indicte the program handles a condition of interest to a users. 
NORMAL=logging.WARNING-1 # Programs isse comfort messages indicating progress and status "              "
VERBOSE=logging.INFO    # Programs issue status messages indicicating an additional level of status and progress " 
DEBUG=logging.DEBUG      # Programs issed very detailes messages, typically about interfaces of details of internaks" 


LEVELDICT = {"NONE": NONE,
             "ERROR" : ERROR,
             "WARNING": WARNING,
             "NORMAL": NORMAL,  
             "VERBOSE": VERBOSE,
             "DEBUG": DEBUG}
for (levelname, levelno) in LEVELDICT.items():
    logging.addLevelName(levelno, levelname)

# re-using the standard logging funtions gives all the sugar features of the
# logging modues  so create the "shlog.normal" function to be an alias of
# logging.normal, etc.
normal = logging.fatal
warning = logging.warning
normal = logging.info
debug = logging.debug

def error(msg, *args, **kwargs):
    if not CONFIGURED : raise NotConfigured("shlog call before basicConfig call")    
    logging.log(LEVELDICT["ERROR"], msg, *args, **kwargs)
    
def warning(msg, *args, **kwargs):
    if not CONFIGURED : raise NotConfigured("shlog call before basicConfig call")    
    logging.log(LEVELDICT["WARNING"], msg, *args, **kwargs)
    
def normal(msg, *args, **kwargs):
    if not CONFIGURED : raise NotConfigured("shlog call before basicConfig call")    
    logging.log(LEVELDICT["NORMAL"], msg, *args, **kwargs)
    
def verbose(msg, *args, **kwargs):
    if not CONFIGURED : raise NotConfigured("shlog call before basicConfig call")    
    logging.log(LEVELDICT["VERBOSE"], msg, *args, **kwargs)
    
def debug(msg, *args, **kwargs):
    if not CONFIGURED : raise NotConfigured("shlog call before basicConfig call")    
    logging.log(LEVELDICT["DEBUG"], msg, *args, **kwargs)

LOGHELP = "Logging Level: NONE, ERROR, WARNING, VERBOSE, DEBUG"
"""
def dot(symbol="."):
    #log progress dots, by default dots are a period (.)
    import sys
    loglevel = logging.root.getEffectiveLevel()
    if loglevel > DOTS : return 
    print(symbol, end="", file=sys.stderr)
    
def newline():
    #just a newline, useful if last dot is known and dots are printed
    import sys
    loglevel = logging.root.getEffectiveLevel()
    if loglevel > DOTS : return 
    print("",file=sys.stderr)
"""
def basicConfig(**kwargs):
    # Call underlying loggger
    global CONFIGURED
    logging.basicConfig(**kwargs)
    CONFIGURED=True
    return

helptext = "NONE, ERROR, WARNING, NORMAL, VERBOSE, DEBUG"

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

    #generate an outout for each message
    error("ERROR Message")
    warning("WARNING message")
    normal("NORMAL message")
    verbose("VERBOSE message")
    debug("DEBUG message")
 
