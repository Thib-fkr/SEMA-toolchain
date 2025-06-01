import angr
import logging
import os

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class RegQueryValueExW(angr.SimProcedure):
    def run(
        self,
        hKey,
        lpValueName,
        lpReserved,
        lpType,
        lpData,
        lpcbData
    ):
        if lpValueName.symbolic:
            return self.state.solver.BVS(
                "retval_{}".format(self.display_name), self.arch.bits
            )

        value_ptr = self.state.solver.eval(lpValueName)
        value_wstr = "" if value_ptr == 0 else self.state.mem[value_ptr].wstring.concrete

        if value_wstr in ("Count",):
            return 0x0

        ptr = self.state.solver.BVS(
            "regkey_query_{}_{}".format(self.display_name, lpData), self.arch.bits
        )
        self.state.memory.store(lpData, ptr)
        return 0x0
