#! /usr/bin/env python

"""

These are System tests

They will only work if you have all the moving parts available

"""

import wingdbstub
import datetime
import os
import time
import unittest
import subprocess
import random
import shutil
import threading

vm_dir = os.path.realpath("test_vm")
report_dir = os.path.realpath("test_reports")

systems = ["vbox", "vmware"]

distros = [{
    "name": "ubuntu",
    "releases": ["14.04", "12.04"],
    "architectures": ["amd64", "i386"],
}, {
    "name": "fedora",
    "releases": ["20", "19"],
    "architectures": ["x86", "x86_64"],
}]


class TestSystem(unittest.TestCase):

    timeout = 500

    def setUp(self):
        self.tempdir = vm_dir

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def killkillkill(self, p):
        if p.poll() is None:
            print "Process taking too long, terminating"
            try:
                p.kill()
            except:
                # race condition
                pass

    def hyperkit(self, hypervisor, command, args):
        command = ["hyperkit",
                   "--debug",
                   "--directory", self.tempdir,
                   "--hypervisor", hypervisor,
                   command,
                   ] + args
        print "Executing", " ".join(command)
        t = time.time()
        p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        th = threading.Timer(self.timeout, self.killkillkill, [p])
        th.start()
        stdout, stderr = p.communicate()
        th.cancel()
        print "Command completed in", time.time() - t, "seconds"
        #for l in stderr.splitlines():
        #    print l
        return dict(stdout=stdout, stderr=stderr, code=p.returncode)

    def generate_name(self):
        def rndchr():
            for i in range(10):
                yield chr(65 + random.randint(0, 25))
        return "".join(rndchr())

    def test_system(self):
        d = datetime.datetime.now()
        self.run = "%04d-%02d-%02d-%010d" % (d.year, d.month, d.year, time.time())
        self.rundir = os.path.join(report_dir, self.run)
        os.mkdir(self.rundir)
        start = time.time()
        for system in systems:
            system_start = time.time()
            for distro in distros:
                distro_start = time.time()
                for release in distro["releases"]:
                    release_start = time.time()
                    for arch in distro["architectures"]:
                        self.exec_test( system=system, distro=distro["name"], release=release, arch=arch)
                    print "Release tested in", time.time() - release_start, "s"
                print "Distro tested in", time.time() - distro_start
            print "System tested in", time.time() - system_start
        print "Tests completed in", time.time() - start

    def exec_test(self, system, distro, release, arch):
        print "Testing", system, distro, release, arch
        name = self.generate_name()
        print "Creating virtual machine", name
        instance = "-".join([system, distro, release, arch])

        def run(command, args):
            r = self.hyperkit(system, command, args)
            for key, value in r.items():
                lf = open(os.path.join(self.rundir, "%s.%s.%s" % (instance, command, key)), "w")
                lf.write(str(value))
            if r['code'] != 0:
                raise OSError(r)
            return r['stdout']

        try:
            run("create", [name, distro, release, arch])
        except OSError:
            print "Could not create VM"
            return
        try:
            path = run("path", [name])
            run("start", [name])
            run("wait", [name])
        except OSError:
            print "VM starting failed, will try to stop and destroy"
        try:
            run("stop", [name])
            # stopping takes time
            time.sleep(10)
        except OSError:
            print "VM Stopping failed, will try to destroy anyway"
        finally:
            self.analyze_image(system, path)
        run("destroy", [name])

    def analyze_image(self, system, path):
        """ Analyze a disk image """
        pass

if __name__ == '__main__':
    print "Running system tests"
    print "Creating virtual machines in", vm_dir
    print "Writing reports to", report_dir
    if not os.path.exists(report_dir):
        os.mkdir(report_dir)
    if not os.path.exists(vm_dir):
        os.mkdir(vm_dir)
    unittest.main()
