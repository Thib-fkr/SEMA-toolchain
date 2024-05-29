import logging
import angr

import os

lw = logging.getLogger("CustomSimProcedureWindows")
lw.setLevel(os.environ["LOG_LEVEL"])
from .TlsSetValue import TlsSetValue


class TlsFree(angr.SimProcedure):
    KEY = "win32_tls"
    SETTER = TlsSetValue

    def run(self, index):
        set_val = self.inline_call(
            self.SETTER, index, self.state.solver.BVV(0, self.state.arch.bits)
        )
        return set_val.ret_expr
