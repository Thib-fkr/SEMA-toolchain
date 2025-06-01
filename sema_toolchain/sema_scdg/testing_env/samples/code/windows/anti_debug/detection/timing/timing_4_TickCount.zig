// This sample uses the GetTickCount function to evaluate the time
// spent by the program to run some arbitrary code.
// If the time spent is greater than a manually set threshold,
// It could mean the code is running through a debugger.

const std = @import("std");
const win = std.os.windows;
const debug = std.debug;

extern "kernel32" fn GetTickCount() callconv(win.WINAPI) win.DWORD;
const threshold = 23000000; // ! Arbitrary threshold

pub fn main() void {
    const timing1 = GetTickCount();

    // ? Arbitrary time consuming task
    var t: usize = 2;
    for (0..1000000) |i| {
        if ((i + timing1) % 13 == 0) {
            t += std.math.divFloor(usize, timing1 + 2 * i, 13) catch 0;
        } else {
            t += std.math.divFloor(usize, timing1 + i, 17) catch 0;
        }
    }
    debug.print("[+] Time-consuming task: {d}", .{t});

    const timing2 = GetTickCount();

    const diff = timing2 - timing1;

    if (diff > threshold) {
        debug.print("[#] Potential debugger side-effect detected, the execution is abnormaly slow\n", .{});
    } else {
        debug.print("[+] No debugger found !\n", .{});
    }
    return;
}
