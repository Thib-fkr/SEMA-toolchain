// This sample tries to close an invalid handle and check if the exception that should be trigered is swallowed or not.
// If it is, it can indicate the presence of a debugger
const std = @import("std");
const win = std.os.windows;
const debug = std.debug;

var is_debugged = false;
const EXCEPTION_INVALID_HANDLE: u32 = 0xC0000008;

fn custom_handler(ExceptionInfo: *win.EXCEPTION_POINTERS) callconv(win.WINAPI) c_long {
    if (ExceptionInfo.ExceptionRecord.ExceptionCode == EXCEPTION_INVALID_HANDLE) {
        is_debugged = true;
    }
    return -1; // EXCEPTION_CONTINUE_EXECUTION
}

pub fn main() !u8 {
    const veh_handler = win.kernel32.AddVectoredExceptionHandler(1, &custom_handler);
    defer _ = win.kernel32.RemoveVectoredExceptionHandler(veh_handler.?);

    const handle: win.HANDLE = @ptrFromInt(0x99999999);

    //_ = win.kernel32.CloseHandle(handle);
    _ = win.ntdll.NtClose(handle);

    // Check the debug_flag
    if (is_debugged) {
        std.debug.print("[#] Found Debug behavior with call to CloseHandle() and NtClose()\n", .{});
        return 0;
    }

    std.debug.print("[+] No debugger found !\n", .{});
    return 0;
}
