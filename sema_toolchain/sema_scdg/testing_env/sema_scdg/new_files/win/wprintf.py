import os


import logging
import angr

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)


class wprintf(angr.SimProcedure):
    def run(self, fmt, *args):
        lw.debug("[+] Called wprintf")
        if fmt.symbolic:
            return self.state.solver.BVS("retval_{}".format(self.display_name), 32)

        lw.warning(f"wprintf lookalike prints: [{self.state.mem[self.state.solver.eval(fmt)].wstring.concrete}]")
        return 1
        

