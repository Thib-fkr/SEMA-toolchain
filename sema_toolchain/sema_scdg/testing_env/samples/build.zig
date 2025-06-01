const std = @import("std");

// Declarative construction of a build graph
pub fn build(b: *std.Build) !void {

    // Uncomment the desired build-target
    const build_target: std.Build.StandardTargetOptionsArgs = .{ .default_target = .{ .os_tag = .windows, .cpu_arch = .x86_64 } };
    //const build_target: std.Build.StandardTargetOptionsArgs = .{ .default_target = .{ .os_tag = .linux } };

    // Declare compiler options
    const target = b.standardTargetOptions(build_target);
    const optimize = b.standardOptimizeOption(.{ .preferred_optimize_mode = .Debug });

    const OS = enum { Windows, Linux, Any };
    const SRC = "code/";

    // Iterate through the src directory
    const dir = try std.fs.cwd().openDir(SRC[0..SRC.len], .{ .iterate = true });
    var walker = try dir.walk(b.allocator);
    defer walker.deinit();
    while (try walker.next()) |file| {
        switch (file.kind) {
            .file => {
                var os: OS = undefined;

                // Find OS prefix
                var directory_splitter = std.mem.splitScalar(u8, file.path, '/');
                const os_prefix = directory_splitter.first();
                if (std.mem.eql(u8, "windows", os_prefix)) {
                    os = OS.Windows;
                } else if (std.mem.eql(u8, "linux", os_prefix)) {
                    os = OS.Linux;
                } else if (std.mem.eql(u8, "any", os_prefix)) {
                    os = OS.Any;
                } else {
                    std.debug.print("[-] Unrecognized OS prefix\t: {s}\n", .{os_prefix});
                    unreachable; // ? The os prefix should always be known
                }

                // Clean file name
                var file_name_splitter = std.mem.splitBackwardsScalar(u8, file.basename, '/');
                const file_name = file_name_splitter.first();

                // Skip non-compatible files
                if ((os == .Windows and target.result.os.tag != .windows) or (os == .Linux and target.result.os.tag != .linux)) {
                    std.debug.print("[+] Ignoring path\t: {s} (Source & target mismatch)\n", .{file.basename});
                    continue;
                }

                // Construct file path
                var file_path = try b.allocator.alloc(u8, SRC.len + file.path.len);
                defer b.allocator.free(file_path);
                @memcpy(file_path[0..SRC.len], SRC);
                @memcpy(file_path[SRC.len..], file.path);
                std.debug.print("[+] Compiling path\t: {s}\n", .{file_path});

                // Compile into executable
                const exe = b.addExecutable(.{
                    .name = file_name[0 .. file_name.len - 4],
                    .root_source_file = b.path(file_path),
                    .target = target,
                    .optimize = optimize,
                });

                // Add artifact to the build graph
                b.installArtifact(exe);

                // Add run command
                const run_cmd = b.addRunArtifact(exe);
                run_cmd.step.dependOn(b.getInstallStep());
                if (b.args) |args| {
                    run_cmd.addArgs(args);
                }

                // Construct command name
                var command_name = try b.allocator.alloc(u8, file_name.len);
                defer b.allocator.free(command_name);
                @memcpy(command_name[0..4], "run_");
                @memcpy(command_name[4..], file_name[0 .. file_name.len - 4]);

                // Construct command description
                const command_desc = try b.allocator.alloc(u8, 20 + command_name.len);
                defer b.allocator.free(command_desc);
                _ = try std.fmt.bufPrint(command_desc, "Run the file named: {s}", .{command_name});

                // Add the run steps
                const run_step = b.step(command_name, command_desc);
                run_step.dependOn(&run_cmd.step);
            },
            else => {
                // Placeholder for potential debug info ?
            },
        }
    }
}
