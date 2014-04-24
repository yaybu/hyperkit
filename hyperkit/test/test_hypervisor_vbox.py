import unittest2
import mock

from hyperkit.hypervisor.command import Command
from hyperkit.hypervisor import vbox


class TestVBoxCommandIntegration(unittest2.TestCase):

    """ These are integration tests strictly, to ensure we're calling the
    right subprocess calls using command.Command. """

    def setUp(self):
        Command.known_locations = ["/fake_bin"]
        self.m = vbox.VBoxMachineInstance("/does_not_exist", "foo")

    def tearDown(self):
        Command.known_locations = ()

    def assert_popen(self, m_popen, args):
        self.assertEqual(m_popen.call_args,
                         mock.call(stdin=None, args=args, cwd=None, stderr=-1, stdout=-1))

    @mock.patch("os.path.isfile")
    @mock.patch("os.access")
    @mock.patch("subprocess.Popen")
    def test_start_gui(self, m_popen, m_access, m_isfile):
        m_isfile.return_value = True
        m_access.return_value = True
        m_popen().communicate.return_value = ["", ""]
        m_popen().returncode = 0
        self.m._start(True)
        self.assert_popen(m_popen, [
                '/fake_bin/VBoxManage',
                'startvm',
                '--type', 'gui',
                'foo'])


class TestVBoxMachineInstance(unittest2.TestCase):

    def setUp(self):
        self.m = vbox.VBoxMachineInstance("/does_not_exist", "foo")
        self.m.vboxmanage = mock.MagicMock()

    def test_start_gui(self):
        self.m._start(True)
        self.assertEqual(self.m.vboxmanage.call_args, mock.call('startvm', type='gui', name='foo'))

    def test_start(self):
        self.m._start()
        self.assertEqual(self.m.vboxmanage.call_args, mock.call('startvm', type='headless', name='foo'))

    def test_stop(self):
        self.m._stop()
        self.assertEqual(self.m.vboxmanage.call_args, mock.call('controlvm', name='foo', button='acpipowerbutton'))

    @mock.patch("shutil.rmtree")
    def test_destroy(self, m_rmtree):
        self.m._destroy()
        self.assertEqual(self.m.vboxmanage.call_args, mock.call('unregistervm', name='foo'))
        self.assertEqual(m_rmtree.call_args, mock.call("/does_not_exist/foo"))

    def test_get_ip(self):
        self.m.vboxmanage.return_value = "Value: 192.168.0.1"
        ip = self.m.get_ip()
        self.assertEqual(ip, "192.168.0.1")


class TestVirtualBox(unittest2.TestCase):

    def setUp(self):
        self.vbox = vbox.VirtualBox()
        self.vbox.vboxmanage = mock.MagicMock()
        self.vbox.qemu_img = mock.MagicMock()

    def test_str(self):
        self.assertEqual(str(self.vbox), "VirtualBox")

    def test_present(self):
        self.vbox.vboxmanage.pathname = "foo"
        self.assertTrue(self.vbox.present)

    @mock.patch("os.mkdir")
    @mock.patch("__builtin__.open")
    @mock.patch("yaml.dump")
    @mock.patch("subprocess.Popen")
    @mock.patch("os.unlink")
    @mock.patch("os.rmdir")
    @mock.patch("tempfile.mkdtemp")
    def test_create(self, m_mkdtemp, m_rmdir, m_unlink, m_popen, m_metadata, m_open, m_mkdir):
        m_mkdtemp.return_value = "/fake_tmp"
        m_popen().communicate.return_value = ["", ""]
        m_popen().returncode = 0
        cloud_config = mock.MagicMock(name="cloud_config")
        m_metadata.filename = "meta-data"
        cloud_config().filename = "user-data"
        spec = mock.MagicMock()
        spec.name = "myvm"
        spec.image.distro = "mock_distro"
        self.vbox.configs['mock_distro'] = cloud_config
        self.vbox.ostype['mock_distro'] = "Mock_64"
        self.vbox.create(spec)
        self.assertEqual(m_rmdir.call_args, mock.call("/fake_tmp"))
        self.assertEqual(m_unlink.call_args_list, [
            mock.call('/fake_tmp/user-data'),
            mock.call('/fake_tmp/meta-data')])
        self.assertEqual(m_popen.call_args, mock.call(
            stdin=None,
            args=['/usr/bin/genisoimage',
                  '-output', '/home/doug/VirtualBox VMs/myvm-2014-04-23-01/seed.iso',
                  '-volid', 'cidata',
                  '-joliet', '-rock',
                  'user-data', 'meta-data'],
            cwd='/fake_tmp',
            stderr=-1,
            stdout=-1))
