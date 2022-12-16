#!/usr/bin/env python2.7
"""
Check the  .v file for an SRAM
"""

import unittest
from header import header
import sys,os
sys.path.append(os.path.join(sys.path[0],".."))
import globals
import debug
import calibre

OPTS = globals.get_opts()


class verilog_test(unittest.TestCase):

    def runTest(self):
        globals.init_openram("config_20_{0}".format(OPTS.tech_name))
        # we will manually run lvs/drc
        OPTS.check_lvsdrc = False

        import sram
        import verilog
        import filecmp

        debug.info(1, "Testing Verilog for sample 2 bit, 16 words SRAM with 1 bank")
        s = sram.sram(word_size=2,
                      num_words=OPTS.config.num_words,
                      num_banks=OPTS.config.num_banks,
                      name="sram_2_16_1_{0}".format(OPTS.tech_name))

        OPTS.check_lvsdrc = True

        curpath=os.path.dirname(os.path.realpath(__file__)) + "/"
        vfile = s.name + ".v"
        vname = curpath + vfile
        verilog.verilog(vname,s)


        # let's diff the result with a golden model
        golden = "{0}/golden/{1}".format(os.path.dirname(os.path.realpath(__file__)),vfile)
        self.assertEqual(filecmp.cmp(vname,golden),True)

        os.system("rm {0}".format(vname))

# instantiate a copdsay of the class to actually run the test
if __name__ == "__main__":
    (OPTS, args) = globals.parse_args()
    del sys.argv[1:]
    header(__file__, OPTS.tech_name)
    unittest.main()
