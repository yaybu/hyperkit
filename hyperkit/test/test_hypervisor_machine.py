
import unittest2
import mock

from hyperkit.hypervisor import machine

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


