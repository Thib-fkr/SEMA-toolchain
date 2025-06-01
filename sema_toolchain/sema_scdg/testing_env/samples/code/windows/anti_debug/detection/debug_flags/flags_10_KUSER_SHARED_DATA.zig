// This sample checks debug flags in SharedUserData to detect the presence of a debugger

const std = @import("std");
const win = std.os.windows;
const debug = std.debug;

pub fn main() !u8 {
    // Used by malware: Raspberry Robin
    if (win.SharedUserData.KdDebuggerEnabled != 0) { // [(0xFFFFF78000000000|0x7FFE0000) + 0x2D4]
        debug.print("[#] Found Debug flag in KUSER_SHARED_DATA.KdDebuggerEnabled\n", .{});
        return 0;
    }

    debug.print("[+] No debugger found !\n", .{});
    return 0;
}
