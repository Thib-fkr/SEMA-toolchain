import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

STATUS_DEBUGGER_INACTIVE = 0xC0000354
STATUS_NOT_IMPLEMENTED = 0xC0000002
STATUS_SUCCESS = 0x0

class NtSystemDebugControl(angr.SimProcedure):
    def run(self, Command, InputBuffer, InputBufferLength, OutputBuffer,OutputBufferLength, ReturnLength):
        if Command.symbolic:
            return self.state.solver.BVS(
                "retval_{}".format(self.display_name), self.arch.bits
            )

        command = self.state.solver.eval(Command)
        if command == 0x14:
            return STATUS_DEBUGGER_INACTIVE # Concrete value to emulate the absence of debugger, could also be STATUS_NOT_IMPLEMENTED

        return STATUS_SUCCESS # NTSTATUS
