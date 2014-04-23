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
