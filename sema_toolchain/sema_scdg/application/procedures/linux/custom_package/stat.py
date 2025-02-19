import os
import sys


import angr


class stat(angr.SimProcedure):
    def run(self, path, stat_buf):
        strlen = angr.SIM_PROCEDURES["libc"]["strlen"]
        p_strlen = self.inline_call(strlen, pathaddr)
        p_expr = self.state.memory.load(
            pathaddr, p_strlen.max_null_index, endness="Iend_BE"
        )
        path = self.state.solver.eval(p_expr, cast_to=bytes)
        fd = self.state.posix.open(path, self.state.solver.BVV(1, self.state.arch.bits))

        stat = self.state.posix.fstat(fd)
        # TODO: make arch-neutral
        # import pdb; pdb.set_trace()
        if self.state.arch.name == "AMD64":
            self._store_amd64(stat_buf, stat)
        else:
            self._store_i868(stat_buf, stat)
        self.state.posix.close(fd)
        return 0

    def _store_i868(self, stat_buf, stat):
        store = lambda offset, val: self.state.memory.store(
            stat_buf + offset, val, endness="Iend_LE"
        )

        store(0x00, stat.st_dev)
        store(0x04, stat.st_ino)
        store(0x08, stat.st_nlink)
        store(0x10, stat.st_mode)
        store(0x14, stat.st_uid)
        store(0x18, stat.st_gid)
        store(0x1C, self.state.solver.BVV(0, 32))
        store(0x20, stat.st_rdev)
        store(0x24, stat.st_size)
        store(0x28, stat.st_blksize)
        store(0x2C, stat.st_blocks)
        store(0x30, stat.st_atime)
        store(0x34, stat.st_atimensec)
        store(0x38, stat.st_mtime)
        store(0x3C, stat.st_mtimensec)
        store(0x40, stat.st_ctime)
        store(0x44, stat.st_ctimensec)
        store(0x48, self.state.solver.BVV(0, 32))
        store(0x4C, self.state.solver.BVV(0, 32))
        store(0x50, self.state.solver.BVV(0, 32))

    def _store_amd64(self, stat_buf, stat):
        store = lambda offset, val: self.state.memory.store(stat_buf + offset, val)

        store(0x00, stat.st_dev)
        store(0x08, stat.st_ino)
        store(0x10, stat.st_nlink)
        store(0x18, stat.st_mode)
        store(0x1C, stat.st_uid)
        store(0x20, stat.st_gid)
        store(0x24, self.state.solver.BVV(0, 32))
        store(0x28, stat.st_rdev)
        store(0x30, stat.st_size)
        store(0x38, stat.st_blksize)
        store(0x40, stat.st_blocks)
        store(0x48, stat.st_atime)
        store(0x50, stat.st_atimensec)
        store(0x58, stat.st_mtime)
        store(0x60, stat.st_mtimensec)
        store(0x68, stat.st_ctime)
        store(0x70, stat.st_ctimensec)
        store(0x78, self.state.solver.BVV(0, 64))
        store(0x80, self.state.solver.BVV(0, 64))
        store(0x88, self.state.solver.BVV(0, 64))
