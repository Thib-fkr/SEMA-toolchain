// https://evasions.checkpoint.com/src/Evasions/techniques/cpu.html

const std = @import("std");

const common_vendors = [_][]const u8{
    "bhyve bhyve", //FreeBSD HV
    "Microsoft Hv", //Hyper-V | VirtualPC
    "KVMKVMKVM", //KVM
    "prl hyperv", //Parallels
    "VBoxVBoxVBox", //VirtualBox
    "VMwareVMware", //VMware
    "XenVMMXenVMM", //Xen
};

fn cpuid_vendor(output_ptr: *[16]u8) void {
    const new_ptr: usize = asm volatile (
        \\ push %rbx
        \\ push %rdi
        \\ xor  %rbx, %rbx
        \\ xor  %rcx, %rcx
        \\ xor  %rdx, %rdx
        \\ mov  $0x40000000, %rax
        \\ cpuid
        \\ pop  %rdi
        \\ mov  %rbx, %rax
        \\ stosl
        \\ mov  %rcx, %rax
        \\ stosl
        \\ mov  %rdx, %rax
        \\ stosl
        \\ pop  %rbx
        \\ xor  %rax, %rax
        \\ mov  %rdi, %rax
        : [ret] "={rax}" (-> usize),
        : [output_ptr] "{rdi}" (output_ptr),
    );
    // std.debug.print("\n[+] CPU vendor1: \"{s}\"\n", .{@as(*[16]u8, @ptrFromInt(new_ptr))});
    // output_ptr.* = @as(*[16]u8, @ptrFromInt(@intFromPtr(output_ptr) + 12)).*;
    output_ptr.* = @as(*[16]u8, @ptrFromInt(new_ptr)).*;
}

fn cpuid_hypervisor() bool {
    return asm volatile (
        \\ xor  %rax, %rax
        \\ xor  %rcx, %rcx
        \\ mov  $0x1, %rax
        \\ cpuid
        \\ bt   $0x1F, %rcx
        \\ setc %al
        : [ret] "={al}" (-> bool),
    );
}

// Empty program
pub fn main() !u8 {
    var vendor_string: [16]u8 = undefined;
    @memset(vendor_string[0..], 0);
    cpuid_vendor(&vendor_string);
    // std.debug.print("\n[+] CPU vendor: \"{s}\"\n", .{vendor_string});

    for (common_vendors) |v| {
        if (vendor_string.len >= v.len and std.mem.eql(u8, v, vendor_string[0..v.len])) {
            std.debug.print("[#] Detected VM / Hypervisor know vendor ({s}) by querying cpuid\n", .{v});
            return 0;
        }
    }

    if (cpuid_hypervisor()) {
        std.debug.print("[#] Detected hypervisor by querying cpuid\n", .{});
        return 0;
    }
    std.debug.print("[+] No VM or hypervisor has been detected using cpuid\n", .{});
    return 0;
}

// To be aware of:
//  - Pointer to the string ([]u8 vs *[16]u8) parameter was causing not-so-well documented errors
