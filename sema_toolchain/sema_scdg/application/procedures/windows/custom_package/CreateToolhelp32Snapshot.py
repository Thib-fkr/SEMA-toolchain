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


class CreateToolhelp32Snapshot(angr.SimProcedure):

    def run(
        self,
        dwFlags,
        th32ProcessID
    ):
        retval =  self.state.solver.BVS("retval_{}".format(self.display_name), self.arch.bits)
        self.state.solver.add(retval != 0xffffffff)
        self.state.solver.add(retval != -1)
        return retval
