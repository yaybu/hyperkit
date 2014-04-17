
"""
hyperkit create myvm

hyperkit create -h vmware --distro ubtuntu myvm
hyperkit start myvm
hyperkit stop myvm
hyperkit

"""

from hyperkit.spec import MachineSpec
from hyperkit.hypervisor import VirtualBox
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--quiet", default=False, action="store_true", help="produce no output unless there is an error")
    parser.add_argument("-H", "--hypervisor", help="The name of the hypervisor layer to use", choices=["vmware", "vbox"])
    sub = parser.add_subparsers()

    create_parser = sub.add_parser("create", help="Create a new virtual machine")
    create_parser.add_argument("name", default="hyperkit", nargs="?", help="The name of the vm to create")
    create_parser.add_argument("distro", default="ubuntu", nargs="?", help="The name of the distro to use")
    create_parser.add_argument("release", nargs="?", help="The release of the distro to use")
    create_parser.add_argument("arch", nargs="?", help="The architecture of the distro to use")
    create_parser.add_argument("--username", default="hyperkit", help="The username of the initial user")
    create_parser.add_argument("--password", default=None, help="The password for the initial user")
    create_parser.add_argument("--public-key", default=None, help="A specific public key to be added to the initial user's authorized list")
    create_parser.add_argument("--key-id", default=None, help="The name of a key in your ~/.ssh folder")
    create_parser.add_argument("--memory", default="128", help="The amount of memory for the new virtual machine")
    create_parser.add_argument("--cpus", default="1", help="The number of cpus for the new virtual machine")
    create_parser.add_argument("--image", help="A file path or url to an image to use instead of the distro's default")

    start_parser = sub.add_parser("start", help="Start a named virtual machine")
    start_parser.add_argument("name", help="The name of the virtual machine as passed to create")

    destroy_parser = sub.add_parser("destroy", help="Destroy a named virtual machine")
    destroy_parser.add_argument("name", help="The name of the virtual machine as passed to create")

    ip_parser = sub.add_parser("ip", help="Print the IP address of the virtual machine, if available")
    ip_parser.add_argument("name", help="The name of the virtual machine as passed to create")

    args = parser.parse_args()

    #spec = MachineSpec()
    #hypervisor = VirtualBox()
    #vm = hypervisor.create(spec)
    #vm.start()

