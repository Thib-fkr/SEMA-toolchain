
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class wcsrchr(angr.SimProcedure):
    def run(self, string, c):
        if string.symbolic or c.symbolic:
            return self.state.solver.BVS(
                "retval_{}".format(self.display_name), self.arch.bits
            )

        string_ptr = self.state.solver.eval(string)
        char_b = self.state.solver.eval(c)

        if string_ptr == 0:
            return 0 # TODO: Or whatever the NULL value is with angr

        char = chr(char_b)

        string_wstr: str = self.state.mem[string_ptr].wstring.concrete

        if char not in string_wstr:
            return 0 # TODO: Same

        index = string_ptr + string_wstr.rfind(char)*4
        
        return index # wchar_t
