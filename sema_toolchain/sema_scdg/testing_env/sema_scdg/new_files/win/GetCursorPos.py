
import os
import angr
import logging
from random import getrandbits

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

"""
    Store in lpPoint [out] a coordinate pair with random values.
"""
class GetCursorPos(angr.SimProcedure):
    def run(self, lpPoint):
        if lpPoint.symbolic:
            return self.state.solver.BVS("retval_{}".format(self.display_name), self.arch.bits)

        POINT_SIZE = 8
        OFFSETS = [0, 4]
        point = self.state.solver.BVS("POINT_{}".format(self.display_name), 8*POINT_SIZE)
        self.state.memory.store(lpPoint, point)

        x = getrandbits(32)
        y = getrandbits(32)
        coordinates = [x, y]
        for offset, c in zip(OFFSETS, coordinates):
            coord = self.state.memory.load(lpPoint+offset, 4)
            self.state.add_constraints(coord == c)
        return 0x1 # BOOL
