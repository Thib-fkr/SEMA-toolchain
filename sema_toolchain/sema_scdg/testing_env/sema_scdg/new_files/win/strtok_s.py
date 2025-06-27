
import os
import angr
import logging
from itertools import cycle

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)



# strtok_s:
# ---------
# - string : a pointer to a string to tokenize
# - delimiters : a pointer to a string containing delimiters to identify the token in the string to tokenize
# - context : used as a state-iterator for multiple call to strtok_s, contain the rest of the string to tokenize after having removed the first token
#
# run:
# ----
# 1) See error conditions in the link mentioned in comment
# 2) Check if we work in the first argument (first call to strtok_s) or the third argument (subsequent calls)
# 3) Find the first occurence of a delimiter
# 4) Handle the exit scenarios accordingly (first char is a delimiter or no delimiter found)
# 5) Set the delimiter to \0 (end of c-string)
# 6) Set the context to delimiter_index + 1 (beginning of the next token)
# 7) Return the pointer to first first token found
#
# NOTE
# ----
# It seems to work fine for a few calls, but in my (Thibault G.) tests it hogs 31GB of memory in only a few calls with a relatively large string to tokenize (see al-khaser, ModuleBoundsHookCheckSingle)
class strtok_s(angr.SimProcedure):
    def run(self, string, delimiters, context):
        if string.symbolic or delimiters.symbolic or context.symbolic:
            lw.warning("[+] Trying to execute strtok_s with symbolic arguments, returning NULL...")
            return self.state.solver.BVS(
                "retval_{}".format(self.display_name), self.arch.bits
            )

        return 0 # NOTE: temporary al-khaser specific fix

        first_token_ptr = self.state.solver.eval(string)
        first_token_bytes = self.state.mem[first_token_ptr].string.concrete

        delim_ptr = self.state.solver.eval(delimiters)
        delim_bytes = self.state.mem[delim_ptr].string.concrete

        context_ptr = self.state.solver.eval(context)
        context_deref_ptr = self.state.mem[context_ptr].uintptr_t.resolved # TODO : check if it works on 32 bits architectures ?
        context_deref_bytes = self.state.mem[context_deref_ptr].string.concrete

        # TODO : See the following link for error scenarios
        # https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/strtok-s-strtok-s-l-wcstok-s-wcstok-s-l-mbstok-s-mbstok-s-l?view=msvc-170#return-value
        # if delim_ptr == 0:
        #     lw.info("[-] No delimiter provided to strtok_s")
        #     return 0
    
        # if context_ptr == 0:
        #     lw.info("[-] No context provided to strtok_s")
        #     return 0
       
        # FIX : Cannot check truthiness of expression, expression could be symbolic
        # if first_token_ptr == 0 and context_deref_ptr == 0:
        #     lw.info("[-] Invalid parameters passed to strtok_s, no str and invalid context")
        #     return 0
   
        # dest is the current token
        dest_ptr = first_token_ptr if first_token_bytes else context_deref_ptr

        delim_indexes = map(bytes.find , cycle([first_token_bytes if first_token_bytes else context_deref_bytes]), delim_bytes) # Find the index of the first occurence of each delimiter in the string to tokenize
        delim_indexes = filter(lambda idx: idx > -1, delim_indexes) # Ignore delimiters not found
        delim_index = min(delim_indexes, default = -1)
        if delim_index == -1:
            # No delimiter was found in the string to tokenize
            return dest_ptr
        elif delim_index == 0:
            # The first char of dest_bytes is a delimiter
            return 0

        # Set the first occurence of the delimiter to \0
        self.state.mem[dest_ptr + delim_index].char = b'\0'
        # Set the context to the beginning of the next token
        self.state.mem[context_ptr].uintptr_t = dest_ptr + delim_index + 1

        # lw.warning(f"[+] current_token : {self.state.mem[dest_ptr].string.concrete}") # | current_ptr : {hex(dest_ptr)} | context : {self.state.mem[self.state.mem[context_ptr].uintptr_t.resolved].string.concrete}")

        # return a pointer to the first token of the string to tokenize
        return dest_ptr # char*

