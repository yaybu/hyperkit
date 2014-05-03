
"""

These are System tests

They will only work if you have all the moving parts available

"""

import sys
import os
import unittest2
import subprocess
import random
import tempfile
import shutil

from hyperkit.hypervisor import vbox
from hyperkit.hypervisor import vmware

class TestSystem(unittest2.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp(prefix="/var/tmp/tmp")

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def _hyperkit(self, args):
        command = ["hyperkit", "--directory", self.tempdir] + args
        p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        return dict(
            stdout=stdout.splitlines(),
            stderr=stderr.splitlines(),
            code=p.returncode
        )

    def hyperkit(self, args):
        r = self._hyperkit(args)
        return r

    def generate_name(self):
        def rndchr():
            for i in range(10):
                yield chr(65 + random.randint(0, 25))
        return "".join(rndchr())

    @unittest2.skipIf(not os.environ.get("HYPERKIT_SYSTEM_TEST", None), "Not executing system test")
    def test_bare_create(self):
        name = self.generate_name()
        self.hyperkit(["create", name])
