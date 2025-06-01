// This sample uses kernel32.SetUnhandledExceptionFilter to generate an exception handler
// and checks if a manually triggered interupt exception has been swallowed or not
// in order to detect the presence of a debugger
const std = @import("std");
const win = std.os.windows;
const debug = std.debug;

var is_debugged = true;

const UnhandledExceptionFilter = *const fn (*win.EXCEPTION_POINTERS) callconv(win.WINAPI) c_long;
extern "kernel32" fn SetUnhandledExceptionFilter(
    lpTopLevelExceptionFilter: UnhandledExceptionFilter,
) callconv(win.WINAPI) UnhandledExceptionFilter;

fn custom_filter(ExceptionInfo: *win.EXCEPTION_POINTERS) callconv(win.WINAPI) c_long {
    // Intercept only the debug interrupt
    if (ExceptionInfo.ExceptionRecord.ExceptionCode == 0x80000003) {
        // debug.print("[+] (custom_filter) Intercepted debug interupt. This is expected behavior\n", .{});
        is_debugged = false;

        // Increase the IP (EIP, RIP, ...) to skip the interrupt instruction when returning
        var context_ptr = ExceptionInfo.ContextRecord;
        context_ptr.setIp(context_ptr.getRegs().ip + 1);
    }

    return -1; // EXCEPTION_CONTINUE_EXECUTION
}

pub fn main() !u8 {
    // Add an exception handle
    _ = SetUnhandledExceptionFilter(&custom_filter);

    // Raise an interrupt exception (0x80000003)
    _ = asm volatile (
        \\ int $0x3
    );

    // Check the debug_flag
    if (is_debugged) {
        debug.print("[#] Found Debug behavior via custom exception handling (UnhandledExceptionFilter)\n", .{});
        return 0;
    }

    debug.print("[+] No debugger found !\n", .{});
    return 0;
}
