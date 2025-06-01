
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class ReadProcessMemory(angr.SimProcedure):
    def run(self, hProcess, lpBaseAddress, lpBuffer, nSize, lpNumberOfBytesRead):
        lw.info("Called ReadProcessMemory")
        return # BOOL
