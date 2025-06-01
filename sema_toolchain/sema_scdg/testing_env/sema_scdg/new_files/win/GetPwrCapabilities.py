
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class GetPwrCapabilities(angr.SimProcedure):
    def run(self, lpspc):
        context_size = 76
        offsets = [3, 4, 5, 6, 13]

        context = self.state.solver.BVS("CONTEXT_{}".format(self.display_name), 8*context_size)
        self.state.memory.store(lpspc, context)

        for offset in offsets:
            regval = self.state.memory.load(lpspc + offset, 1)
            self.state.add_constraints(regval == 1)
        return 0x1
