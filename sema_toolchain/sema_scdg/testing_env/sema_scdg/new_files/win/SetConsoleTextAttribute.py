import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class SetConsoleTextAttribute(angr.SimProcedure):
    def run(self, hConsoleOutput, wAttributes):
        lw.info("SetConsoleTextAttribute called")
        return 1 # 0 If failed, non-zero if succeeded
