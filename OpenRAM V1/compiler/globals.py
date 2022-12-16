"""
This is called globals.py, but it actually parses all the arguments and performs
the global OpenRAM setup as well.
"""
import os
import debug
import shutil                     
import optparse
import options                    # contains variables with openRAM options
                                  # all others are built-in libraries
import sys
import re                         # regular expression matching library
import importlib                 

# Current version of OpenRAM.
VERSION = "1.0"

# Output banner for file output and program execution.
BANNER = """\
##############################################################
#                                                            #                                           
#                OpenRAM Compiler v""" + VERSION + """                       #
#                                                            #                                           
#                VLSI Design Automation Lab                  #
#                UCSC CE Department                          #
#                                                            #
#                VLSI Computer Architecture Research Group   #
#                Oklahoma State University ECE Department    #
#                                                            #
##############################################################\n"""

USAGE = "usage: openram.py [options] <config file>\n"

# Anonymous object that will be the options
OPTS = options.options()            # variable enlisting options in 'options.py'
# going to options from here

def is_exe(fpath):                  # Is path accessible, with execution permission?
    return os.path.exists(fpath) and os.access(fpath, os.X_OK)

# parse the optional arguments
# this only does the optional arguments

# What the two comments above are for? Seem like an artifact


def parse_args():
    """Parse the arguments and initialize openram"""
    
    # parses user input, modifies option variables' values in OPTS,
    # and returns options and arguments provided by the user
    
    
    global OPTS

    # array of options; 'dest' variable names the same as those in options, as
    # expected :)
    
    option_list = {
        optparse.make_option("-b", "--backannotated", dest="run_pex",
                             help="back annotated simulation for characterizer"),
        optparse.make_option("-o", "--output", dest="out_name",
                             help="Base output file name.", metavar="FILE"),
        optparse.make_option("-p", "--outpath", dest="out_path",
                             help="output file location."),
        optparse.make_option("-n", "--nocheck", action="store_false",
                             help="Disable inline LVS/DRC checks", dest="check_lvsdrc"),
        optparse.make_option("-q", "--quiet", action="store_false", dest="print_banner",
                             help="Don\'t display banner"),
        optparse.make_option("-v", "--verbose", action="count", dest="debug_level",
                             help="Increase the verbosity level"),
        optparse.make_option("-t", "--tech", dest="tech_name",
                             help="Technology name"),
        optparse.make_option("-s", "--spiceversion", dest="spice_version",
                             help="Spice simulator name"),
        # TODO: Why is this -f?
        optparse.make_option("-f", "--trim_noncritical", dest="trim_noncritical",
                             help="Trim noncritical memory cells during simulation")
    }
# -h --help is implicit.

    #defining a parser object with option list above
    parser = optparse.OptionParser(option_list=option_list,
                                   description="Compile and/or characterize an SRAM.",
                                   usage=USAGE,
                                   version="sramc v" + VERSION)
    
    # scans the terminal input, stores the results as follows
    # options - an object containing values for all of your options
    # e.g., options.out_name will give the out_name input by user
    # args - the list of positional arguments leftover after parsing options
    (options, args) = parser.parse_args(values=OPTS)
    
    # here, we are passing a values object OPTS, which stores 'option arguments'
    # the variables in OPTS will be modified according to the values provided by
    # the user
    # the variable 'options' will be the same as OPTS after execution

    return (options, args)


def get_opts():                      # get options 
    return(OPTS)


def init_openram(config_file):
    """Initialize the technology, paths, simulators, etc."""

    debug.info(1,"Initializing OpenRAM...")

    setup_paths()           # Set up paths for gdsMill, tests, 
                            # characterizer, temporary files, and output

    read_config(config_file) # reads config_file and imports it into OPTS.config
    
    import_tech()   # set the technology path in OPTS, and import the setup scripts

    set_spice()     # set Spice executable path in OPTS.spice_exe, and set
                    # input dir for spice files if ngspice is used

    set_calibre()   # set Calibre executable path in OPTS.calibre_exe, else
                    # skip LVS/DRC

def read_config(config_file):
    global OPTS
    
    OPTS.config_file = config_file
    OPTS.config_file = re.sub(r'\.py$', "", OPTS.config_file)
    # remove all '*.py' from/in the config_file

    # dynamically import the configuration file of which modules to use
    debug.info(1, "Configuration file is " + OPTS.config_file + ".py")
    try:
        OPTS.config = importlib.import_module(OPTS.config_file)
        # import_module used as module name is a variable
    except:
        debug.error("Unable to read configuration file: {0}".format(OPTS.config_file+".py. Did you specify the technology?"),2)


def set_calibre():
    debug.info(2,"Finding calibre...")
    global OPTS

    # check if calibre is installed, if so, we should be running LVS/DRC on
    # everything.
    if not OPTS.check_lvsdrc:
        # over-ride the check LVS/DRC option
        debug.info(0,"Over-riding LVS/DRC. Not performing inline LVS/DRC.")
    else:
        # see if calibre is in the path (extend to other tools later)
        for path in os.environ["PATH"].split(os.pathsep):
            OPTS.calibre_exe = os.path.join(path, "calibre")
            # if it is found, do inline LVS/DRC
            if is_exe(OPTS.calibre_exe):
                OPTS.check_lvsdrc = True
                debug.info(1, "Using calibre: " + OPTS.calibre_exe)
                break
        else:
            # otherwise, give warning and procede
            debug.warning("Calibre not found. Not performing inline LVS/DRC.")
            OPTS.check_lvsdrc = False


def setup_paths():
    """ Set up the non-tech related paths. """
    
    # paths for gdsMill, tests, characterizer, temporary files, and output
    
    debug.info(2,"Setting up paths...")

    global OPTS

    OPENRAM_HOME = os.path.abspath(os.environ.get("OPENRAM_HOME"))
    sys.path.append("{0}".format(OPENRAM_HOME))
    sys.path.append("{0}/gdsMill".format(OPENRAM_HOME)) 
    sys.path.append("{0}/tests".format(OPENRAM_HOME))
    sys.path.append("{0}/characterizer".format(OPENRAM_HOME))


    if not OPTS.openram_temp.endswith('/'):
        OPTS.openram_temp += "/"
    debug.info(1, "Temporary files saved in " + OPTS.openram_temp)

    # we should clean up this temp directory after execution...
    # emptying temp directory
    if os.path.exists(OPTS.openram_temp):
        shutil.rmtree(OPTS.openram_temp, ignore_errors=True) # recursive delete

    # make the directory if it doesn't exist
    try:
        os.makedirs(OPTS.openram_temp, 0750)
    except OSError as e:
        if e.errno == 17:  # errno.EEXIST
            os.chmod(OPTS.openram_temp, 0750)

    # Don't delete the output dir, it may have other files!
    # make the directory if it doesn't exist
    try:
        os.makedirs(OPTS.out_path, 0750)
    except OSError as e:
        if e.errno == 17:  # errno.EEXIST
            os.chmod(OPTS.out_path, 0750)
    
    # path string manipulations
    if OPTS.out_path=="":
        OPTS.out_path="."
    if not OPTS.out_path.endswith('/'):
        OPTS.out_path += "/"
    debug.info(1, "Output saved in " + OPTS.out_path)


def set_spice():
    debug.info(2,"Finding spice...")
    global OPTS

    # set the input dir for spice files as the temp directory 
    # if using ngspice (not needed for hspice)
    if OPTS.spice_version == "ngspice":
        os.environ["NGSPICE_INPUT_DIR"] = "{0}".format(OPTS.openram_temp)

    # search for calibre in the path
    for path in os.environ["PATH"].split(os.pathsep):
        OPTS.spice_exe = os.path.join(path, OPTS.spice_version)
        # if it is found, then break and use first version
        if is_exe(OPTS.spice_exe):
            debug.info(1, "Using spice: " + OPTS.spice_exe)
            break
    else:
        # otherwise, give warning and procede
        debug.warning("Spice not found. Unable to perform characterization.")


# imports correct technology directories for testing
def import_tech():
    global OPTS

    debug.info(2,"Importing technology: " + OPTS.tech_name)

    if OPTS.tech_name == "":
        OPTS.tech_name = OPTS.config.tech_name

        # environment variable should point to the technology dir
    OPTS.openram_tech = os.path.abspath(os.environ.get("OPENRAM_TECH")) + "/" + OPTS.tech_name
    # setting technology directory path to the 'openram_tech' option,
    # which was not filled by the user
    
    if not OPTS.openram_tech.endswith('/'):
        OPTS.openram_tech += "/"
    debug.info(1, "Technology path is " + OPTS.openram_tech)

    try:
        filename = "setup_openram_{0}".format(OPTS.tech_name)
        # we assume that the setup scripts (and tech dirs) are located at the
        # same level as the compielr itself, probably not a good idea though.
        path = "{0}/setup_scripts".format(os.environ.get("OPENRAM_TECH"))
        sys.path.append(os.path.abspath(path))
        __import__(filename)
    except ImportError:
        debug.error("Nonexistent technology_setup_file: {0}.py".format(filename))
        sys.exit(1)

