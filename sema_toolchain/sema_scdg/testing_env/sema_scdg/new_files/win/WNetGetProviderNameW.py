
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class WNetGetProviderNameW(angr.SimProcedure):
    def run(self, dwNetType, lpProviderName, lpBufferSize):
        if lpProviderName.symbolic:
            return self.state.solver.BVS(
                "retval_{}".format(self.display_name), self.arch.bits
            )

        buf = self.state.solver.BVS("lpProviderName_{}".format(self.display_name), self.arch.bits)
        self.state.memory.store(lpProviderName, buf)
        
        return 0 # DWORD : NO_ERROR
