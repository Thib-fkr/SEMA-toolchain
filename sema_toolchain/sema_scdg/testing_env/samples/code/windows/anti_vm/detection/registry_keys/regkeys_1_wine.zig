// This program looks into Windows Registry keys for a known key indicating the presence of the Wine emulator

const std = @import("std");
const win = std.os.windows;
const advapi = win.advapi32;
const W = std.unicode.utf8ToUtf16LeStringLiteral;

pub fn main() u8 {
    var hkey: win.HKEY = undefined;
    if (advapi.RegOpenKeyExW(win.HKEY_CURRENT_USER, W("SOFTWARE\\Wine"), 0, win.KEY_READ, &hkey) == 0) {
        _ = advapi.RegCloseKey(hkey);
        std.debug.print("[#] Found Registry key associated with wine emulator", .{});
        return 0;
    } else {
        std.debug.print("[+] No wine-related regkey found !\n", .{});
        return 0;
    }
}
