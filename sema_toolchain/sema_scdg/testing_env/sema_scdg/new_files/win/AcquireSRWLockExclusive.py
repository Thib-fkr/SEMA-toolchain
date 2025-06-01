import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class AcquireSRWLockExclusive(angr.SimProcedure):
    def run(self, SRWLock):
        lw.info("AcquireSRWLockExclusive called")
        return 1 # Zero if failed, non-zero if succeeded
