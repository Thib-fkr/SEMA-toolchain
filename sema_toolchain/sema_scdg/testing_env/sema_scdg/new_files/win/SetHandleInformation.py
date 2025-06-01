import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class SetHandleInformation(angr.SimProcedure):
    def run(self, hObject, dwMask, dwFlags):
        lw.info("Called SetHandleInformation")
        return # BOOL
