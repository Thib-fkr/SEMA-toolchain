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


class InternetOpenUrlA(angr.SimProcedure):
    def run(self, hInternet, lpszUrl, lpszHeaders, dwHeadersLength, dwFlags, dwContext):
        print(self.state.mem[lpszUrl].string.concrete)
        handle = self.state.solver.BVS("retval_{}".format(self.display_name), self.arch.bits)
        self.state.solver.add(handle != 0)
        return handle
