import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class IsProcessorFeaturePresent(angr.SimProcedure):
    def run(self, feat):
        lw.info("IsProcessorFeaturePresent called")
        return self.state.solver.BVV(0x1, self.state.arch.bits) # Zero if failed, non-zero if succeeded
