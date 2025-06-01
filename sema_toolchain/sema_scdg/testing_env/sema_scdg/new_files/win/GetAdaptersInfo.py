
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class GetAdaptersInfo(angr.SimProcedure):
    def run(self, AdapterInfo, SizePointer):
        lw.info("Called GetAdaptersInfo")
        return 0 # ULONG
