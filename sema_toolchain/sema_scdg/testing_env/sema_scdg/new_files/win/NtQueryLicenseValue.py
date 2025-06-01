
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class NtQueryLicenseValue(angr.SimProcedure):
    def run(self, ValueName, Type, Data, DataSize, ResultDataSize):
        lw.info("Called NtQueryLicenseValue")
        return # NTSTATUS
