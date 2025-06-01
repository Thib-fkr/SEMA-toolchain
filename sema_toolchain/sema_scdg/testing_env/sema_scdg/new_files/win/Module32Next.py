import os

import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class Module32Next(angr.SimProcedure):
    def run(self, hSnapshot, lpme):
        lw.info("Module32Next called")
        # https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/nf-tlhelp32-module32first
        # Summary:
        # - use the return value of a previous call to CreateToolhelp32Snapshot to retrieve data
        # - place the data in the pointer as a MODULEENTRY32 structure
        # - return either TRUE or FALSE depending on if the module has been successfully copied in the buffer
        # - can set the last error to ERROR_NO_MORE_FILES if either no snapshot exist or no module info was found
        return
