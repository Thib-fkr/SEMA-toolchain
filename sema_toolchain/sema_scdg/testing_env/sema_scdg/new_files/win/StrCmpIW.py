
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class StrCmpIW(angr.SimProcedure):
    def run(self, psz1, psz2):
        
        if psz1.symbolic or psz2.symbolic:
            # Used to mitigate sim value in loop in al-khaser (VMDriver check)
            if "services_buffer" in str(psz1):
                return 1

            return self.state.solver.BVS(
                "retval_{}".format(self.display_name), self.arch.bits
            )

        str1_ptr = self.state.solver.eval(psz1)
        str1_loaded = self.state.memory.load(psz1, self.state.arch.bits)
        str2_ptr = self.state.solver.eval(psz2)
        str2_loaded = self.state.memory.load(psz2, self.state.arch.bits)

        # Microsoft specification does not handle invalid pointer case
        wstr1 = "" if str1_ptr == 0 or str1_loaded.symbolic else self.state.mem[str1_ptr].wstring.concrete
        wstr2 = "" if str2_ptr == 0 or str2_loaded.symbolic else self.state.mem[str2_ptr].wstring.concrete

        wstr1 = wstr1.lower()
        wstr2 = wstr2.lower()

        if wstr1 == wstr2:
            return 0 # int
        elif wstr1 > wstr2:
            return 1 # int
        else:
            return -1 # int
