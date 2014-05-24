#! /usr/bin/env python

"""

These are System tests

They will only work if you have all the moving parts available

"""

import os
import time
import subprocess
import threading
import sqlite3

from . import sql


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
        dbpath = os.path.join(directory, self.db_name)
        if not os.path.exists(dbpath):
            print "Database %s does not exist - have you specified the test directory?" % dbpath
            raise SystemExit
        self.directory = directory
        self.db = sqlite3.connect(dbpath)

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

    def terminate(self, p):
        if p.poll() is None:
            print "Process taking too long, terminating"
            try:
                p.kill()
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
        p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        th = threading.Timer(self.timeout, self.terminate, [p])
        th.start()
        stdout, stderr = p.communicate()
        th.cancel()
        print "Command completed in %0.2fs" % (time.time() - t)
        return dict(stdout=stdout, stderr=stderr, code=p.returncode)

    def exec_test(self, hypervisor, distro, release, arch):
        instance = "-".join([hypervisor, distro, release, arch])
        name = "system_test-" + instance
        results = {}

        path = os.path.join(self.directory, name)
        if os.path.exists(path):
            raise KeyError("Path %r already exists" % path)

        for stage in ["create", "start", "wait", "stop"]:
            args = [name, distro, release, arch] if stage == "create" else [name]
            r = self.hyperkit(stage, hypervisor, args)
            results[stage] = r
            if r['code'] != 0:
                results['failed_at'] = stage
                self.cleanup(hypervisor, name)
                return results

        # actually wait for it to stop
        time.sleep(10)

        results["analysis"] = self.analyze_image(hypervisor, path)
        self.cleanup(hypervisor, name)
        return results

    def cleanup(self, hypervisor, name):
        self.hyperkit("cleanup", hypervisor, ["--yes", name])

    def analyze_image(self, hypervisor, name):
        """ Analyze a disk image """
        pass
