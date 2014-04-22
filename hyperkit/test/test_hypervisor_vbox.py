import unittest2
import mock

from hyperkit.hypervisor import vbox

class TestVBoxMachineInstance(unittest2.TestCase):

    def setUp(self):
        self.m = vbox.VBoxMachineInstance("/does_not_exist", "foo")

    @mock.patch("subprocess.Popen")
    def test_start_gui(self, m_popen):
        m_popen().communicate.return_value = ["", ""]
        m_popen().returncode = 0
        self.m._start(True)
        self.assertEqual(m_popen.call_args, mock.call(
            stdin=None,
            args=[
                '/usr/bin/VBoxManage',
                'startvm',
                '--type', 'gui',
                'foo'],
            cwd=None, stderr=-1, stdout=-1))

    @mock.patch("subprocess.Popen")
    def test_start(self, m_popen):
        m_popen().communicate.return_value = ["", ""]
        m_popen().returncode = 0
        self.m._start()
        self.assertEqual(m_popen.call_args, mock.call(
            stdin=None,
            args=[
                '/usr/bin/VBoxManage',
                'startvm',
                '--type', 'headless',
                'foo'],
            cwd=None, stderr=-1, stdout=-1))
