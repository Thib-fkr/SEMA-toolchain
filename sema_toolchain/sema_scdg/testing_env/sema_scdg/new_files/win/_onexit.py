import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class _onexit(angr.SimProcedure):
    def run(self, fptr):
        lw.info("_onexit called")
        return # Function pointer or Null
