
def placeholder(name, args, ret_type):
    return f"""
import os
import angr
import logging

try:
    lw = logging.getLogger("CustomSimProcedureWindows")
    lw.setLevel(os.environ["LOG_LEVEL"])
except Exception as e:
    print(e)

class {name}(angr.SimProcedure):
    def run(self{args}):
        lw.info("Called {name}")
        return # {ret_type}
"""


def main():
    name = input("SimProc name:")
    ret_type = input("ret_type:")
    args = input("args:")
    with open(f"new_files/win/{name}.py", 'x') as f:
        f.write(placeholder(name, args, ret_type))

    with open(f"./scdg_local/sema_scdg/application/procedures/windows/custom_package/{name}.py", 'x') as f:
        f.write(placeholder(name, args, ret_type))

if __name__ == "__main__":
    main()
