// This sample checks the flags in the Process Environment Block to detect the presence of a debugger

const std = @import("std");
const win = std.os.windows;
const debug = std.debug;

// https://github.com/marlersoft/zigwin32/blob/main/win32/system/diagnostics/debug.zig
pub extern "kernel32" fn IsDebuggerPresent() callconv(win.WINAPI) win.BOOL;

pub fn main() !u8 {
    const peb = win.peb();
    if (IsDebuggerPresent() == 1) {
        debug.print("[#] Found Debug flag with a call to IsDebuggerPresent()\n", .{});
        return 0;
    } else if (peb.BeingDebugged != 0) {
        debug.print("[#] Found Debug flag by checking the value of PEB.BeingDebugged\n", .{});
        return 0;
    } else if (peb.NtGlobalFlag == 0x70) {
        debug.print("[#] Found Debug flag by checking the value of PEB.NtGlobalFlag\n", .{});
        return 0;
    }

    debug.print("[+] No debugger found !\n", .{}); // If the code reaches here, no debugger has been found
    return 0;
}
