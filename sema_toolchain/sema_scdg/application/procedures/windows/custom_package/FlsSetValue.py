import os
import sys


from .TlsSetValue import TlsSetValue


class FlsSetValue(TlsSetValue):
    KEY = "win32_fls"
