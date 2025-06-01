
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class WSAStartup(angr.SimProcedure):
    def run(self, wVersionRequired, lpWSAData):
        lw.info("Called WSAStartup")
        return # int
