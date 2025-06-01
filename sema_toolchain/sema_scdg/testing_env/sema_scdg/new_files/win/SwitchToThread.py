import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class SwitchToThread(angr.SimProcedure):
    def run(self, Handle):
        lw.info("SwitchToThread called")
        return 1 # BOOL
