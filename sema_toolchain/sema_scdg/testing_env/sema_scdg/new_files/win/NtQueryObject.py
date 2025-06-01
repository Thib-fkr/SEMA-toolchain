import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class NtQueryObject(angr.SimProcedure):
    def run(self, Handle, ObjectInformationClass, ObjectInformation, ObjectInformationLength, ReturnLength):
        lw.info("Called NtQueryObject")
        return # NTSTATUS
