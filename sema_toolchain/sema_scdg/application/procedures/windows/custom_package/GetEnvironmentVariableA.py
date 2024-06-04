import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
import logging
import angr

import os

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)


class GetEnvironmentVariableA(angr.SimProcedure):
    """
    https://docs.microsoft.com/en-us/windows/win32/api/processenv/nf-processenv-getenvironmentvariablea
    """
    def get_str(self, lpName, size):
        if not self.state.has_plugin("plugin_env_var"):
            lw.warning("The procedure GetEnvironmentVariableA is using the plugin plugin_env_var which is not activated")
        name = self.state.mem[lpName].string.concrete
        if hasattr(name, "decode"):
            name = name.decode("utf-8")
        name = name.upper()
        lw.debug(name)
        if self.state.has_plugin("plugin_env_var") and name in self.state.plugin_env_var.env_var:
            ret = self.state.plugin_env_var.env_var[name][:size]
            lw.debug(ret)
            # lw.warning(name + " " + str(size) + " " + ret)
            try:  # TODO investigate why needed with explorer
                if ret[-1] != "\0":
                    ret += "\0"
            except IndexError:
                lw.warning("IndexError - GetEnvironmentVariableA")
                ret = "\0"
            if hasattr(ret, "encode"):
                ret = ret.encode("utf-8")
        else:
            ret = None
            if self.state.has_plugin("plugin_env_var") :
                self.state.plugin_env_var.env_var[name] = None
        lw.debug(ret)
        if self.state.has_plugin("plugin_env_var"):
            self.state.plugin_env_var.env_var_requested[name] = ret
        return ret

    def run(self, lpName, lpBuffer, nSize):
        if lpName.symbolic or lpBuffer.symbolic or nSize.symbolic:
            return self.state.solver.BVS(
                "retval_{}".format(self.display_name), self.arch.bits
            )
        try:
            name = self.state.mem[lpName].string.concrete
            if name == b'COMSPEC':
                self.state.memory.store(lpBuffer, self.state.solver.BVV(b"C:\\Windows\\System32\\cmd.exe"))
                return 27
        except:
            lw.debug(self.state.memory.load(lpName,0x20))
        #size = self.state.mem[nSize].int.concrete
        size = self.state.solver.eval(nSize)
        ret_len = size

        var = self.get_str(lpName, size)
        # import pdb; pdb.set_trace()
        if var:
            new_str = self.state.solver.BVV(var)
            ret_len = len(var)

            self.state.memory.store(
                lpBuffer, new_str
            )  # ,endness=self.arch.memory_endness)
        else:
            for i in range(size):
                c = self.state.solver.BVS(
                    "c{}_env_var_{}".format(i, self.display_name), 8
                )
                self.state.memory.store(lpBuffer + i, c)
                return self.state.solver.BVS(
                    "retval_{}".format(self.display_name), self.arch.bits
                )
