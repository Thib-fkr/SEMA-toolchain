import angr
import logging
import os

lw = logging.getLogger("CustomSimProcedureLinux")
lw.setLevel(os.environ["LOG_LEVEL"])

class readdir(angr.SimProcedure):
    # pylint: disable=arguments-differ
    def run(self,dirp):
        lw.debug(self.cc)
        return 0
