import angr
import logging

import os

lw = logging.getLogger("CustomSimProcedureWindows")
lw.setLevel(os.environ["LOG_LEVEL"])

class _wgetenv_s(angr.SimProcedure):
    def get_str(self, lpName):
        if not self.state.has_plugin("plugin_env_var"):
            lw.warning("The procedure _wgetenv_s is using the plugin plugin_env_var which is not activated")
        name = self.state.mem[lpName].wstring.concrete
        # if hasattr(name, "decode"):
        #     name = name.decode("utf-16-le")
        name = name.upper()
        name = str(name.encode("utf-8")).replace("b'","").replace("'","")
        lw.debug(name)
        lw.debug(self.state.plugin_env_var.wenv_var.keys())
        if self.state.has_plugin("plugin_env_var") and name in self.state.plugin_env_var.wenv_var.keys() and self.state.plugin_env_var.wenv_var[name] != None:
            ret = self.state.plugin_env_var.wenv_var[name].decode("utf-16-le")
            lw.debug(ret)
            # lw.warning(name + " " + str(size) + " " + ret)
            try:  # TODO investigate why needed with explorer
                if ret[-1] != "\0":
                    ret += "\0"
            except IndexError:
                lw.warning("IndexError - GetEnvironmentVariableA")
                ret = "\0"
            if hasattr(ret, "encode"):
                ret = ret.encode("utf-16-le")
        else:
            ret =  None #"None"
            if self.state.has_plugin("plugin_env_var"):
                self.state.plugin_env_var.wenv_var[name] = None
        lw.debug(ret)
        if self.state.has_plugin("plugin_env_var"):
            self.state.plugin_env_var.wenv_var_requested[name] = ret
        return ret


    def run(self, pReturnValue, buffer, numberOfElements, varname):
        if varname.symbolic:
            lw.debug("varname is symb")
            return self.state.solver.BVS(
                "retval_{}".format(self.display_name), self.arch.bits
            )
        # Get the environment variable value
        env_value = self.get_str(varname)

        lw.debug(env_value)

        # If the environment variable is not defined, set the return value to EINVAL
        if env_value is None:
            return self.state.solver.BVS(
                    "retval_{}".format(self.display_name), self.arch.bits
            )

        # If the environment variable is defined, copy its value to the buffer
        buf_size = min(len(env_value), self.state.solver.eval(numberOfElements) - 1)
        self.state.memory.store(buffer, env_value[:buf_size] + b"\0")

        # Set the return value to zero and update pReturnValue with the number of characters copied
        self.state.memory.store(pReturnValue, buf_size, self.state.arch.bits)
        return 0x0 #self.state.solver.BVV(0, self.state.arch.bits)
