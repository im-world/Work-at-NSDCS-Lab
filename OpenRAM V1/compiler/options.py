import optparse             # library used to take options as command
                            # line inputs (e.g. -r, -a); a good example:  
                            # https://docs.python.org/3/library/optparse.html

import getpass              # username and password library

class options(optparse.Values): # It seems like the optparse.Values argument 
                                # contains the values provided by the user,
                                # which it replaces in these variables somehow,
                                # maybe by using the 'dest' option while 
                                # defining the 'optparse' object
                                
                                # no explicit mention of the 'optparse' input
                                # argument is made in the class
    """
    Class for holding all of the OpenRAM options.
    """
    # This is the technology directory.
    openram_tech = ""
    # This is the name of the technology.
    tech_name = ""
    # This is the temp directory where all intermediate results are stored.
    openram_temp = "/tmp/openram_{0}_temp/".format(getpass.getuser())
    # This is the verbosity level to control debug information. 0 is none, 1
    # is minimal, etc.
    debug_level = 0
    # This determines whether  LVS and DRC is checked for each submodule.
    check_lvsdrc = True
    # Variable to select the variant of spice (hspice or ngspice right now)
    spice_version = "hspice"
    # Should we print out the banner at startup
    print_banner = True
    # The Calibre executable being used which is derived from the user PATH.
    calibre_exe = ""
    # The spice executable being used which is derived from the user PATH.
    spice_exe = ""
    # Run with extracted parasitics
    run_pex = False
    # Trim noncritical memory cells for simulation speed-up
    trim_noncritical = False
    # Define the output file paths
    out_path = ""
    # Define the output file base name
    out_name = ""
