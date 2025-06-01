// This samples uses ntdll.NtQuerySystemInformation to retrieve SYSTEM_KERNEL_DEBUGGER_INFORMATION
// and check the value of flags indicating the presence of a debugger

const std = @import("std");
const win = std.os.windows;
const debug = std.debug;

// Redefinition of SYSTEM_INFORMATION_CLASS and related types
// Changes made:
//  - Added SystemKernelDebuggerInformation = 0x23
// Why ?
// ! - Only valid in Windows API versions 3.50 and higher, see https://www.geoffchappell.com/studies/windows/km/ntoskrnl/inc/api/ntexapi/system_information_class.htm
const SYSTEM_INFORMATION_CLASS = enum(c_int) {
    SystemBasicInformation = 0,
    SystemPerformanceInformation = 2,
    SystemTimeOfDayInformation = 3,
    SystemProcessInformation = 5,
    SystemProcessorPerformanceInformation = 8,
    SystemInterruptInformation = 23,
    SystemExceptionInformation = 33,
    SystemKernelDebuggerInformation = 35,
    SystemRegistryQuotaInformation = 37,
    SystemLookasideInformation = 45,
    SystemCodeIntegrityInformation = 103,
    SystemPolicyInformation = 134,
};

pub extern "ntdll" fn NtQuerySystemInformation(
    SystemInformationClass: SYSTEM_INFORMATION_CLASS,
    SystemInformation: win.PVOID,
    SystemInformationLength: win.ULONG,
    ReturnLength: ?*win.ULONG,
) callconv(win.WINAPI) win.NTSTATUS;

const SYSTEM_KERNEL_DEBUGGER_INFORMATION = struct {
    debugger_enabled: win.BOOLEAN,
    debugger_not_present: win.BOOLEAN,
};

pub fn main() !u8 {
    var system_info: SYSTEM_KERNEL_DEBUGGER_INFORMATION = undefined;
    const rc = NtQuerySystemInformation(.SystemKernelDebuggerInformation, &system_info, @sizeOf(@TypeOf(system_info)), null);
    switch (rc) {
        .SUCCESS => {
            if (system_info.debugger_enabled == 1 and system_info.debugger_not_present == 0) {
                debug.print("[#] Found debug flag by checking the value of SystemInformation[0x23] with a call to NtQuerySystemInformation()\n", .{});
                return 0;
            }
        },
        else => {
            debug.print("[#] Could not read system information, aborting...\n", .{});
            return win.unexpectedStatus(rc);
        },
    }

    debug.print("[+] No debugger found !\n", .{});
    return 0;
}
