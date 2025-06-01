
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class GetBinaryTypeW(angr.SimProcedure):
    def run(self, lpApplicationName, lpBinaryType):
        lw.info("Called GetBinaryTypeW")
        return 0 # BOOL, in ak this call should fail

