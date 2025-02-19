import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
# Copyright (C) 2011-2013 Claudio Guarnieri.
# Copyright (C) 2014-2019 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import logging
import os
import re
import subprocess
import _thread
import threading
import time

from cuckoo.common.abstracts import Machinery
from cuckoo.common.config import config
from cuckoo.common.exceptions import (
    CuckooCriticalError, CuckooMachineError, CuckooMachineSnapshotError,
    CuckooMissingMachineError
)
from cuckoo.misc import Popen

log = logging.getLogger(__name__)

class IgnoreLock(object):
    """Behaves like a Lock object. Always allows the creating thread to
    ignore the lock. The lock is used to prevent Virtualbox start/stop race
    conditions. In the event of Cuckoo stopping, the scheduler should always
    be able to perform the stopping operation."""

    def __init__(self):
        self.parent = _thread.get_ident()
        self._takers = []
        self._ev = threading.Event()

    def acquire(self):
        th_ident = _thread.get_ident()
        self._takers.append(th_ident)

        if th_ident == self.parent:
            return True

        while self._takers[0] != th_ident:
            self._ev.wait(timeout=0.1)

        self._ev.clear()

        return True

    def release(self):
        self._takers.remove(_thread.get_ident())
        self._ev.set()

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

_power_lock = IgnoreLock()

class VirtualBox(Machinery):
    """Virtualization layer for VirtualBox."""

    # VM states.
    SAVED = "saved"
    RUNNING = "running"
    POWEROFF = "poweroff"
    ABORTED = "aborted"
    ERROR = "machete"

    def _initialize_check(self):
        """Run all checks when a machine manager is initialized.
        @raise CuckooMachineError: if VBoxManage is not found.
        """
        if not self.options.virtualbox.path:
            raise CuckooCriticalError(
                "VirtualBox VBoxManage path is missing, please add it to the "
                "virtualbox.conf configuration file!"
            )

        if not os.path.exists(self.options.virtualbox.path):
            raise CuckooCriticalError(
                "VirtualBox' VBoxManage not found at specified path \"%s\" "
                "(as specified in virtualbox.conf). Did you properly install "
                "VirtualBox and configure Cuckoo to use it?"
                % self.options.virtualbox.path
            )

        if self.options.virtualbox.mode not in ("gui", "headless"):
            raise CuckooCriticalError(
                "VirtualBox has been configured to run in a non-supported "
                "mode: %s. Please upgrade your configuration to reflect "
                "either 'gui' or 'headless' mode!" %
                self.options.virtualbox.mode
            )

        super(VirtualBox, self)._initialize_check()

        # Restore each virtual machine to its snapshot. This will crash early
        # for users that don't have proper snapshots in-place, which is good.
        # TODO This should be ported to all machinery engines.
        machines = self._list()
        for machine in self.machines():
            if machine.label not in machines:
                continue

            self.restore(machine.label, machine)

    def restore(self, label, machine):
        """Restore a VM to its snapshot."""
        args = [
            self.options.virtualbox.path, "snapshot", label
        ]

        if machine.snapshot:
            log.debug(
                "Restoring virtual machine %s to %s",
                label, machine.snapshot
            )
            args.extend(["restore", machine.snapshot])
        else:
            log.debug(
                "Restoring virtual machine %s to its current snapshot",
                label
            )
            args.append("restorecurrent")

        try:
            p = Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                close_fds=True
            )
            _, err = p.communicate()
            if p.returncode:
                raise OSError("error code %d: %s" % (p.returncode, err))
        except OSError as e:
            raise CuckooMachineSnapshotError(
                "VBoxManage failed trying to restore the snapshot of "
                "machine '%s' (this most likely means there is no snapshot, "
                "please refer to our documentation for more information on "
                "how to setup a snapshot for your VM): %s" % (label, e)
            )

    def start(self, label, task):
        """Start a virtual machine.
        @param label: virtual machine name.
        @param task: task object.
        @raise CuckooMachineError: if unable to start.
        """
        log.debug("Starting vm %s", label)

        if self._status(label) == self.RUNNING:
            raise CuckooMachineError(
                "Trying to start an already started VM: %s" % label
            )

        machine = self.db.view_machine_by_label(label)
        self.restore(label, machine)

        self._wait_status(label, self.SAVED)

        if self.remote_control:
            self.enable_vrde(label)

        try:
            args = [
                self.options.virtualbox.path, "startvm", label,
                "--type", self.options.virtualbox.mode
            ]

            with _power_lock:
                _, err = Popen(
                    args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    close_fds=True
                ).communicate()
            if err:
                raise OSError(err)
        except OSError as e:
            if self.options.virtualbox.mode == "gui":
                raise CuckooMachineError(
                    "VBoxManage failed starting the machine in gui mode! "
                    "In case you're on a headless server, you should probably "
                    "try using 'headless' mode. Error: %s" % e
                )
            else:
                raise CuckooMachineError(
                    "VBoxManage failed starting the machine in headless mode. "
                    "Are you sure your machine is still functioning correctly "
                    "when trying to use it manually? Error: %s" % e
                )

        self._wait_status(label, self.RUNNING)

        # Handle network dumping through the internal VirtualBox functionality.
        if "nictrace" in machine.options:
            self.dump_pcap(label, task)

    def dump_pcap(self, label, task):
        """Dump the pcap for this analysis through the VirtualBox integrated
        nictrace functionality. This is useful in scenarios where multiple
        Virtual Machines are talking with each other in the same subnet (which
        you normally don't see when tcpdump'ing on the gatway)."""
        try:
            args = [
                self.options.virtualbox.path,
                "controlvm", label,
                "nictracefile1", self.pcap_path(task.id),
            ]
            subprocess.check_call(args)
        except subprocess.CalledProcessError as e:
            log.critical("Unable to set NIC tracefile (pcap file): %s", e)
            return

        try:
            args = [
                self.options.virtualbox.path,
                "controlvm", label,
                "nictrace1", "on",
            ]
            subprocess.check_call(args)
        except subprocess.CalledProcessError as e:
            log.critical("Unable to enable NIC tracing (pcap file): %s", e)
            return

    def stop(self, label):
        """Stop a virtual machine.
        @param label: virtual machine name.
        @raise CuckooMachineError: if unable to stop.
        """
        log.debug("Stopping vm %s" % label)

        status = self._status(label)

        # The VM has already been restored, don't shut it down again. This
        # appears to be a VirtualBox-specific state though, hence we handle
        # it here rather than in Machinery._initialize_check().
        if status == self.SAVED:
            return

        if status == self.POWEROFF or status == self.ABORTED:
            raise CuckooMachineError(
                "Trying to stop an already stopped VM: %s" % label
            )

        vm_state_timeout = config("cuckoo:timeouts:vm_state")

        try:
            args = [
                self.options.virtualbox.path, "controlvm", label, "poweroff"
            ]

            with _power_lock:
                proc = Popen(
                    args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    close_fds=True
                )

            # Sometimes VBoxManage stucks when stopping vm so we needed
            # to add a timeout and kill it after that.
            stop_me = 0
            while proc.poll() is None:
                if stop_me < vm_state_timeout:
                    time.sleep(1)
                    stop_me += 1
                else:
                    log.debug("Stopping vm %s timeouted. Killing" % label)
                    proc.terminate()

            if proc.returncode != 0 and stop_me < vm_state_timeout:
                _, err = proc.communicate()
                log.debug(
                    "VBoxManage exited with error powering off the "
                    "machine: %s", err
                )
                raise OSError(err)
        except OSError as e:
            raise CuckooMachineError(
                "VBoxManage failed powering off the machine: %s" % e
            )

        self._wait_status(label, self.POWEROFF, self.ABORTED, self.SAVED)

    def _list(self):
        """List virtual machines installed.
        @return: virtual machine names list.
        """
        try:
            args = [
                self.options.virtualbox.path, "list", "vms"
            ]
            output, _ = Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                close_fds=True
            ).communicate()
        except OSError as e:
            raise CuckooMachineError(
                "VBoxManage error listing installed machines: %s" % e
            )

        machines = []
        for line in output.split("\n"):
            if '"' not in line:
                continue

            label = line.split('"')[1]
            if label == "<inaccessible>":
                log.warning(
                    "Found an inaccessible virtual machine, please check "
                    "its state."
                )
                continue

            machines.append(label)
        return machines

    def vminfo(self, label, field):
        """Return False if invoking vboxmanage fails. Otherwise return the
        VM information value, if any."""
        try:
            args = [
                self.options.virtualbox.path,
                "showvminfo", label, "--machinereadable"
            ]
            proc = Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                close_fds=True
            )
            output, err = proc.communicate()

            if proc.returncode != 0:
                if "VBOX_E_OBJECT_NOT_FOUND" in err:
                    raise CuckooMissingMachineError(
                        "The virtual machine '%s' doesn't exist! Please "
                        "create one or more Cuckoo analysis VMs and properly "
                        "fill out the Cuckoo configuration!" % label
                    )

                # It's quite common for virtualbox crap utility to exit with:
                # VBoxManage: error: Details: code E_ACCESSDENIED (0x80070005)
                # So we just log to debug this.
                log.debug(
                    "VBoxManage returns error checking status for "
                    "machine %s: %s", label, err
                )
                return False
        except OSError as e:
            log.warning(
                "VBoxManage failed to check status for machine %s: %s",
                label, e
            )
            return False

        for line in output.split("\n"):
            if not line.startswith("%s=" % field):
                continue

            if line.count('"') == 2:
                return line.split('"')[1].lower()
            else:
                return line.split("=", 1)[1]

    def _status(self, label):
        """Get current status of a vm.
        @param label: virtual machine name.
        @return: status string.
        """
        status = self.vminfo(label, "VMState")
        if status is False:
            status = self.ERROR

        # Report back status.
        if status:
            self.set_status(label, status)
            return status

        raise CuckooMachineError(
            "Unable to get status for %s" % label
        )

    def dump_memory(self, label, path):
        """Take a memory dump.
        @param path: path to where to store the memory dump.
        """

        try:
            args = [self.options.virtualbox.path, "-v"]
            proc = Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                close_fds=True
            )
            output, err = proc.communicate()

            if proc.returncode != 0:
                # It's quite common for virtualbox crap utility to exit with:
                # VBoxManage: error: Details: code E_ACCESSDENIED (0x80070005)
                # So we just log to debug this.
                log.debug(
                    "VBoxManage returns error checking status for "
                    "machine %s: %s", label, err
                )
        except OSError as e:
            raise CuckooMachineError(
                "VBoxManage failed to return its version: %s" % e
            )

        # VirtualBox version 4, 5 and 6
        if output.startswith(("5", "6")):
            dumpcmd = "dumpvmcore"
        else:
            dumpcmd = "dumpguestcore"

        try:
            args = [
                self.options.virtualbox.path,
                "debugvm", label, dumpcmd, "--filename", path
            ]

            Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                close_fds=True
            ).wait()

            log.info(
                "Successfully generated memory dump for virtual machine "
                "with label %s to path %s", label, path.encode("utf8")
            )
        except OSError as e:
            raise CuckooMachineError(
                "VBoxManage failed to take a memory dump of the machine "
                "with label %s: %s" % (label, e)
            )

    def enable_remote_control(self, label):
        self.remote_control = True

    def enable_vrde(self, label):
        try:
            proc = self._set_flag(label, "vrde", "on")
            if proc.returncode != 0:
                log.error("VBoxManage returned non-zero value while enabling "
                          "remote control: %d" % proc.returncode)
                return False

            proc = self._set_flag(label, "vrdemulticon", "on")
            if proc.returncode != 0:
                log.error("VBoxManage returned non-zero value while enabling "
                          "remote control multicon: %d" % proc.returncode)
                return False

            self._set_vrde_ports(label, self.options.virtualbox.controlports)

            log.info(
                "Successfully enabled remote control for virtual machine "
                "with label %s on port(s): %s",
                label, self.vminfo(label, "vrdeports")
            )
        except OSError as e:
            raise CuckooMachineError(
                "VBoxManage failed to enable remote control: %s" % e
            )

    def disable_remote_control(self, label):
        try:
            proc = self._set_flag(label, "vrde", "off")
            if proc.returncode != 0:
                log.error(
                    "VBoxManage returned non-zero value while "
                    "disabling remote control: %d" % proc.returncode
                )
                return False

            log.info(
                "Successfully disabled remote control for virtual machine "
                "with label %s" % label
            )
        except OSError as e:
            raise CuckooMachineError(
                "VBoxManage failed to disable remote control: %s" % e
            )

    def get_remote_control_params(self, label):
        port = int(self.vminfo(label, "vrdeport"))
        if port < 0:
            log.error(
                "The VirtualBox Extension Pack hasn't been installed or "
                "VirtualBox hasn't been restarted since installation. "
                "Without the Extension Pack, Remote Control is disabled!"
            )

        # TODO The Cuckoo Web Interface may be running at a different host
        # than the actual Cuckoo daemon (and as such, the VMs).
        return {
            "protocol": "rdp",
            "host": "127.0.0.1",
            "port": port,
        }

    def _set_vrde_ports(self, label, ports):
        if not re.match("^[0-9\\-]+$", ports):
            log.error("Refusing to set illegal port range for VRDE")
            return False

        proc = self._set_flag(label, "vrdeport", ports)
        if proc.returncode != 0:
            log.error(
                "VboxManage returned non-zero return status while "
                "setting remote control ports: %d" % proc.returncode
            )
            return False

        log.info(
            "Successfully set remote control ports for virtual machine "
            "with label %s: %s" % (label, ports)
        )
        return proc

    # TODO Optimize this method away simply by invoking "vboxmanage modifyvm"
    # once with all parameters (i.e., --vrde --vrdeport 1234 etc).
    def _set_flag(self, label, key, val):
        args = [
            self.options.virtualbox.path, "modifyvm", label,
            "--%s" % key, val
        ]
        proc = Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            close_fds=True
        )
        _, _ = proc.communicate()
        return proc

    @staticmethod
    def version():
        """Get the version for the installed Virtualbox"""
        try:
            proc = Popen(
                [config("virtualbox:virtualbox:path"), "--version"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True
            )
            output, err = proc.communicate()
        except OSError:
            return None

        output = output.strip()
        version = ""
        for c in output:
            if not c.isdigit() and c != ".":
                break
            version += c

        # A 3 digit version number is expected. If it has none or fewer, return
        # None because we are unsure what we have.
        if len(version.split(".", 2)) < 3:
            return None

        return version
