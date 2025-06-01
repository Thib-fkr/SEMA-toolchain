import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class GetConsoleScreenBufferInfo(angr.SimProcedure):
    def run(self, hConsoleOutput, lpConsoleScreenBufferInfo):
        lw.info("GetConsoleScreenBufferInfo called")
        return 1 # Zero if failed, non-zero if succeeded
