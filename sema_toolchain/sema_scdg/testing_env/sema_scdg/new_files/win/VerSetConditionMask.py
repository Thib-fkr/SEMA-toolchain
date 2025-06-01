import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class VerSetConditionMask(angr.SimProcedure):
    def run(self, ConditionMask, TypeMask, Condition):
        lw.info("VerSetConditionMask called")
        return # ULONGLONG
