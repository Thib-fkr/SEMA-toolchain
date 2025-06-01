import os
import sys


import logging
import angr
import archinfo
import os

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

CSR_GLOBAL_KEY = "CsrProcessId" # Should be the same in CsrGetProcessId.py

class OpenProcess(angr.SimProcedure):
    def run(self, dwDesiredAccess, bInheritHandle, dwProcessId):

        # Check whether or not the given process id is the CsrProcessId
        if not dwProcessId.symbolic and CSR_GLOBAL_KEY in self.state.globals:
            proc_id = self.state.solver.eval(dwProcessId)
            if proc_id == self.state.globals[CSR_GLOBAL_KEY]:
                return 0 # We can emulate the absence of the necessary admin process given by a debugger by being unable to open CsrProcessId

        
        retval = self.state.solver.BVS("retval{}".format(self.display_name), self.arch.bits)
        self.state.solver.add(retval != 0)
        return retval
