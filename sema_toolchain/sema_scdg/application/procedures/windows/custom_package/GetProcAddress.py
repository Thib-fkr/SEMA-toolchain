import os
import sys


import json
import logging
import sys
import angr
# import procedures.dll_table as dll
from angr.calling_conventions import SimCCStdcall, SimCCMicrosoftAMD64
from angr.procedures import SIM_LIBRARIES

from procedures.WindowsSimProcedure import WindowsSimProcedure

import os

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)


class GetProcAddress(angr.SimProcedure):
    def run(self, lib_handle, name_addr):
        if not self.state.has_plugin("plugin_widechar"):
            lw.warning("The procedure GetProcAddress is using the plugin plugin_widechar which is not activated")
        call_sim = WindowsSimProcedure()
        if self.state.has_plugin("plugin_widechar") and self.state.solver.eval(name_addr) in self.state.plugin_widechar.widechar_address:
                name = self.state.mem[name_addr].wstring.concrete
        else:
            name = self.state.mem[name_addr].string.concrete
            if not isinstance(name, str):
                name = name.decode("utf-8") # TODO
        lw.debug("GetProcAddress: " + str(name))
        if(str(name) == "wine_get_unix_file_name"):
            return 0x0
        proj = self.project
        symb = proj.loader.find_symbol(str(name))
        if symb:
            # Yeah ! Symbols exist and it is already hooked (normaly)
            return symb.rebased_addr

        lib_addr = self.state.solver.eval(lib_handle)

        # import pdb; pdb.set_trace()
        if self.state.solver.eval(lib_addr) in self.state.globals["loaded_libs"]:
            lib = self.state.globals["loaded_libs"][lib_addr]
            test = lib + ".dll"
            if lib not in SIM_LIBRARIES and (test in SIM_LIBRARIES):
                lib = lib + ".dll"
        else:
            try:
                lib = self.state.mem[lib_handle].string.concrete.decode("utf-8")
            except:
                lib = self.state.mem[lib_handle].wstring.concrete
            test = lib + ".dll"
            if lib not in SIM_LIBRARIES and (test in SIM_LIBRARIES):
                lib = test
        if lib not in SIM_LIBRARIES:
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
                lw.debug("GetProcAddress: Fail to load dynamically lib " + str(lib))
                exit(-1)

        lw.debug("GetProcAddress - Query to lib : " + str(lib))

        if symb:
            # Yeah ! Symbols exist and it is already hooked (normally)
            return symb.rebased_addr
        else:
            lw.debug("GetProcAddress: Symbol not found")
            extern = proj.loader.extern_object
            addr = extern.get_pseudo_addr(name)
            if name in call_sim.sim_proc["custom_package"]:
                if not call_sim.amd64_sim_proc_hook(proj, addr, call_sim.sim_proc["custom_package"][name]):
                    call_sim.std_sim_proc_hook(proj, addr, call_sim.sim_proc["custom_package"][name])
            elif name in call_sim.sim_proc:
                if not call_sim.amd64_sim_proc_hook(proj, addr, call_sim.sim_proc[name]):
                    call_sim.std_sim_proc_hook(proj, addr, call_sim.sim_proc[name])
            elif lib in SIM_LIBRARIES:
                # import pdb; pdb.set_trace()
                proj.hook_symbol(name, SIM_LIBRARIES[lib].get(name, self.state.arch))
            else:
                # return 0x0
                return self.state.solver.BVS(
                    "retval_{}".format(self.display_name), self.arch.bits
                )
            return addr

    def retrieve_func(self, lib, name):
        from procedures.linux.CustomSimProcedureLinux import (
            gen_simproc0,
            gen_simproc1,
            gen_simproc2,
            gen_simproc3,
            gen_simproc4,
            gen_simproc5,
            gen_simproc6,
            gen_simproc7,
        )

        generic = {}
        generic["0"] = gen_simproc0
        generic["1"] = gen_simproc1
        generic["2"] = gen_simproc2
        generic["3"] = gen_simproc3
        generic["4"] = gen_simproc4
        generic["5"] = gen_simproc5
        generic["6"] = gen_simproc6
        generic["7"] = gen_simproc7

        with open("./calls/" + str(lib) + ".json", "r") as fp:
            data = json.load(fp)
            if name in data:
                num_args = len(data[name]["arguments"])
                sim_proc = generic[str(num_args)]()
                sim_proc.name = name
                return sim_proc
