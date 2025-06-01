import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class K32GetModuleInformation(angr.SimProcedure):
    def run(self, hprocess, hmodule, lpmodinfo, cb):
        lw.info("K32GetModuleInformation called")
        return # BOOL
