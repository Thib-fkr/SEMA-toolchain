// This sample uses the language's standard time evaluation
// function to measure the time spent by the program to run some arbitrary code.
// If the time spent is greater than a manually set threshold,
// It could mean the code is running through a debugger.

const std = @import("std");
const debug = std.debug;
const time = std.time;
const math = std.math;

const threshold = 7000000; // ! Arbitrary threshold

pub fn main() void {
    const timing1 = time.nanoTimestamp();

    // ? Arbitrary time consuming task
    var t: usize = 2;
    for (0..1000000) |i| {
        if ((i + @as(usize, @intCast(timing1))) % 13 == 0) {
            t += math.divFloor(usize, @as(usize, @intCast(timing1)) + 2 * i, 13) catch 0;
        } else {
            t += math.divFloor(usize, @as(usize, @intCast(timing1)) + i, 17) catch 0;
        }
    }
    debug.print("[+] Time-consuming task: {d}", .{t});

    const timing2 = time.nanoTimestamp();

    const diff = timing2 - timing1;
    if (diff > threshold) {
        debug.print("[#] Potential debugger side-effect detected, the execution is abnormaly slow\n", .{});
    } else {
        debug.print("[+] No debugger found !\n", .{});
    }
    return;
}
