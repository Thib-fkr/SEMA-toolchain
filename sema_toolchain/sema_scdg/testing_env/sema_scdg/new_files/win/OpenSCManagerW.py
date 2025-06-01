
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class OpenSCManagerW(angr.SimProcedure):
    def run(self, lpMachineName, lpDatabaseName, dwDesiredAccess):
        lw.info("Called OpenSCManagerW")
        return # SC_HANDLE
