
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class SLIsGenuineLocal(angr.SimProcedure):
    def run(self, pAppId, pGenuineState, pUIOptions):

        if pGenuineState.symbolic:
            return self.state.solver.BVS(
                "retval_{}".format(self.display_name), self.arch.bits
            )
            
        ENUM_SIZE = 4
        genuine_state = self.state.solver.BVS("GenuineState_{}".format(self.display_name), 8*ENUM_SIZE)
        self.state.memory.store(pGenuineState, genuine_state)

        regval = self.state.memory.load(pGenuineState, ENUM_SIZE)
        self.state.add_constraints(regval == 0)
        
        return 0x0 # HRESULT
