
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class CoUninitialize(angr.SimProcedure):
    def run(self):
        lw.info("Called CoUninitialize")
        return # void
