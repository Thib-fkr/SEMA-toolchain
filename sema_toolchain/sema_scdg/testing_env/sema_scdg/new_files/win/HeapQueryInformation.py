
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class HeapQueryInformation(angr.SimProcedure):
    def run(self, HeapHandle, HeapInformationClass, HeapInformation, HeapInformationLength, Returnlength):
        lw.info("Called HeapQueryInformation")
        return 0 # BOOL : in ak, this call should fail
