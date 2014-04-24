
import unittest2
import mock

from hyperkit.hypervisor import vmware


class TestVMX(unittest2.TestCase):

    @mock.patch("os.path.exists")
    def setUp(self, m_exists):
        m_exists.return_value = False
        self.vmx = vmware.VMX("/does_not_exist", "foo")

    def test_pathname(self):
        self.assertEqual(self.vmx.pathname, "/does_not_exist/foo.vmx")

    def test_parse_value(self):
        self.assertEqual(self.vmx.parse_value("TRUE"), True)
        self.assertEqual(self.vmx.parse_value("True"), True)
        self.assertEqual(self.vmx.parse_value("true"), True)
        self.assertEqual(self.vmx.parse_value("FALSE"), False)
        self.assertEqual(self.vmx.parse_value("False"), False)
        self.assertEqual(self.vmx.parse_value("false"), False)
        self.assertEqual(self.vmx.parse_value("foo"), "foo")
        self.assertEqual(self.vmx.parse_value("10"), 10)

    @mock.patch("__builtin__.open")
    def test_read(self, m_open):
        m_open().__iter__.return_value = [
            "#foo\n",
            "foo.bar = baz\n",
            "quux = TRUE\n",
            "zap = 10\n",
        ]
        self.vmx.read()
        self.assertEqual(self.vmx['foo']['bar'], "baz")
        self.assertEqual(self.vmx['quux'], True)
        self.assertEqual(self.vmx['zap'], 10)

    def test_fmt(self):
        self.assertEqual(self.vmx.fmt(True), '"TRUE"')
        self.assertEqual(self.vmx.fmt(False), '"FALSE"')
        self.assertEqual(self.vmx.fmt(10), '"10"')
        self.assertEqual(self.vmx.fmt("foo"), '"foo"')


class TestVMWare(unittest2.TestCase):

    def setUp(self):
        self.vmware = vmware.VMWare()
        self.vmware.vmrun = mock.MagicMock()
        self.vmware.qemu_img = mock.MagicMock()

    def test_str(self):
        self.assertEqual(str(self.vmware), "VMWare")

    def test_present(self):
        self.vmware.vmrun.pathname = "foo"
        self.assertTrue(self.vmware.present)
