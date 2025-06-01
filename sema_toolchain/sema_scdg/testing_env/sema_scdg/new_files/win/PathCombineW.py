
import os
import angr
import logging
import claripy

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class PathCombineW(angr.SimProcedure):
    def run(self, pszDest, pszDir, pszFile):
        if pszDest.symbolic or pszDir.symbolic or pszFile.symbolic:
            return self.state.solver.BVS(
                "retval_{}".format(self.display_name), self.arch.bits
            )

        pszDest_ptr = self.state.solver.eval(pszDest)
        pszDir_ptr = self.state.solver.eval(pszDir)
        pszFile_ptr = self.state.solver.eval(pszFile)
        if pszDest_ptr == 0 or pszFile_ptr == 0:
            return 0 # NULL


        wstr_dir = self.state.mem[pszDir_ptr].wstring.concrete if pszDir_ptr != 0 else ""
        wstr_file = self.state.mem[pszFile_ptr].wstring.concrete

        wstr_out = wstr_dir + '\\' + wstr_file + '\0'

        self.state.memory.store(pszDest, claripy.BVV(wstr_out.encode("utf-16le")))
        return pszDest_ptr # LPWSTR
