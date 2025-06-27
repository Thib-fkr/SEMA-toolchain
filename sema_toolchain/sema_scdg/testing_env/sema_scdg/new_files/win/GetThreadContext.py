
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class GetThreadContext(angr.SimProcedure):
    def run(self: angr.SimProcedure, hThread, lpContext):
        # TODO: Only do the anti-debug bellow if the thread context is set with CONTEXT_DEBUG_REGISTERS
        context_size = 1232
        offsets = [72, 80, 88, 96]

        context = self.state.solver.BVS("CONTEXT_{}".format(self.display_name), 8*context_size)
        self.state.memory.store(lpContext, context)

        for offset in offsets:
            regval = self.state.memory.load(lpContext+offset, 8)
            self.state.add_constraints(regval == 0)

        if "mem_bp_evasion" not in self.state.globals:
            self.state.globals["mem_bp_evasion"] = []

        super_state = self.state
        super_globals = self.state.globals
        def watch_HW_BP(bp_state):
            addr_sym = bp_state.inspect.mem_read_address
            if type(addr_sym) is not int and addr_sym.symbolic:
                return

            addr = bp_state.solver.eval(addr_sym)
            thread_addr_conc = super_state.solver.eval(lpContext)
            if addr != 0 and addr in list(map(lambda a: thread_addr_conc + a, offsets)):
                lw.warning(f"\nAccessed hardware breakpoints at address: {hex(addr)} (offset: {addr-thread_addr_conc})\n")

                super_globals["mem_bp_evasion"].append(("Hardware Breakpoints", hex(addr), hex(addr-thread_addr_conc)))

        self.state.inspect.b("mem_read", when=angr.BP_BEFORE, action=watch_HW_BP)

        return 0x1
