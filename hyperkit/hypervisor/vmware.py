# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import random
import collections

from hyperkit.cloudinit import CloudConfig, Seed, MetaData
from .machine import MachineInstance, Hypervisor
from .vmrun import VMRun
from .qemu_img import QEmuImg

logger = logging.getLogger(__name__)


class VMX(collections.defaultdict):

    """ A VMWare VMX configuration. """

    def __init__(self, directory, prefix):
        collections.defaultdict.__init__(self, lambda: {})
        self.directory = directory
        self.prefix = prefix
        if os.path.exists(self.pathname):
            self.read()
        else:
            self.vanilla()

    @property
    def pathname(self):
        return os.path.join(self.directory, self.prefix + ".vmx")

    def vanilla(self):
        """ Create a vanilla VMX File """
        self['config']['version'] = 8
        self['virtualhw']['version'] = 7
        self.configure_core()
        self.configure_devices()
        self.configure_toolscripts()
        self.connect_network()

    def configure_core(self, displayname="yaybu image", annotation="",
                       guestos="fedora", memsize=256, cpus=1, cores=1):
        self['displayname'] = displayname
        self['guestos'] = guestos
        self['annotation'] = annotation
        self['memsize'] = memsize
        self['cpuid']['coresPerSocket'] = cores
        self['numvcpus'] = cpus

    def configure_devices(self, usb=True, floppy=False, vmci=True):
        self['usb']['present'] = usb
        self['floppy0']['present'] = floppy
        self['vmci0']['present'] = vmci
        self['pciBridge0']['present'] = True
        for bridge in 4, 5, 6, 7:
            self['pciBridge{0}'.format(bridge)] = {
                'present': True,
                'virtualDev': 'pcieRootPort',
                'functions': 8,
            }

    def configure_toolscripts(self):
        self["toolscripts"] = {
            "afterresume": "true",
            "afterpoweron": "true",
            "beforesuspend": "true",
            "beforepoweroff": "true",
        }

    def parse_value(self, value):
        if value in ("TRUE", "true", "True"):
            value = True
        if value in ("FALSE", "false", "False"):
            value = False
        try:
            value = int(value)
        except ValueError:
            pass
        return value

    def read(self):
        """ Read a VMX File from disk """
        for l in open(self.pathname):
            l = l.strip()
            if l and not l.startswith("#"):
                name, value = [x.strip() for x in l.strip().split("=", 1)]
                value = self.parse_value(value)
                parts = name.split(".", 1)
                if len(parts) == 1:
                    self[name] = value
                elif len(parts) == 2:
                    component, prop = parts
                    self[component][prop] = value

    def fmt(self, value):
        if isinstance(value, bool):
            value = str(value).upper()
        else:
            value = str(value)
        return '"{0}"'.format(value)

    def write(self):
        """ Write the VMX File on disk """
        f = open(self.pathname, "w")
        print >> f, ".encoding = UTF8"
        for name, value in sorted(self.items()):
            if isinstance(value, dict):
                for k, v in sorted(value.items()):
                    print >> f, "{0}.{1} = {2}".format(name, k, self.fmt(v))
            else:
                print >> f, "{0} = {1}".format(name, self.fmt(value))

    def connect_iso(self, filename, device="ide0:0", present=True):
        self[device] = {
            "deviceType": "cdrom-image",
            "present": present,
            "fileName": filename,
        }

    def connect_disk(self, filename, device="scsi0:0", present=True):
        device_parent = device.split(":", 1)[0]
        self[device_parent] = {
            "virtualDev": "lsilogic",
            "present": True,
        }
        self[device] = {
            "present": present,
            "fileName": filename,
            "mode": "persistent",
            "deviceType": "disk",
        }

    def generate_mac(self):
        # valid range is 00:50:56:00:00:00 to 00:50:56:3f:ff:ff
        # we should check the mac isn't used as well
        seg1 = random.randint(0, 0x3f)
        seg2 = random.randint(0, 0xff)
        seg3 = random.randint(0, 0xff)
        return "00:50:56:{0:x}:{1:x}:{2:x}".format(seg1, seg2, seg3)

    def connect_network(self, interface="ethernet0", net_type="nat"):
        # http://sanbarrow.com/vmx/vmx-network-advanced.html

        self[interface] = {
            # determines if the interface is used at all
            "present": "TRUE",
            # bridged, nat, hostonly, custom, monitor_dev
            "connectionType": net_type,
            "virtualDev": "e1000",
            "startConnected": True,
            # static, generated or vpx
            "addressType": "static",
            "address": self.generate_mac(),
        }


class VMWareMachineInstance(MachineInstance):

    def __init__(self, directory, instance_id):
        super(VMWareMachineInstance, self).__init__(directory, instance_id)
        self.vmx = VMX(self.instance_dir, self.instance_id)
        self.vmrun = VMRun()

    def _start(self, gui=False):
        s_type = {
            True: "gui",
            False: "nogui",
        }[gui]
        self.vmrun("start", name=self.vmx.pathname, type=s_type)

    def _stop(self, force=False):
        s_type = {
            True: "hard",
            False: "soft",
            }[force]
        self.vmrun("stop", name=self.vmx.pathname, type=s_type)

    def _destroy(self):
        self.vmrun("stop", name=self.vmx.pathname)

    def get_ip(self):
        return self.vmrun("readVariable", name=self.vmx.pathname, variable="ip").strip()


class VMWareCloudConfig(CloudConfig):

    vmware_tools_install = [
        ['mount', '/dev/sr1', '/mnt'],
        ['bash', '/mnt/run_upgrader.sh'],
        ['umount', '/mnt'],
    ]

    # there is probably a neater way of doing this
    open_tools_install = [
        ['sed', '-i', "'/^# deb.*multiverse/ s/^# //'", '/etc/apt/sources.list'],
        ['apt-get', 'update'],
        ['apt-get', 'install', '-y', 'open-vm-tools'],
    ]

    runcmd = vmware_tools_install


class VMWareUbuntuCloudConfig(VMWareCloudConfig):
    packages = ['zip']


class VMWareFedoraCloudConfig(VMWareCloudConfig):
    packages = ['file', 'perl']


class VMWare(Hypervisor):

    hypervisor_id = "vmware"
    directory = os.path.expanduser("~/vmware")
    instance = VMWareMachineInstance

    configs = {
        "ubuntu": VMWareUbuntuCloudConfig,
        "fedora": VMWareFedoraCloudConfig,
    }

    def __init__(self):
        self.vmrun = VMRun()
        self.qemu_img = QEmuImg()

    @property
    def present(self):
        return self.vmrun.pathname is not None

    def __str__(self):
        return "VMWare"

    def create(self, spec, image_dir="~/.hyperkit"):

        image_dir = os.path.expanduser(image_dir)
        instance_id = self.get_instance_id(spec)
        instance_dir = os.path.join(self.directory, instance_id)

        # create the directory to hold all the bits
        logger.info("Creating directory %s" % (instance_dir, ))
        os.mkdir(instance_dir)

        # create a vanilla vmx file
        logger.info("Creating VMX file")
        vmx = VMX(instance_dir, instance_id)
        vmx.configure_core(guestos=spec.image.distro)

        # create the disk image and attach it
        disk = os.path.join(instance_dir, instance_id + "_disk1.vmdk")
        logger.info("Creating disk image from %s" % (spec.image, ))
        self.qemu_img("convert", source=spec.image.fetch(image_dir), destination=disk, format="vmdk")

        vmx.connect_disk(disk)

        # create the seed ISO
        logger.info("Creating CloudInfo Seed")
        config_class = self.configs[spec.image.distro]
        cloud_config = config_class(spec.auth)
        meta_data = MetaData(spec.name)
        seed = Seed(instance_dir, cloud_config=cloud_config, meta_data=meta_data)
        seed.write()

        # connect the seed ISO and the tools ISO
        logger.info("Connecting devices")
        vmx.connect_iso(seed.pathname)
        vmx.connect_iso("/usr/lib/vmware/isoimages/linux.iso", "ide0:1", "TRUE")
        vmx.write()
        logger.info("Machine created")
        return self.load(instance_id)

__all__ = [VMWare]
