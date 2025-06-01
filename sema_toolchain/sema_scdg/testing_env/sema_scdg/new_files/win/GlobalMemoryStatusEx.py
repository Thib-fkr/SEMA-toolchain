
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class GlobalMemoryStatusEx(angr.SimProcedure):
    def run(self, lpBuffer):
        lw.info("Called GlobalMemoryStatusEx")
        return # BOOL
