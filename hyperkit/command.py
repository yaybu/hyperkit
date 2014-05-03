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
import sys
import argparse
import logging

from hyperkit.spec import MachineSpec, PasswordAuth, SSHAuth, Hardware, CanonicalImage, LiteralImage
from hyperkit.hypervisor import VirtualBox, VMWare

logger = logging.getLogger()


def guess_hypervisor(args):
    if args.hypervisor is not None:
        hypervisor = {"vbox": VirtualBox, "vmware": VMWare}.get(args.hypervisor, None)
        if hypervisor is None:
            print >> sys.stderr, "Specified hypervisor is not valid"
            raise SystemExit(1)
        logging.debug("%s hypervisor selected by user" % hypervisor.hypervisor_id)
    else:
        if VirtualBox.present:
            hypervisor = VirtualBox
        elif VMWare.present:
            hypervisor = VMWare
        else:
            print >> sys.stderr, "No hypervisor found"
            raise SystemExit
        logging.debug("%r hypervisor selected by inspection" % hypervisor)
    return hypervisor


def make_hypervisor(args):
    return guess_hypervisor(args)(args.directory)


def make_password_auth(args):
    logging.debug("Using password authentication for user %r" % args.username)
    return PasswordAuth(username=args.username, password=args.password)


def make_public_key_auth(args):
    raise NotImplementedError()


def guess_best_agent_key():
    keys = os.listdir(os.path.expanduser("~/.ssh"))
    keys = [x[:-4] for x in keys if x.endswith(".pub")]
    if not keys:
        raise KeyError("No keys found")
    if "id_rsa" in keys:
        return "id_rsa"
    if "id_dsa" in keys:
        return "id_dsa"
    return keys[0]


def make_agent_key_auth(args):
    logging.debug("Using ssh agent keys for user %r" % args.username)
    if args.key_id is not None:
        key_id = args.key_id
    else:
        key_id = guess_best_agent_key()
    logging.debug("Using key %r" % key_id)
    public_key = os.path.expanduser("~/.ssh/%s.pub" % key_id)
    private_key = os.path.expanduser("~/.ssh/%s" % key_id)
    if not os.path.exists(public_key):
        raise OSError("Missing public key file %r" % public_key)
    if not os.path.exists(private_key):
        raise OSError("Missing private key file %r" % private_key)
    return SSHAuth(args.username, public_key, private_key)


def make_auth(args):
    scheme = None
    # Only one of password, public_key and key_id should be specified
    if args.password is not None:
        scheme = "password"
    if args.public_key is not None:
        if scheme is not None:
            raise ValueError("Too many authentication options provided")
        scheme = "public_key"
    if args.key_id is not None:
        if scheme is not None:
            raise ValueError("Too many authentication options provided")
        scheme = "key_id"
    if scheme == "password":
        return make_password_auth(args)
    elif scheme == "public_key":
        return make_public_key_auth(args)
    else:
        return make_agent_key_auth(args)


def make_hardware(args):
    return Hardware(memory=args.memory, cpus=args.cpus)


def make_image(args):
    if args.image is not None:
        logging.debug("Using a literal image at %r" % args.image)
        return LiteralImage(args.distro, args.release, args.arch, args.image)
    logging.debug("Using a canonical distro image")
    return CanonicalImage(args.distro, args.release, args.arch)


def make_spec(args):
    auth = make_auth(args)
    hardware = make_hardware(args)
    image = make_image(args)
    return MachineSpec(args.name, auth=auth, hardware=hardware, image=image)


def create(args):
    hypervisor = make_hypervisor(args)
    spec = make_spec(args)
    logging.info("Creating a new %s machine '%s' with:" % (hypervisor, spec.name))
    logging.info("    authentication: %s" % (spec.auth, ))
    logging.info("    base image: %s" % spec.image)
    logging.info("    hardware: %s" % spec.hardware)

    vm = hypervisor.create(spec)
    logging.info("You can start this machine with: hyperkit -H %s start %s" % (hypervisor.hypervisor_id, vm.instance_id, ))


def start(args):
    hypervisor = make_hypervisor(args)
    logging.info("Starting %s machine '%s'" % (hypervisor, args.name))
    vm = hypervisor.load(args.name)
    vm.start()
    logging.info("Machine starting.")
    if args.wait:
        logging.info("Waiting for startup to complete...")
        vm.wait(0)
        logging.info("Machine is running")


def stop(args):
    hypervisor = make_hypervisor(args)
    logging.info("Stopping %s machine '%s'" % (hypervisor, args.name))
    vm = hypervisor.load(args.name)
    vm.stop(force=args.force)
    logging.info("Machine stopping")


def destroy(args):
    hypervisor = make_hypervisor(args)
    logging.info("Destroying %s machine '%s'" % (hypervisor, args.name))
    vm = hypervisor.load(args.name)
    vm.destroy()
    logging.info("Machine destroyed")


def ip(args):
    hypervisor = make_hypervisor(args)
    vm = hypervisor.load(args.name)
    print vm.get_ip()


def wait(args):
    hypervisor = make_hypervisor(args)
    vm = hypervisor.load(args.name)
    vm.wait(0)
    logging.info("Machine is running")
    print vm.get_ip()


def net(args):
    args.sub_func(args)


def net_show(args):
    hypervisor = make_hypervisor(args)
    network = hypervisor.guess_network()
    logging.info(str(network))


def main():

    default_username = os.environ.get('LOGNAME', os.environ.get('USER', 'hyperkit'))
    logging.basicConfig(level=logging.INFO, format="hyperkit: %(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--quiet", default=False, action="store_true", help="produce no output unless there is an error")
    parser.add_argument("-d", "--debug", default=False, action="store_true", help="produce lots of output")
    parser.add_argument("-H", "--hypervisor", help="The name of the hypervisor layer to use", choices=["vmware", "vbox"])
    parser.add_argument("-D", "--directory", default=None, help="The directory the VM resides in, if different from the hypervisor default")
    sub = parser.add_subparsers()

    create_parser = sub.add_parser("create", help="Create a new virtual machine")
    create_parser.add_argument("name", default="myvm", nargs="?", help="The name of the vm to create")
    create_parser.add_argument("distro", default="ubuntu", nargs="?", help="The name of the distro to use")
    create_parser.add_argument("release", nargs="?", help="The release of the distro to use")
    create_parser.add_argument("arch", nargs="?", help="The architecture of the distro to use")
    create_parser.add_argument("--username", default=default_username, help="The username of the initial user")
    create_parser.add_argument("--password", default=None, help="The password for the initial user")
    create_parser.add_argument("--public-key", default=None, help="A specific public key to be added to the initial user's authorized list")
    create_parser.add_argument("--key-id", default=None, help="The name of a key in your ~/.ssh folder")
    create_parser.add_argument("--memory", default="256", help="The amount of memory for the new virtual machine")
    create_parser.add_argument("--cpus", default="1", help="The number of cpus for the new virtual machine")
    create_parser.add_argument("--image", help="A file path or url to an image to use instead of the distro's default")
    create_parser.add_argument("--options", help="hypervisor specific options to pass to the new VM")
    create_parser.set_defaults(func=create)

    start_parser = sub.add_parser("start", help="Start a named virtual machine")
    start_parser.add_argument("name", help="The name of the virtual machine as passed to create")
    start_parser.add_argument("--wait", action="store_true", default=False, help="Wait for the machine to start before returning")
    start_parser.set_defaults(func=start)

    stop_parser = sub.add_parser("stop", help="Stop a named virtual machine")
    stop_parser.add_argument("name", help="The name of the virtual machine as passed to create")
    stop_parser.add_argument("--force", action="store_true", default=False, help="Force a power off")
    stop_parser.set_defaults(func=stop)

    destroy_parser = sub.add_parser("destroy", help="Destroy a named virtual machine")
    destroy_parser.add_argument("name", help="The name of the virtual machine as passed to create")
    destroy_parser.set_defaults(func=destroy)

    ip_parser = sub.add_parser("ip", help="Print the IP address of the virtual machine, if available")
    ip_parser.add_argument("name", help="The name of the virtual machine as passed to create")
    ip_parser.set_defaults(func=ip)

    wait_parser = sub.add_parser("wait", help="Wait until the virtual machine starts")
    wait_parser.add_argument("name", help="The name of the virtual machine as passed to create")
    wait_parser.set_defaults(func=wait)

    net_parser = sub.add_parser("net", help="Network operations")
    net_parser.set_defaults(func=net)
    netsub = net_parser.add_subparsers()

    net_show_parser = netsub.add_parser("show", help="Show the network configurations that will be used for virtual machines")
    net_show_parser.set_defaults(sub_func=net_show)

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    if args.quiet:
        logger.setLevel(logging.ERROR)
    args.func(args)
