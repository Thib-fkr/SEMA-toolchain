
import os
from angr.procedures.stubs.format_parser import FormatParser
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)


VFWPRINTF_GLOBAL_KEY="ak_vfwprintf"
VFWPRINTF_BUFFER_BASE_VALUE=""
VFWPRINTF_FLUSH_CHAR='\n'

class __stdio_common_vfwprintf(FormatParser):
    def run(self, Options, _Stream, _Format, _Locale, _ArgList):
        # al-khaser:
        #   - _Options is always 0
        #   - _Stream is always the retval of acrt_iob_func
        #   - _Locale is always NULL

        if _Format.symbolic or _ArgList.symbolic:
            lw.warning("[-] Sym arg passed to printf-lookalike func: __stdio_common_vfwprintf")
            return

        fmt_ptr = self.state.solver.eval(_Format)
        if fmt_ptr == 0:
            lw.warning("[-] Invalid ptr passed to printf-lookalike func: __stdio_common_vfwprintf")
            return

        args_ptr = self.state.solver.eval(_ArgList)
        if args_ptr == 0:
            lw.warning("[-] Invalid ArgList passed to printf-lookalike func: __stdio_common_vfwprintf")
            return

        # Ensures a buffer exists in the state to hold the string
        if VFWPRINTF_GLOBAL_KEY not in self.state.globals:
            self.state.globals[VFWPRINTF_GLOBAL_KEY] = VFWPRINTF_BUFFER_BASE_VALUE

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

        # Append the current string to the buffer
        self.state.globals[VFWPRINTF_GLOBAL_KEY] += fmt_wstr
        # Flush the buffer if it contains a newline
        if VFWPRINTF_FLUSH_CHAR in fmt_wstr:
            lw.warning(f"[+] vfwprintf: '{self.state.globals[VFWPRINTF_GLOBAL_KEY]}'")
            self.state.globals.pop(VFWPRINTF_GLOBAL_KEY)

        return # int
