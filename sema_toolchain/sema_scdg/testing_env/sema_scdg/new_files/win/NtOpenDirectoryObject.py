
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class NtOpenDirectoryObject(angr.SimProcedure):
    def run(self, DirectoryHandle, DesiredAccess, ObjectAttributes):
        lw.info("Called NtOpenDirectoryObject")
        return # NTSTATUS
