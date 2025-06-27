
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class RegEnumKeyExW(angr.SimProcedure):
    def run(self, hKey, dwIndex, lpName, lpcchName, lpReserved, lpClass, lpcchClass, lpftLastWriteTime):
        lw.info("Called RegEnumKeyExW")
        # ak: TODO: put a BVS value for lpcchName (used in multiple checks `check_reg_value` & `Is_RegKeyExist`)
        return 0 # LSTATUS : 0 == ERROR_SUCCES, 259 == ERROR_NO_MORE_ITEMS
