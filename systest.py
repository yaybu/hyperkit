#! /usr/bin/env python

"""

These are System tests

They will only work if you have all the moving parts available

"""

import time
import unittest
import subprocess
import random
import tempfile
import shutil

vm_dir = "/var/tmp"

systems = ["vbox", "vmware"]

distros = [{
    "name": "ubuntu",
    "releases": ["10.04", "12.04", "14.04"],
    "architectures": ["amd64", "x86"],
}, {
    "name": "fedora",
    "releases": ["19", "20"],
    "architectures": ["x86", "x86_64"],
}]


class TestSystem(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp(prefix=vm_dir + "/vm")

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def _hyperkit(self, hypervisor, command, args):
        command = ["hyperkit",
                   "--directory", self.tempdir,
                   "--hypervisor", hypervisor,
                   command,
                   ] + args
        print "Executing", " ".join(command)
        t = time.time()
        p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        print "Command completed in", time.time() - t, "seconds"
        return dict(
            stdout=stdout.splitlines(),
            stderr=stderr.splitlines(),
            code=p.returncode
        )

    def hyperkit(self, hypervisor, command, args):

        def strip_prefix(lines):
            for l in lines:
                if l.startswith("hyperkit: "):
                    yield l[10:]
                else:
                    yield l

        r = self._hyperkit(hypervisor, command, args)
        r['stderr'] = list(strip_prefix(r['stderr']))
        return r

    def generate_name(self):
        def rndchr():
            for i in range(10):
                yield chr(65 + random.randint(0, 25))
        return "".join(rndchr())

    def test_system(self):
        for system in systems:
            for distro in distros:
                for release in distro["releases"]:
                    for arch in distro["architectures"]:
                        self.exec_test(
                            system=system,
                            distro=distro["name"],
                            release=release,
                            arch=arch)

    def exec_test(self, system, distro, release, arch):
        print "Testing", system, distro, release, arch
        name = self.generate_name()
        print "Creating virtual machine", name
        self.hyperkit(system, "create", [name, distro, release, arch])
        self.hyperkit(system, "destroy", [name])

if __name__ == '__main__':
    print "Running system tests"
    print "Creating virtual machines in", vm_dir
    unittest.main()
