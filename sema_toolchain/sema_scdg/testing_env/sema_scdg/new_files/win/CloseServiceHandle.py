
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class CloseServiceHandle(angr.SimProcedure):
    def run(self, hSCObject):
        lw.info("Called CloseServiceHandle")
        return # BOOL
