
import unittest2
import mock
import datetime
import os

from hyperkit.hypervisor import machine

fixed_date = datetime.datetime(2001, 1, 1)

class MockMachineInstance(machine.MachineInstance):

    ip = None

    def _start(self, gui=False):
        self.started = True
        self.started_gui = gui

    def _stop(self, force=False):
        self.stopped = True

    def _destroy(self):
        self.destroyed = True

    def get_ip(self):
        return self.ip


class TestMachineInstance(unittest2.TestCase):

    def setUp(self):
        with mock.patch("os.path.exists") as m_exists:
            m_exists.return_value = True
            self.m = MockMachineInstance("/tmp", "foo")

    def test_start(self):
        self.m.start(False)
        self.assertEqual(self.m.started, True)
        self.assertEqual(self.m.started_gui, False)
        self.assertEqual(self.m.state, machine.State.STARTING)

    def test_stop(self):
        self.m.stop()
        self.assertEqual(self.m.stopped, True)
        self.assertEqual(self.m.state, machine.State.DEAD)

    def test_destroy(self):
        self.m.destroy()
        self.assertEqual(self.m.destroyed, True)
        self.assertEqual(self.m.state, machine.State.DEAD)

    def test_wait(self):
        self.m.ip = "foo"
        self.m.wait(-1)
        self.assertEqual(self.m.state, machine.State.RUNNING)

    @mock.patch("time.time")
    @mock.patch("time.sleep")
    def test_wait_timeout(self, m_sleep, m_time):
        self.t = 0

        def time():
            return self.t

        def sleep(x):
            self.t += 1
            if self.t > 5:
                self.m.ip = "foo"
        m_sleep.side_effect = sleep
        m_time.side_effect = time
        self.m.wait(10)
        self.assertEqual(self.t, 6)


class MockHypervisor(machine.Hypervisor):

    instance = mock.MagicMock()
    directory = "/fake_dir"

    def create(self, spec, image_dir="~/.hyperkit"):
        return mock.MagicMock()

    def __str__(self):
        return "Mock Hypervisor"

    def present(self):
        return True


class TestHypervisor(unittest2.TestCase):

    def setUp(self):
        self.hypervisor = MockHypervisor()

    @mock.patch("os.path.expanduser")
    def test_set_image_dir(self, m_expanduser):
        m_expanduser.side_effect = lambda x: x.replace("~", "/bar")
        self.hypervisor.set_image_dir("~/foo")
        self.assertEqual(self.hypervisor.image_dir, "/bar/foo")

    @mock.patch("os.path.exists")
    def test_load(self, m_exists):
        m_exists.return_value = True
        instance = self.hypervisor.load("foo")
        self.assertEqual(instance, self.hypervisor.instance("/fake_dir/foo"))
        m_exists.return_value = False
        self.assertRaises(machine.MachineDoesNotExist, self.hypervisor.load, "foo")

    @mock.patch("os.path.exists")
    @mock.patch("datetime.datetime")
    def test_get_instance_id_new(self, m_datetime, m_exists):
        m_exists.return_value = False
        m_datetime.now.return_value = fixed_date
        spec = mock.MagicMock()
        spec.name = "foo"
        self.assertEqual(self.hypervisor.get_instance_id(spec), "foo")

    @mock.patch("os.path.exists")
    @mock.patch("datetime.datetime")
    def test_get_instance_id_exists(self, m_datetime, m_exists):
        m_exists.side_effect = [True, True, True, False]
        m_datetime.now.return_value = fixed_date
        spec = mock.MagicMock()
        spec.name = "foo"
        self.assertEqual(self.hypervisor.get_instance_id(spec), "foo-2001-01-01-03")

    @mock.patch("os.listdir")
    def test_instances(self, m_listdir):
        m_listdir.return_value = ['foo', 'bar', 'baz']
        self.assertEqual(list(self.hypervisor.instances()), [
            self.hypervisor.instance("/fake_dir/foo"),
            self.hypervisor.instance("/fake_dir/bar"),
            self.hypervisor.instance("/fake_dir/baz"),
        ])
