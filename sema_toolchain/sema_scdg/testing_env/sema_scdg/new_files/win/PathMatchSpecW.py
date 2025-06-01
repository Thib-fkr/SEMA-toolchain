
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class PathMatchSpecW(angr.SimProcedure):
    def run(self, pszFile, pszSpec):
        lw.info("Called PathMatchSpecW, default to true for reg key checking (To implement if encountered in another scenario)")
        return 1 # BOOL
