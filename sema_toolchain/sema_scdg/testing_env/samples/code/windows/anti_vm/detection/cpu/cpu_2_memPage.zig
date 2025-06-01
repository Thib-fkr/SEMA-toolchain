// Techniques from Raspberry Robin
const std = @import("std");
const win = std.os.windows;
const debug = std.debug;

const MEM_STATUS_EX = extern struct {
    dwLength: win.DWORD,
    dwMemoryLoad: win.DWORD,
    ullTotalPhys: win.DWORD64,
    ullAvailPhys: win.DWORD64,
    ullTotalPageFile: win.DWORD64,
    ullAvailPageFile: win.DWORD64,
    ullTotalVirtual: win.DWORD64,
    ullAvailVirtual: win.DWORD64,
    ullAvailextendedVirtual: win.DWORD64,
};

extern "kernel32" fn GlobalMemoryStatusEx(
    lpBuffer: *MEM_STATUS_EX,
) callconv(win.WINAPI) win.BOOL;

// Check the number of available memory pages
pub fn main() !u8 {
    var mem_status: MEM_STATUS_EX = undefined;
    if (GlobalMemoryStatusEx(&mem_status) == 0) {
        debug.print("[-] Could not retrieve memory status information\n", .{});
        return 1;
    } else if (mem_status.ullTotalPhys < 0x40000000) {
        debug.print("[#] Anormaly low number of physical memory detected, may be in a virtual Machine\n", .{});
        return 0;
    }

    // Using KSHARED_USER_DATA
    if (win.SharedUserData.NumberOfPhysicalPages < 0x32000) {
        debug.print("[#] Anormaly low number of memory pages detected, may be in a virtual Machine\n", .{});
        return 0;
    }

    debug.print("[+] No anomaly found in mem page data\n", .{});
    return 0;
}
