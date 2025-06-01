
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class GetSystemFirmwareTable(angr.SimProcedure):
    def run(self, FirmwareTableProviderSignature, FirmwareTableID, pFirmwareTableBuffer, BufferSize):
        # Returning a 0 value to stop Al-khaser from stalling in the SMBIOS checks
        # In order to concretely implement this SimProcedure:
        #    - return concrete value equal to buffer size
        #    - put a BVS or BVV in pFirmwareTableBuffer with the same size
        #    - use a value that is not comparable to a known VM string
        return 0 # UINT
