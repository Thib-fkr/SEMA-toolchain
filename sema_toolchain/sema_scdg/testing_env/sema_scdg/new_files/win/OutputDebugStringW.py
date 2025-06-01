import os
import sys


import angr
import logging

import os

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class OutputDebugStringW(angr.SimProcedure):
    def run(self, lpOutputString):
        return 0

