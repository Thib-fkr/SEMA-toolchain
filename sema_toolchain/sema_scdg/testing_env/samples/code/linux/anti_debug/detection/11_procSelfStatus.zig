// This sample looks for traces of a tracer process in the filesystem (proc/self/status)
const std = @import("std");
const linux = std.os.linux;
const debug = std.debug;
const mem = std.mem;

pub fn main() !u8 {
    const tracer_pid = "TracerPid:";

    // Open /proc/self/status in read mode
    const file = try std.fs.openFileAbsolute("/proc/self/status", .{ .mode = .read_only });
    defer file.close();

    // Create an interface to read the file nicely in a buffer
    const reader = file.reader();
    var buf: [4096]u8 = undefined;
    while (try reader.read(&buf) != 0) {

        // Look for the tracer pid
        if (mem.indexOf(u8, &buf, tracer_pid)) |i| {

            // Parse the tracer pid and compare it to a known constant
            var iterator = mem.splitAny(u8, buf[i + tracer_pid.len ..], "\n");
            if (try std.fmt.parseInt(u64, mem.trimLeft(u8, iterator.first(), "\t"), 10) != 0) {
                debug.print("[#] Found non null tracer pid in proc/self/status\n", .{});
                return 0;
            }
        } else {}
    }

    debug.print("[+] No debugger found !\n", .{});
    return 0;
}
