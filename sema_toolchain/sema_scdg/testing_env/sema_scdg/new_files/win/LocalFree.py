
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class LocalFree(angr.SimProcedure):
    def run(self, hMem):
        lw.info("Called LocalFree")
        return # HLOCAL
