import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
# Volatility
# Copyright (C) 2007-2013 Volatility Foundation
# Copyright (C) 2010,2011,2012 Michael Hale Ligh <michael.ligh@mnin.org>
#
# This file is part of Volatility.
#
# Volatility is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Volatility is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Volatility.  If not, see <http://www.gnu.org/licenses/>.
#

import volatility.plugins.gui.windowstations as windowstations
from volatility.renderers import TreeGrid
from volatility.renderers.basic import Address, Hex

class DeskScan(windowstations.WndScan):
    """Poolscaner for tagDESKTOP (desktops)"""

    def unified_output(self, data):
        return TreeGrid([("Offset", Address),
                       ("Name", str),
                       ("Next", Hex),
                       ("SessionId", int),
                       ("DesktopInfo", Hex),
                       ("fsHooks", int),
                       ("spwnd", Hex),
                       ("Windows", int),
                       ("Heap", Hex),
                       ("Size", Hex),
                       ("Base", Hex),
                       ("Limit", Hex),
                       ("ThreadId", int),
                       ("Process", str),
                       ("PID", int),
                       ("PPID", int)
                        ],
                        self.generator(data))

    def generator(self, data):
        seen = []

        for window_station in data:
            for desktop in window_station.desktops():
                offset = desktop.PhysicalAddress
                if offset in seen:
                    continue
                seen.append(offset)
                name = "{0}\\{1}".format(desktop.WindowStation.Name, desktop.Name)

                for thrd in desktop.threads():
                    yield (0, [Address(offset),
                        name,
                        Hex(desktop.rpdeskNext.v()),
                        int(desktop.dwSessionId),
                        Hex(desktop.pDeskInfo.v()),
                        int(desktop.DeskInfo.fsHooks),
                        Hex(desktop.DeskInfo.spwnd),
                        int(len(list(desktop.windows(desktop.DeskInfo.spwnd)))),
                        Hex(desktop.pheapDesktop.v()),
                        Hex(desktop.DeskInfo.pvDesktopLimit - desktop.DeskInfo.pvDesktopBase),
                        Hex(desktop.DeskInfo.pvDesktopBase),
                        Hex(desktop.DeskInfo.pvDesktopLimit),
                        int(thrd.pEThread.Cid.UniqueThread),
                        str(thrd.ppi.Process.ImageFileName),
                        int(thrd.ppi.Process.UniqueProcessId),
                        int(thrd.ppi.Process.InheritedFromUniqueProcessId)])


    def render_text(self, outfd, data):
        seen = []

        for window_station in data:
            for desktop in window_station.desktops():

                offset = desktop.PhysicalAddress
                if offset in seen:
                    continue
                seen.append(offset)

                outfd.write("*" * 50 + "\n")
                outfd.write("Desktop: {0:#x}, Name: {1}\\{2}, Next: {3:#x}\n".format(
                    offset,
                    desktop.WindowStation.Name,
                    desktop.Name,
                    desktop.rpdeskNext.v(),
                    ))
                outfd.write("SessionId: {0}, DesktopInfo: {1:#x}, fsHooks: {2}\n".format(
                    desktop.dwSessionId,
                    desktop.pDeskInfo.v(),
                    desktop.DeskInfo.fsHooks,
                    ))
                outfd.write("spwnd: {0:#x}, Windows: {1}\n".format(
                    desktop.DeskInfo.spwnd,
                    len(list(desktop.windows(desktop.DeskInfo.spwnd)))
                    ))
                outfd.write("Heap: {0:#x}, Size: {1:#x}, Base: {2:#x}, Limit: {3:#x}\n".format(
                    desktop.pheapDesktop.v(),
                    desktop.DeskInfo.pvDesktopLimit - desktop.DeskInfo.pvDesktopBase,
                    desktop.DeskInfo.pvDesktopBase,
                    desktop.DeskInfo.pvDesktopLimit,
                    ))
                ## This is disabled until we bring in the heaps plugin
                #if self._config.VERBOSE:
                #    granularity = desktop.obj_vm.profile.get_obj_size("_HEAP_ENTRY")
                #    for entry in desktop.heaps():
                #        outfd.write("  Alloc: {0:#x}, Size: {1:#x} Previous: {2:#x}\n".format(
                #            entry.obj_offset + granularity,
                #            entry.Size, entry.PreviousSize,
                #            ))
                for thrd in desktop.threads():
                    outfd.write(" {0} ({1} {2} parent {3})\n".format(
                        thrd.pEThread.Cid.UniqueThread,
                        thrd.ppi.Process.ImageFileName,
                        thrd.ppi.Process.UniqueProcessId,
                        thrd.ppi.Process.InheritedFromUniqueProcessId,
                    ))
