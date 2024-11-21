import os
import sys


import angr
import logging

import os

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class RaiseException(angr.SimProcedure):
    # Defining a function called "NO_RET" that does not return anything.
    NO_RET = True
    def run(self, hKey, lpValueName, lpReserved, lpType, lpData, lpcbData):
        # Implement the logic for querying the value of a registry key using the provided parameters.
        lw.warning("RaiseException called")
        return
