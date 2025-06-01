
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class CoInitializeEx(angr.SimProcedure):
    def run(self, pvReserved, dwCoInit):
        lw.info("Called CoInitializeEx")
        return # HRESULT
