
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class StrCmpNIW(angr.SimProcedure):
    def run(self, psz1, psz2, nChar):
        if psz1.symbolic or psz2.symbolic or nChar.symbolic:
            return self.state.solver.BVS(
                "retval_{}".format(self.display_name), self.arch.bits
            )

        str1_ptr = self.state.solver.eval(psz1)
        str2_ptr = self.state.solver.eval(psz2)
        n = self.state.solver.eval(nChar)

        # Microsoft specification does not handle invalid pointer case
        wstr1 = "" if str1_ptr == 0 else self.state.mem[str1_ptr].wstring.concrete
        wstr2 = "" if str2_ptr == 0 else self.state.mem[str2_ptr].wstring.concrete

        wstr1_low = wstr1[:n].lower()
        wstr2_low = wstr2[:n].lower()
        
        if wstr1_low == wstr2_low:
            return 0 # int
        elif wstr1_low > wstr2_low:
            return 1 # int
        else:
            return -1 # int
