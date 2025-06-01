import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class NtClose(angr.SimProcedure):
    def run(self, Handle):
        lw.info("NtClose called")
        return # NTSTATUS
