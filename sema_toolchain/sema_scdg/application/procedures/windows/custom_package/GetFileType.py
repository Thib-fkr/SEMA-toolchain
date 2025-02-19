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


class GetFileType(angr.SimProcedure):
    def run(self, hFile):
        if self.state.solver.eval(hFile) == 1000 or self.state.solver.eval(hFile) == 1001 or self.state.solver.eval(hFile) == 1002:
            return 0x3
        retval = self.state.solver.BVS("retval_{}".format(self.display_name),  self.arch.bits)
        self.state.solver.add(retval > 0)
        return retval
