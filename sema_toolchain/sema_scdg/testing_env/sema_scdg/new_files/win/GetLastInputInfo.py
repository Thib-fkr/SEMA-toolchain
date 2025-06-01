
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class GetLastInputInfo(angr.SimProcedure):
    def run(self, plii):
        lw.info("Called GetLastInputInfo")
        return 0 # BOOL
