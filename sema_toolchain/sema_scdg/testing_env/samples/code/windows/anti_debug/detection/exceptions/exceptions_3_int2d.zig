// This sample uses kernel32.SetUnhandledExceptionFilter to generate an exception handler
// and checks if a manually triggered interupt exception has been swallowed or not
// in order to detect the presence of a debugger
const std = @import("std");
const win = std.os.windows;
const debug = std.debug;

const EXCEPTION_BREAKPOINT: u32 = 0x80000003;
var is_debugged = true;

fn custom_handler(ExceptionInfo: *win.EXCEPTION_POINTERS) callconv(win.WINAPI) c_long {
    if (ExceptionInfo.ExceptionRecord.ExceptionCode == EXCEPTION_BREAKPOINT) {
        // debug.print("[+] (custom_handler) Intercepted DBG_CONTROL_C. This is expected behavior.\n", .{});
        is_debugged = false;

        // Increase the IP (EIP, RIP, ...) to skip the interrupt instruction when returning
        var context_ptr = ExceptionInfo.ContextRecord;
        context_ptr.setIp(context_ptr.getRegs().ip + 1);
    }
    return -1; // EXCEPTION_CONTINUE_EXECUTION
}

pub fn main() !u8 {
    // Add a custom VEH to intercept the exception
    const veh_handle = win.kernel32.AddVectoredExceptionHandler(1, &custom_handler);
    defer _ = win.kernel32.RemoveVectoredExceptionHandler(veh_handle.?);

    // Raise an exception if no debugger is present
    _ = asm volatile (
        \\ int $0x2d
    );

    // Check the debug_flag
    if (is_debugged) {
        std.debug.print("[#] Found Debug behavior via custom exception handling (VEH)\n", .{});
        return 0;
    }

    std.debug.print("[+] No debugger found !\n", .{});
    return 0;
}
