import os
import sys


import logging
import sys
import angr

import os

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)
from procedures.WindowsSimProcedure import WindowsSimProcedure

class LoadLibraryExA(angr.SimProcedure):
    def run(self, lib_ptr, flag1, flag2):
        call_sim = WindowsSimProcedure()
        proj = self.state.project
        try:
            lib = self.state.mem[lib_ptr].string.concrete
            if hasattr(lib, "decode"):
                lib = lib.decode("utf-8")
        except:
            pass
            # import pdb; pdb.set_trace()
        lib = str(lib).lower()
        # We will create a fake symbol to represent the handle to the library
        # Check first if we already did that before
        symb = proj.loader.find_symbol(lib)
        if symb:
            # Yeah !
            self.state.globals["loaded_libs"][symb.rebased_addr] = lib
            return symb.rebased_addr
        else:
            lw.debug("LoadLibraryExA: Symbol not found")
            extern = proj.loader.extern_object
            addr = extern.get_pseudo_addr(lib)
            self.state.globals["loaded_libs"][addr] = lib
            try:
                # import pdb; pdb.set_trace()
                str_lib = str(lib)
                if ".dll" not in lib:
                    lib = str_lib + ".dll"
                self.state.project.loader.requested_names.add(lib)
                call_sim.loadlibs_proc(
                    call_sim.ddl_loader.load(self.state.project), self.state.project
                )
            except Exception as inst:
                # self.log.warning(type(inst))    # the exception instance
                lw.warning(inst)  # __str__ allows args to be printed directly,
                exc_type, exc_obj, exc_tb = sys.exc_info()
                # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                lw.warning(exc_type, exc_obj)
                lw.debug("LoadLibraryExA: Fail to load dynamically lib " + str(lib))
                exit(-1)

            # import pdb; pdb.set_trace()
            return addr
        return lib_ptr
        return self.load(lib)

    def load(self, lib):
        if "." not in lib:
            lib += ".dll"

        loaded = self.project.loader.dynamic_load(lib)
        if loaded is None:
            lw.debug("LoadLibraryExA: Could not load %s", lib)
            return 0

        # Add simprocedures
        for obj in loaded:
            self.register(obj)

        lw.debug("LoadLibraryExA: Loaded %s", lib)
        return self.project.loader.find_object(lib).mapped_base

    def register(self, obj):  # can be overridden for instrumentation
        self.project._register_object(obj, obj.arch)
