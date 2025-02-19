import os
import sys


import logging
import angr

import os

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)


class GetAdaptersInfo(angr.SimProcedure):
    def run(self, arg1, arg2):
        return self.state.solver.BVS(
            "retval_{}".format(self.display_name), self.arch.bits
        )
