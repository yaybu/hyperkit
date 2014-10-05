#! /usr/bin/env python

"""

These are System tests

They will only work if you have all the moving parts available

"""

import unittest2
import guestfs
import os
import time
import subprocess
import threading
import sqlite3
import StringIO

from . import core
from . import sql
from . import monitor

class HyperkitTestError(Exception):
    pass

class SystemTestManager:

    db_name = "hyperkit.sqlite"
    timeout = 500
    hypervisors = ["vbox", "vmware"]

    distros = [{
        "name": "ubuntu",
        "releases": ["14.04", "12.04"],
        "architectures": ["amd64", "i386"],
    }, {
        "name": "fedora",
        "releases": ["20", "19"],
        "architectures": ["x86", "x86_64"],
    }]

    def __init__(self, directory):
        directory = os.path.realpath(directory)
        dbpath = os.path.join(directory, self.db_name)
        if not os.path.exists(dbpath):
            print "Database %s does not exist - have you specified the test directory?" % dbpath
            raise SystemExit
        self.directory = directory
        self.db = sqlite3.connect(dbpath)
        self.executing = None

    def set_hypervisors(self, hypervisors):
        c = self.cursor
        c.execute("delete from hypervisor")
        for h in hypervisors:
            c.execute(sql.hypervisor_insert, [h])
        self.db.commit()

    def set_releases(self, releases):
        for r in releases:
            if not self.check_release(*r):
                print "Bad release spec:", r
                raise SystemExit
        c = self.cursor
        c.execute("delete from candidate")
        for d, r, a in releases:
            c.execute(sql.candidate_insert, [d, r, a])
        self.db.commit()

    @property
    def cursor(self):
        return self.db.cursor()

    @classmethod
    def create(self, directory):
        if not os.path.exists(directory):
            os.mkdir(directory)
        dbpath = os.path.join(directory, self.db_name)
        print "Creating test database", dbpath
        db = sqlite3.connect(dbpath)
        cur = db.cursor()
        cur.executescript(sql.create)
        m = self(directory)
        m.set_hypervisors(self.hypervisors)
        c = m.cursor
        for d in m.distros:
            distro = d['name']
            c.execute(sql.distro_insert, [distro])
            for r in d['releases']:
                c.execute(sql.release_insert, (r, distro))
            for a in d['architectures']:
                c.execute(sql.architecture_insert, (a, distro))
                for r in d['releases']:
                    c.execute(sql.candidate_insert, (distro, r, a))
        m.db.commit()

    def check_release(self, distro, release=None, architecture=None):
        for e in self.distros:
            if e['name'] == distro:
                if release not in e['releases']:
                    print "Release", release, "not recognised for distro", distro
                    return False
                if architecture not in e['architectures']:
                    print "Architecture", architecture, "not recognised for distro", distro
                    return False
                return True
        return False

    def should_test(self, hypervisor, distro, release, architecture):
        if self.hypervisors and hypervisor not in self.hypervisors:
            return False
        if self.releases and (distro, release, architecture) not in self.releases:
            return False
        return True

    def terminate(self):
        if self.executing.poll() is None:
            print "Test taking too long, terminating running process"
            try:
                self.executing.kill()
            except:
                # ignore race condition
                pass

    def hyperkit(self, command, hypervisor, args):
        command = ["hyperkit",
                   "--debug",
                   "--directory", self.directory,
                   "--hypervisor", hypervisor,
                   command,
                   ] + args
        print "Executing", " ".join(command)
        t = time.time()
        self.executing = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = self.executing.communicate()
        return_code = self.executing.returncode
        self.executing = None
        print "Command completed in %0.2fs" % (time.time() - t)
        return dict(stdout=stdout, stderr=stderr, code=return_code)

    def test_kernel_permissions(self):
        p = subprocess.Popen(["uname", "-r"], stdout=subprocess.PIPE)
        release = p.stdout.read().strip()
        kernel = "/boot/vmlinuz-%s" % release
        if not os.access(kernel, os.R_OK):
            raise HyperkitTestError("Cannot read kernel %s. You need to chmod +r this file." % kernel)

    def exec_test(self, hypervisor, distro, release, arch):
        self.test_kernel_permissions()
        instance = "-".join([hypervisor, distro, release, arch])
        name = "system_test-" + instance
        results = {}

        path = os.path.join(self.directory, name)
        if os.path.exists(path):
            raise KeyError("Path %r already exists" % path)

        r = self.hyperkit("create", hypervisor, ["--password", "password", name, distro, release, arch])
        results['create'] = r
        if r['code'] != 0:
            self.cleanup(hypervisor, name)
            return results

        start_time = time.time()
        timer = threading.Timer(self.timeout, self.terminate)
        timer.start()

        stages = ["start", "wait", "stop"]

        for stage in stages:
            r = self.hyperkit(stage, hypervisor, [name])
            results[stage] = r
            if r['code'] != 0:
                results['failed_at'] = stage
                self.cleanup(hypervisor, name)
                timer.cancel()
                return results

        timer.cancel()

        results["analysis"] = self.analyze_image(hypervisor, name)
        self.cleanup(hypervisor, name)
        return results

    def cleanup(self, hypervisor, name):
        self.hyperkit("cleanup", hypervisor, ["--yes", name])

    def mount_guest(self, name, disk_name):
        disk_path = os.path.join(self.directory, name, disk_name)
        guest = guestfs.GuestFS(python_return_dict=True)
        guest.add_drive_opts(disk_path, readonly=1)
        guest.launch()
        guest.mount_ro("/dev/sda1", "/")
        return guest

    def analyze_image(self, hypervisor, name):
        """ Analyze a disk image """
        disk_name = name + "_disk1.vdi"  # conditional on hypervisor
        guest = self.mount_guest(name, disk_name)
        loader = unittest2.TestLoader()
        # yes this is horrific
        core.guest = guest
        suite = loader.loadTestsFromModule(core)
        results = StringIO.StringIO()
        unittest2.TextTestRunner(stream=results, verbosity=2).run(suite)
        guest.shutdown()
        return results.getvalue()
