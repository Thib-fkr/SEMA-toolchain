// Techniques from Raspberry Robin
const std = @import("std");
const win = std.os.windows;
const debug = std.debug;

// check the number of active processors
pub fn main() !u8 {
    // Using the PEB
    if (win.peb().NumberOfProcessors < 2) {
        debug.print("[#] Anormaly low number of processor detected, may be in a virtual Machine\n", .{});
        return 0;
    }

    // Using GetSystemInfo
    var sys_info: win.SYSTEM_INFO = undefined;
    win.kernel32.GetSystemInfo(&sys_info);
    if (sys_info.dwNumberOfProcessors < 2) {
        debug.print("[#] Anormaly low number of processor detected, may be in a virtual Machine\n", .{});
        return 0;
    }

    // Using KSHARED_USER_DATA
    if (win.SharedUserData.ActiveProcessorCount < 2) {
        debug.print("[#] Anormaly low number of processor detected, may be in a virtual Machine\n", .{});
        return 0;
    }

    debug.print("[+] No anomaly found with the number of processors\n", .{});
    return 0;
}
