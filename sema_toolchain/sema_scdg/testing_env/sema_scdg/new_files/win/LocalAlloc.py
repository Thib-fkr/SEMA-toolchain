
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class LocalAlloc(angr.SimProcedure):
    def run(self, uFlags, uBytes):
        lw.info("Called LocalAlloc")
        return # HANDLE
