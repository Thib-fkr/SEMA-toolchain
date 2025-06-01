
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class _wcsicmp(angr.SimProcedure):
    def run(self, string1, string2):
        if string1.symbolic or string2.symbolic:
            return self.state.solver.BVS(
                "retval_{}".format(self.display_name), self.arch.bits
            )

        str1_ptr = self.state.solver.eval(string1)
        str2_ptr = self.state.solver.eval(string2)
        if str1_ptr == 0 or str2_ptr == 0:
            return 2147483647 # Return _NLSCMPERROR (INT_MAX)

        wstr1 = self.state.mem[str1_ptr].wstring.concrete
        wstr2 = self.state.mem[str2_ptr].wstring.concrete

        wstr1_low = wstr1.lower()
        wstr2_low = wstr2.lower()

        if wstr1_low == wstr2_low:
            return 0 # int
        elif wstr1_low > wstr2_low:
            return 1 # int
        else:
            return -1 # int
       
