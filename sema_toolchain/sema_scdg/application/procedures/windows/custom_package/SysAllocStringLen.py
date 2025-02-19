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


class SysAllocStringLen(angr.SimProcedure):
    def run(self, strIn, ui):
        if strIn.symbolic or ui.symbolic:
            return self.state.solver.BVS(
                "retval_{}".format(self.display_name), self.arch.bits
            )

        string_addr = self.state.solver.eval(strIn)
        string = self.state.mem[string_addr].wstring.concrete
        len_str = self.state.solver.eval(ui)

        ptr = self.state.heap.malloc(len_str + 1)
        # import pdb; pdb.set_trace()

        if hasattr(string, "decode"):
            str_BVV = string.decode("utf-8")[:len_str]
            str_BVV = str_BVV + "\0"
        else:
            str_BVV = string[:len_str]
            str_BVV = str_BVV + "\0"
        self.state.memory.store(ptr, str_BVV)  # ,endness=self.arch.memory_endness)
        return ptr
