import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class GetWriteWatch(angr.SimProcedure):
    def run(self, dwFlags, lpBaseAddress, dwRegionSize, lpAddresses, lpdwCount, lpdwGranularity):
        lw.info("Called GetWriteWatch")
        return 1 # UINT : 0 if success. non-zero if fails. In ak it is supposed to fail
