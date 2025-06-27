const std = @import("std");
const win = std.os.windows;
const debug = std.debug;

pub extern "kernel32" fn GetThreadContext(
    hThread: win.HANDLE,
    lpContext: *win.CONTEXT,
) callconv(win.WINAPI) win.BOOL;

pub fn main() !u8 {
    var thread_context: win.CONTEXT = std.mem.zeroes(win.CONTEXT);
    thread_context.ContextFlags = 0x00010010;
    if (GetThreadContext(win.GetCurrentThread(), &thread_context) == 1 and std.mem.indexOfScalar(u64, &[_]u64{
        thread_context.Dr0,
        thread_context.Dr1,
        thread_context.Dr2,
        thread_context.Dr3,
    }, 1) != null) {
        debug.print("[+]Debugger found\n", .{});
    }
    debug.print("[+] No debugger found !\n", .{});
    return 0;
}
