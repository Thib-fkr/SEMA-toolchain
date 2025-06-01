
import os
import claripy
import logging
import angr

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)


class __stdio_common_vswprintf_s(angr.SimProcedure):
    def run(self, Options, _Buffer, _BufferCount, _Format, _Locale, _ArgList):
        # al-khaser:
        #   - _Options is always 0
        #   - _Stream is always the retval of acrt_iob_func
        #   - _Locale is always NULL

        if _Buffer.symbolic or _BufferCount.symbolic or _Format.symbolic or _ArgList.symbolic:
            lw.warning("[-] Sym arg passed to printf-lookalike func: __stdio_common_vswprintf_s")
            return

        buf_ptr = self.state.solver.eval(_Buffer)
        if buf_ptr == 0:
            lw.warning("[-] Invalid buffer ptr passed to printf-lookalike func: __stdio_common_vswprintf_s")
            return

        buf_count = self.state.solver.eval(_BufferCount)
        if buf_count < 0:
            lw.warning("[-] Invalid buffer count passed to printf-lookalike func: __stdio_common_vswprintf_s")
            return

        fmt_ptr = self.state.solver.eval(_Format)
        if fmt_ptr == 0:
            lw.warning("[-] Invalid format ptr passed to printf-lookalike func: __stdio_common_vswprintf_s")
            return

        args_ptr = self.state.solver.eval(_ArgList)
        if args_ptr == 0:
            lw.warning("[-] Invalid ArgList ptr passed to printf-lookalike func: __stdio_common_vswprintf_s")
            return

        fmt_wstr = self.state.mem[fmt_ptr].wstring.concrete
        
        # NOTE: Hopefully every '%' symbol is a format specifier and is not escaped
        arg_count = str.count(fmt_wstr, '%')
        for i in range(arg_count):
            if '%' not in fmt_wstr:
                lw.warning("[-] Error while formating string in __stdio_common_vswprintf_s")
                return

            va_args_ptr = self.state.mem[args_ptr + i*8].uint64_t.resolved

            # Get the type of the argument
            format_specifier = fmt_wstr[str.find(fmt_wstr, '%')+1]
            if format_specifier == 's':
                va_arg = self.state.mem[va_args_ptr].wstring.concrete
                fmt_wstr = str.replace(fmt_wstr, "%s", va_arg, 1)
            elif format_specifier == 'd':
                va_arg = self.state.mem[va_args_ptr].int.concrete
                fmt_wstr = str.replace(fmt_wstr, "%d", str(va_arg), 1)

        if len(fmt_wstr) > buf_count: # NOTE: > or >= ?
            fmt_wstr = fmt_wstr[:buf_count]
        
        fmt_wstr = fmt_wstr + '\0'

        self.state.memory.store(_Buffer, claripy.BVV(fmt_wstr.encode("utf-16le")))

        return # int
