
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class SetupDiEnumDeviceInfo(angr.SimProcedure):
    def run(self, DeviceInfoSet, MemberIndex, DeviceInfoData):
        lw.info("Called SetupDiEnumDeviceInfo")

        if MemberIndex.symbolic:
            return self.state.solver.BVS(
                "retval_{}".format(self.display_name), self.arch.bits
            )

        # For Al-khaser (setupdi-diskdrive), likely to appear in a loop [0..], execute it only once
        i = self.state.solver.eval(MemberIndex)
        if i == 0:
            return 1 # BOOL
        else:
            return 0 # BOOL

