import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class VerifyVersionInfoW(angr.SimProcedure):
    def run(self, lpVersionInformation, dwTypeMask, dwlConditionMask):
        lw.info("VerifyVersionInfoW called")
        return 1 # BOOL
