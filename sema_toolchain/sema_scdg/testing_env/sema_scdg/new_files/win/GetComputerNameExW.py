
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class GetComputerNameExW(angr.SimProcedure):
    def run(self, NameType, lpBuffer, nSize):
        lw.info("Called GetComputerNameExW")
        return # BOOL
