
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class StrStrIW(angr.SimProcedure):
    def run(self, pszFirst, pszSrch):

        if pszFirst.symbolic or pszSrch.symbolic:
            return self.state.solver.BVS(
                "retval_{}".format(self.display_name), self.arch.bits
            )

        # Retrieve the pointers
        haystack_ptr = self.state.solver.eval(pszFirst)
        needle_ptr = self.state.solver.eval(pszSrch)

        # Retrieve the bytes in memory
        if haystack_ptr == 0:
            return 0 # NULL

        haystack_val = self.state.memory.load(pszFirst, self.arch.bits)
        if hasattr(haystack_val, "symbolic") and "regkey_query" in str(haystack_val):
            # Used to avoid forks when checking registry keys in al-khaser (IsRegKeyValueExists in al-khaser)
            return 0 # NULL

        haystack_wstr = self.state.mem[haystack_ptr].wstring.concrete

        if needle_ptr == 0:
            return 0 # NULL
        needle_wstr = self.state.mem[needle_ptr].wstring.concrete

        # Lower both the arguments as the comparison is not case sensitive
        haystack = haystack_wstr.lower()
        needle = needle_wstr.lower()

        index = haystack.find(needle)
        if index == -1:
            return 0 # NULL
       
        return haystack_ptr + index
