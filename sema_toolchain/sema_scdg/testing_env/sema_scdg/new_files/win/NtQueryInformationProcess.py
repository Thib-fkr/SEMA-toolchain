import os
import logging
import angr

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)


class NtQueryInformationProcess(angr.SimProcedure):
    def run(
        self,
        ProcessHandle,
        ProcessInformationClass,
        ProcessInformation,
        ProcessInformationLength,
        ReturnLength
    ):
        if ProcessInformationClass.symbolic:
            return self.state.solver.BVS(
                "retval_{}".format(self.display_name), self.arch.bits
            )

        class_type = self.state.solver.eval(ProcessInformationClass)
        lw.warning(f"[+] (NtQuerySystemInformation) : Requested infoClass={class_type}\n")

        if class_type == 0: #ProcessBasicInformation
            procinfo = self.state.solver.BVS("Process_basic_info_{}".format(self.display_name), 64)
            self.state.memory.store(ProcessInformation, procinfo)
            teb_addr = self.state.regs.fs.concat(self.state.solver.BVV(0, 16))
            self.state.memory.store(ProcessInformation + 4, self.state.memory.load(teb_addr + 0x30,4))

        if class_type == 7: #ProcessDebugPort
            procinfo = self.state.solver.BVV(0x0, self.arch.bits)
            self.state.memory.store(ProcessInformation, procinfo)

        if class_type == 0x1E: #ProcessDebugObjectHandle
            if ProcessInformation.symbolic or ProcessInformationLength.symbolic or ReturnLength.symbolic:
                return self.state.solver.BVS(
                    "retval_{}".format(self.display_name), self.arch.bits
                )
            proc_info_ptr = self.state.solver.eval(ProcessInformation)
            proc_info_length = self.state.solver.eval(ProcessInformationLength)
            ret_length_ptr = self.state.solver.eval(ReturnLength)

            # Set the return length correctly to counter anti-anti-debugger technique (al-khaser.NtQueryInformationProcess_ProcessDebugObject check)
            if ret_length_ptr and ret_length_ptr != 0:
                self.state.mem[ret_length_ptr].uint32_t = proc_info_length

            if proc_info_ptr != ret_length_ptr:
                self.state.mem[proc_info_ptr].uint64_t = 0

            return 0xC0000353 # return STATUS_PORT_NOT_SET to emulate absence of debugger

        if class_type == 0x1F: #ProcessDebugFlags
            proc_info_ptr = self.state.solver.eval(ProcessInformation)
            self.state.mem[proc_info_ptr].uint64_t = 1

        return 0x0 # NTSTATUS
