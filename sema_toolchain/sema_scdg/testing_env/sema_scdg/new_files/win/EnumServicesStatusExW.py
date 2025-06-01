
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class EnumServicesStatusExW(angr.SimProcedure):
    def run(self,
            hSCManager,
            InfoLevel,
            dwServiceType,
            dwServiceState,
            lpServices,
            cbBufSize,
            pcbBytesNeeded,
            lpServicesReturned,
            lpResumeHandle,
            pszGroupName):

        # Temporary al-khaser fix for check `VMDriverServices`
        ptr = self.state.solver.BVS(
            "services_buffer_{}_{}".format(self.display_name, lpServices), self.arch.bits
        )
        self.state.memory.store(lpServices, ptr)

        self.state.mem[lpServicesReturned].uint32_t = 1
        
        return 1 # BOOL
