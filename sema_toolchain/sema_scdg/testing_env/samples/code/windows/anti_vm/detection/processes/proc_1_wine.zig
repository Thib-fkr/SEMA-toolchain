// This program looks into Windows' kernel32 dll for a process named wine_get_unix_file_name. It's presence indicate that wine is also present

const std = @import("std");
const win = std.os.windows;
const W = std.unicode.utf8ToUtf16LeStringLiteral;

pub fn main() u8 {
    if (win.kernel32.GetModuleHandleW(W("kernel32.dll"))) |hk32| {
        if (win.kernel32.GetProcAddress(hk32, "wine_get_unix_file_name")) |_| {
            std.debug.print("[#] Found process kernel32.wine_get_unix_file_name associated with wine emulator", .{});
            return 0;
        } else {
            std.debug.print("[#] No process found related to wine emulator", .{});
            return 0;
        }
    } else {
        std.debug.print("[#] Could not load kernel32 library", .{});
        return 1;
    }
}
