
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class GetComputerNameW(angr.SimProcedure):
    def run(self, lpBuffer, nSize):
        if lpBuffer.symbolic or nSize.symbolic:
            return self.state.solver.BVS(
                "retval_{}".format(self.display_name), self.arch.bits
            )

        buf_ptr = self.state.solver.eval(lpBuffer)
        if buf_ptr == 0:
            lw.warning("[-] (GetComputerNameW) Invalid pointer to buffer")
            return 0

        size_ptr = self.state.solver.eval(nSize)
        if size_ptr == 0:
            lw.warning("[-] (GetComputerNameW) Invalid pointer to size buffer")
            return 0
        size = self.state.mem[nSize].int.concrete

        # Store the name as a wide string
        user_str = ("CharlyBVO_PC"[: size - 1] + "\0").encode("utf-16-le")
        user_bvv = self.state.solver.BVV(user_str)
        self.state.memory.store(
            lpBuffer, user_bvv
        )

        # Store the length (nb of wchar) of the stored name
        len_int = len(user_str)
        len_bvv = self.state.solver.BVV(len_int, self.arch.bits)
        self.state.memory.store(
            nSize, len_bvv
        )    
        return 1 # BOOL
