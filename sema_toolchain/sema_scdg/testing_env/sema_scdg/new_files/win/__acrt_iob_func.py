
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class __acrt_iob_func(angr.SimProcedure):
    def run(self):
        return self.state.solver.BVV(0, self.state.arch.bits)
