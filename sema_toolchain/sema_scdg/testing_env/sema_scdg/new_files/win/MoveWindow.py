import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class MoveWindow(angr.SimProcedure):
    def run(self, hWnd, X, Y, nWidth, nHeight, bRepaint):
        lw.info("MoveWindow called")
        return 1 # 0 If failed, non-zero if succeeded
