import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class QueryInformationJobObject(angr.SimProcedure):
    def run(self, hJob, JobObjectInformationClass, lpJobObjectInformation, cbJobObjectInformationLength, lpReturnLength):
        lw.info("Called QueryInformationJobObject")
        return # BOOL
