import os


import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class CreateMutexW(angr.SimProcedure):
    def run(self, lpMutexAttributes, bInitialOwner, lpName):
        lw.info("Called CreateMutexW")
        return # HANDLE
