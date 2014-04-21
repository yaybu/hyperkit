
import mock
import unittest2
import urllib2

from hyperkit.spec import spec, auth, hardware, image
from hyperkit import error

class TestSpec(unittest2.TestCase):

    def test_init(self):
        s = spec.MachineSpec()
        self.assertTrue(isinstance(s.auth, auth.PasswordAuth))
        self.assertTrue(isinstance(s.image, image.CanonicalImage))
        self.assertTrue(isinstance(s.hardware, hardware.Hardware))
        self.assertEqual(s.name, "myvm")

class TestLiteralImage(unittest2.TestCase):

    def setUp(self):
        self.i = image.LiteralImage("distro", "release", "arch", "url")

    def test_str(self):
        self.assertEqual(str(self.i), 'distro-release-arch at url')

    @mock.patch("os.path.exists")
    @mock.patch("urllib2.urlopen")
    @mock.patch("__builtin__.open")
    @mock.patch("os.mkdir")
    def test_fetch(self, m_mkdir, m_open, m_urlopen, m_exists):
        m_exists.return_value = True
        m_urlopen().read.side_effect = ["foo", "bar", ""]
        pathname = self.i.fetch("/does_not_exist")
        self.assertEqual(pathname, "/does_not_exist/user-distro-release-arch.28e5ebabd9d8f6e237df63da2b503785093f0229241bc7021198f63c43b93269.qcow2")
        self.assertEqual(m_open().write.call_args_list, [mock.call("foo"), mock.call("bar")])
        m_exists.return_value = False
        m_urlopen.side_effect = urllib2.HTTPError(*[None]*5)
        self.assertRaises(error.FetchFailedException, self.i.fetch, "/does_not_exist")
        self.assertEqual(m_mkdir.call_args_list, [mock.call("/does_not_exist")])

