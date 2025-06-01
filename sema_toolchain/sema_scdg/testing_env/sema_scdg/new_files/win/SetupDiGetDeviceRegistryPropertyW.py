
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class SetupDiGetDeviceRegistryPropertyW(angr.SimProcedure):
    def run(self, DeviceInfoSet, DeviceInfoData, Property, PropertyRegDataType, PropertyBuffer, PropertyBufferSize, RequiredSize):
        lw.info("Called SetupDiGetDeviceRegistryPropertyW")
        return 1 # BOOL
