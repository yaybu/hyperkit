
import mock
import unittest2

from hyperkit.spec import spec, auth, hardware, image

class TestSpec(unittest2.TestCase):

    def test_init(self):
        s = spec.MachineSpec()
        self.assertTrue(isinstance(s.auth, auth.PasswordAuth()))
        self.assertTrue(isinstance(s.image, image.CanonicalImage()))
        self.assertTrue(isinstance(s.hardware, hardware.Hardware()))
        self.assertEqual(s.name, "myvm")

