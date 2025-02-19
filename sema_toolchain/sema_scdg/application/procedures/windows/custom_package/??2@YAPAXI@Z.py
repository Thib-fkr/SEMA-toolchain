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

# ??2@YAPAXI@Z
class NewInt(angr.SimProcedure):
    ALT_NAMES = "??2@YAPAXI@Z"
    def run(
        self,
        uint,
    ):
        if uint.symbolic:
            lw.warning("Symbolic size passed to new")
            return self.state.heap._malloc(0x42)
        malloced = self.state.heap._malloc(uint)
        for i in range(self.state.solver.eval(uint)):
            self.state.memory.store(malloced+i, 0,size=1)
        print(malloced)
        return malloced
