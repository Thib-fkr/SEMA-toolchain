import os


import logging
import angr

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)


class strlen(angr.SimProcedure):
    def run(self, s):
        lw.debug("[+] Called strlen")
        if s.symbolic:
            return self.state.solver.BVS("retval_{}".format(self.display_name), 32)
        
        try:
            string = self.state.mem[s].string.concrete
            return len(string)
        except:
            lw.debug("s not resolvable")
            for i in range(0x100):
                if self.state.solver.eval(self.state.memory.load(s+i,1)) == 0x0:
                    return i
            lw.debug("can't find length")
            return self.state.solver.BVS("retval_{}".format(self.display_name), 32)

