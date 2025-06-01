import os
import sys

import logging
import angr

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)


class GetEnvironmentVariableW(angr.SimProcedure):
    def run(self, lpName, lpBuffer, nSize):
        return 0
