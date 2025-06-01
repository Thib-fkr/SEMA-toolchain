import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class Sleep(angr.SimProcedure):
    def run(self, dwMilliseconds):
        lw.info("Sleep called")
        return
