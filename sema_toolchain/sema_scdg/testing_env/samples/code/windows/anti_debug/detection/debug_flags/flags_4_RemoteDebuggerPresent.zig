// This sample uses kernell32.CheckRemoteDebuggerPresent to retrieve and check a flag and detect the presence of a debugger

const std = @import("std");
const win = std.os.windows;
const debug = std.debug;

// https://github.com/marlersoft/zigwin32/blob/main/win32/system/diagnostics/debug.zig
pub extern "kernel32" fn CheckRemoteDebuggerPresent(
    hProcess: ?win.HANDLE,
    pbDebuggerPresent: ?*win.BOOL,
) callconv(win.WINAPI) win.BOOL;

pub fn main() !u8 {
    var pRemoteDebuggerPresent: win.BOOL = undefined;
    if (CheckRemoteDebuggerPresent(win.GetCurrentProcess(), &pRemoteDebuggerPresent) == 1 and pRemoteDebuggerPresent == 1) {
        debug.print("[#] Found debug flag with a call to CheckRemoteDebuggerPresent()\n", .{});
        return 0;
    }
    debug.print("[+] No debugger found !\n", .{});
    return 0;
}
