// This sample uses ntdll.NtQueryInformationProcess to retrieve and check debug flags to detect the presence of a debugger

const std = @import("std");
const win = std.os.windows;
const ntdll = win.ntdll;
const debug = std.debug;

pub fn main() !u8 {
    const current_process = win.GetCurrentProcess();

    var process_debug_port: win.DWORD_PTR = undefined;
    const rc1 = ntdll.NtQueryInformationProcess(current_process, .ProcessDebugPort, &process_debug_port, @sizeOf(win.DWORD_PTR), null);
    switch (rc1) {
        .SUCCESS => {
            if (process_debug_port == 0xFFFFFFFF) {
                debug.print("[#] Found debug flag by checking the value of InformationProcess.DebugPort with a call to NtQueryInformationProcess()\n", .{});
                return 0;
            }
        },
        else => {
            debug.print("[#] Could not read information process (1)\n", .{});
            return win.unexpectedStatus(rc1);
        },
    }

    var process_debug_flags: win.DWORD = undefined;
    const rc2 = ntdll.NtQueryInformationProcess(current_process, .ProcessDebugFlags, &process_debug_flags, @sizeOf(win.DWORD), null);
    switch (rc2) {
        .SUCCESS => {
            if (process_debug_flags == 0x0) {
                debug.print("[#] Found debug flag by checking the value of InformationProcess.ProcessDebugFlags with a call to NtQueryInformationProcess()\n", .{});
                return 0;
            }
        },
        else => {
            debug.print("[#] Could not read information process (2)\n", .{});
            return win.unexpectedStatus(rc2);
        },
    }

    var process_debug_object_handle: win.DWORD_PTR = undefined;
    const rc3 = ntdll.NtQueryInformationProcess(current_process, .ProcessDebugObjectHandle, &process_debug_object_handle, @sizeOf(win.DWORD_PTR), null);
    switch (rc3) {
        .SUCCESS => {
            if (process_debug_object_handle != 0x0) {
                debug.print("[#] Found debug flag by checking the value of InformationProcess.ProcessDebugObjectHandle with a call to NtQueryInformationProcess()\n", .{});
                return 0;
            }
        },
        .PORT_NOT_SET => {
            // No debug port was already attached to the program
            // It is not a success, but no debugger was detected
            // So we can safely ignore the error
        },
        else => {
            debug.print("[#] Could not read information process (3)\n", .{});
            return win.unexpectedStatus(rc3);
        },
    }

    debug.print("[+] No debugger found !\n", .{});
    return 0;
}
