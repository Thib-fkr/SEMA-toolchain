
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class SetupDiGetClassDevsW(angr.SimProcedure):
    def run(self, ClassGuid, Enumerator, hwndParent, Flags):
        lw.info("Called SetupDiGetClassDevsW")

        valid_handle = self.state.solver.BVS(
            "retval_{}".format(self.display_name), self.arch.bits
        )
        self.state.solver.add(valid_handle != -1) # INVALID_HANDLE_VALUE = -1

        return valid_handle # HANDLE

