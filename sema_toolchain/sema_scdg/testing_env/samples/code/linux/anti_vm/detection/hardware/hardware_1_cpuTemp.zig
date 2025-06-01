const std = @import("std");
const debug = std.debug;
const fs = std.fs;

pub fn main() !u8 {
    fs.accessAbsolute("/sys/class/thermal/thermal_zone0", .{}) catch |err| switch (err) {
        fs.Dir.AccessError.FileNotFound => {
            debug.print("[#] Could not found thermal information in sys/class/thermal\n", .{});
            return 0;
        },
        else => {},
    };

    debug.print("[+] No anomaly found with the thermal information of the machine\n", .{});
    return 0;
}
