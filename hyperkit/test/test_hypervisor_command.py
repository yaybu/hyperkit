
import unittest2
import mock

from hyperkit.hypervisor import command


class TestCommand(unittest2.TestCase):

    def setUp(self):
        self.logger = mock.MagicMock()
        command.logger = self.logger
        self.command = command.Command()
        self.command.command_name = "thing"
        self.command.known_locations = [
            "/fake_bin1",
            "/fake_bin2",
        ]
        self.command.subcommands = {
            "foo": ["bar", "{baz}"],
        }
        self.command.log_stderr = True
        self.command.log_stdout = True

    @mock.patch("os.path.isfile")
    @mock.patch("os.access")
    def test_pathname_found_onpath(self, m_access, m_isfile):
        def isfile(pathname):
            return pathname == "/fake_bin/thing"
        m_isfile.side_effect = isfile
        m_access.return_value = True
        with mock.patch.dict("os.environ", {'PATH': "/fake_bin"}):
            self.assertEqual(self.command.pathname, "/fake_bin/thing")

    @mock.patch("os.path.isfile")
    @mock.patch("os.access")
    def test_pathname_found_known_location(self, m_access, m_isfile):
        m_isfile.side_effect = lambda x: x == "/fake_bin2/thing"
        m_access.return_value = True
        self.assertEqual(self.command.pathname, "/fake_bin2/thing")

    @mock.patch("os.path.isfile")
    @mock.patch("os.access")
    def test_pathname_not_found(self, m_access, m_isfile):
        m_isfile.return_value = False
        m_access.return_value = True
        self.assertRaises(OSError, getattr, self.command, "pathname")

    @mock.patch("os.path.isfile")
    @mock.patch("os.access")
    def test_compose(self, m_access, m_isfile):
        m_isfile.return_value = m_access.return_value = True
        self.assertEquals(self.command.compose("foo", baz="zorg"), [
            "/fake_bin1/thing", "bar", "zorg"])
        self.assertEquals(self.command.compose("foo", "quux", baz="zorg"), [
            "/fake_bin1/thing", "bar", "zorg", "quux"])

    def test_parse(self):
        self.assertEqual(self.command.parse("foo ", "bar"), "foo")

    @mock.patch("subprocess.Popen")
    def test_execute(self, m_popen):
        m_popen().communicate.return_value = ["blah ", "errol"]
        m_popen().returncode = 0
        stdout = self.command.execute(["foo", "bar"], None)
        self.assertEqual(stdout, "blah")
        self.assertEqual(m_popen.call_args, mock.call(
            stdin=None,
            args=["foo", "bar"],
            cwd=None,
            stderr=-1, stdout=-1))
        self.assertEqual(self.logger.debug.call_args_list, [
            mock.call('Output from foo bar'),
            mock.call('STDOUT: blah '),
            mock.call('STDERR: errol'),
        ])

    @mock.patch("os.path.isfile")
    @mock.patch("os.access")
    @mock.patch("subprocess.Popen")
    def test_call(self, m_popen, m_access, m_isfile):
        m_popen().communicate.return_value = ["blah ", "errol"]
        m_popen().returncode = 0
        m_isfile.return_value = m_access.return_value = True
        stdout = self.command("foo", baz="zorg")
        self.assertEquals(stdout, "blah")
        self.assertEqual(m_popen.call_args, mock.call(
            stdin=None,
            args=["/fake_bin1/thing", "bar", "zorg"],
            cwd=None,
            stderr=-1, stdout=-1))
        stdout = self.command("foo", baz="zorg", cwd="/does_not_exist")
        self.assertEquals(stdout, "blah")
        self.assertEqual(m_popen.call_args, mock.call(
            stdin=None,
            args=["/fake_bin1/thing", "bar", "zorg"],
            cwd="/does_not_exist",
            stderr=-1, stdout=-1))
