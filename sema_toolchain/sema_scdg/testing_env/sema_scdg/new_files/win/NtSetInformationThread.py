import os

import logging
import angr

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)


class NtSetInformationThread(angr.SimProcedure):
    def run(
        self,
        ThreadHandle,
        ThreadInformationClass,
        ThreadInformation,
        ThreadInformationLength
    ):
        return 0x0 # NTSTATUS value, we can set it to concrete 0x00000000 value representing STATUS_SUCCESS
