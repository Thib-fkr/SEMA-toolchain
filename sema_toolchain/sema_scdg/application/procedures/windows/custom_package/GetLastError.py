import os
import sys


import logging
import angr

import os

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)


class GetLastError(angr.SimProcedure):
    def run(self):
        # x = self.state.globals["GetLastError"]
        # self.state.globals["GetLastError"] = self.state.solver.BVS("last_error", self.arch.bits)
        # return x
        # #ret_expr = self.state.plugin_env_var.last_error
        # # self.state.memory.load(self.state.regs.esp,4,endness= self.arch.memory_endness)
        # #return ret_expr
        # return self.state.solver.BVS(
        #         "retval_{}".format(self.display_name), self.arch.bits
        #     )
        return 0x0
