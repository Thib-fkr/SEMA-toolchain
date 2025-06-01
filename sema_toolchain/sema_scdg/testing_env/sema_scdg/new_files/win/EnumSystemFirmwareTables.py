
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class EnumSystemFirmwareTables(angr.SimProcedure):
    def run(self, FirmwareTableProviderSignature, pFirmwareTableEnumBuffer, BufferSize):
        lw.info("Called EnumSystemFirmwareTables")
        return # UINT
