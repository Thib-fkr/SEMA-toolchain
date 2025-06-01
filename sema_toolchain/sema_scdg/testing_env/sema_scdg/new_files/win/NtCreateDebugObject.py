import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class NtCreateDebugObject(angr.SimProcedure):
    def run(self, DebugObjectHandle, DesiredAccess, ObjectAttributes, KillProcessOnExit):
        lw.info("Called NtCreateDebugObject")
        return # NTSTATUS
