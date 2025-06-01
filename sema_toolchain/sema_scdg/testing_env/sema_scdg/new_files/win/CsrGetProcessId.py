import os
import random
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

CSR_GLOBAL_KEY = "CsrProcessId" # Should be the same in OpenProcess.py

class CsrGetProcessId(angr.SimProcedure):
    def run(self):
        """
            CsrGetProcId is used with OpenProcess as an anti-debug technique.
            The goal here is for the OpenProcess SimProcedure to have a way to
            check whether if it receives the id produced by this function or not.
        """
        if CSR_GLOBAL_KEY not in self.state.globals:
            csr_proc_id = random.getrandbits(0x20)
            self.state.globals[CSR_GLOBAL_KEY] = csr_proc_id
            lw.info(f"CsrGetProcessId obtains random ID: {csr_proc_id}")
        return csr_proc_id
