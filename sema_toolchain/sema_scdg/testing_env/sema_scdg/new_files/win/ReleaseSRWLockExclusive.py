import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class ReleaseSRWLockExclusive(angr.SimProcedure):
    def run(self, SRWLock):
        lw.info("ReleaseSRWLockExclusive called")
        return
