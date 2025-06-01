// This sample tries to open the Csrss process. If it can, then the program has both admin and debug privileges.
const std = @import("std");
const debug = std.debug;
const win = std.os.windows;
const W = std.unicode.utf8ToUtf16LeStringLiteral;

// https://github.com/marlersoft/zigwin32/blob/main/win32/system/threading.zig
pub const PROCESS_ACCESS_RIGHTS = packed struct(u32) {
    TERMINATE: u1 = 0,
    CREATE_THREAD: u1 = 0,
    SET_SESSIONID: u1 = 0,
    VM_OPERATION: u1 = 0,
    VM_READ: u1 = 0,
    VM_WRITE: u1 = 0,
    DUP_HANDLE: u1 = 0,
    CREATE_PROCESS: u1 = 0,
    SET_QUOTA: u1 = 0,
    SET_INFORMATION: u1 = 0,
    QUERY_INFORMATION: u1 = 0,
    SUSPEND_RESUME: u1 = 0,
    QUERY_LIMITED_INFORMATION: u1 = 0,
    SET_LIMITED_INFORMATION: u1 = 0,
    _14: u1 = 0,
    _15: u1 = 0,
    DELETE: u1 = 0,
    READ_CONTROL: u1 = 0,
    WRITE_DAC: u1 = 0,
    WRITE_OWNER: u1 = 0,
    SYNCHRONIZE: u1 = 0,
    _21: u1 = 0,
    _22: u1 = 0,
    _23: u1 = 0,
    _24: u1 = 0,
    _25: u1 = 0,
    _26: u1 = 0,
    _27: u1 = 0,
    _28: u1 = 0,
    _29: u1 = 0,
    _30: u1 = 0,
    _31: u1 = 0,
};

// https://github.com/marlersoft/zigwin32/blob/main/win32/system/threading.zig
pub const PROCESS_ALL_ACCESS = PROCESS_ACCESS_RIGHTS{
    .TERMINATE = 1,
    .CREATE_THREAD = 1,
    .SET_SESSIONID = 1,
    .VM_OPERATION = 1,
    .VM_READ = 1,
    .VM_WRITE = 1,
    .DUP_HANDLE = 1,
    .CREATE_PROCESS = 1,
    .SET_QUOTA = 1,
    .SET_INFORMATION = 1,
    .QUERY_INFORMATION = 1,
    .SUSPEND_RESUME = 1,
    .QUERY_LIMITED_INFORMATION = 1,
    .SET_LIMITED_INFORMATION = 1,
    ._14 = 1,
    ._15 = 1,
    .DELETE = 1,
    .READ_CONTROL = 1,
    .WRITE_DAC = 1,
    .WRITE_OWNER = 1,
    .SYNCHRONIZE = 1,
};
// https://github.com/marlersoft/zigwin32/blob/main/win32/system/threading.zig
pub const PROCESS_QUERY_LIMITED_INFORMATION = PROCESS_ACCESS_RIGHTS{ .QUERY_LIMITED_INFORMATION = 1 };

// https://github.com/marlersoft/zigwin32/blob/main/win32/system/threading.zig
pub extern "kernel32" fn OpenProcess(
    dwDesiredAccess: PROCESS_ACCESS_RIGHTS,
    bInheritHandle: win.BOOL,
    dwProcessId: u32,
) callconv(win.WINAPI) ?win.HANDLE;

const pfnCsrGetProcessId = *const fn () callconv(win.WINAPI) win.DWORD;

pub fn main() !u8 {
    const hNtdll = win.LoadLibraryW(W("ntdll.dll")) catch {
        debug.print("[#] Could not load ntdll library", .{});
        return 1;
    };
    if (win.kernel32.GetProcAddress(hNtdll, "CsrGetProcessId")) |proc_addr| {
        if (OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, 0, @as(pfnCsrGetProcessId, @ptrCast(proc_addr))())) |hCsr| {
            win.CloseHandle(hCsr);
            debug.print("[#] Found potential debugger trace and privilege by opening Csrss", .{});
            return 0;
        }
    }

    debug.print("[+] No debugger found !\n", .{});
    return 0;
}
