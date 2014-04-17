
"""
hyperkit create myvm

hyperkit create -h vmware --distro ubtuntu myvm
hyperkit start myvm
hyperkit stop myvm
hyperkit

"""

from hyperkit.spec import MachineSpec
from hyperkit.hypervisor import VirtualBox


def main():
    spec = MachineSpec()
    hypervisor = VirtualBox()
    vm = hypervisor.create(spec)
    vm.start()
