import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class ShowWindow(angr.SimProcedure):
    def run(self, hWnd, nCmdShow):
        lw.info("ShowWindow called")
        return 1 # BOOL
