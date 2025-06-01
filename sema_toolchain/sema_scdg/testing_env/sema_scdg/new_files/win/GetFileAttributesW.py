
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class GetFileAttributesW(angr.SimProcedure):
    def run(self, lpFileName):
        lw.info("Called GetFileAttributesW")
        return -1 # DWORD (concrete value to avoid state fork for al-khaser)
