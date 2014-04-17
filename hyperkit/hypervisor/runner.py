# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import logging
import itertools
import subprocess

logger = logging.getLogger("util")


class RunnerException(Exception):
    pass


class Runner(object):

    """ Encapsulates running a subcommand using subprocess. When you create
    an instance of this class the command_name command is located and the path is stored. By
    default an exception will be raised when the class is instantiated if the
    named command cannot be found.

    If the command might be found somewhere other than on PATH, you can
    provide these in known_locations

    """

    def __init__(self, command_name, args=(), known_locations=(), bail_if_absent=False,
                 log_execution=False, log_stdout=False, log_stderr=False):
        self.command_name = command_name
        self.args = args
        self.known_locations = known_locations
        self.bail_if_absent = bail_if_absent
        self.log_execution = log_execution
        self.log_stdout = log_stdout
        self.log_stderr = log_stderr
        self.pathname = self.locate_command()
        if self.pathname is None and self.bail_if_absent:
            raise RunnerException("Cannot find {0}".format(self.command_name))

    def compose(self, *args, **kwargs):
        cmd_args = [self.pathname]
        for a in self.args:
            cmd_args.append(a.format(**kwargs))
        cmd_args.extend(args)
        return cmd_args

    def parse(self, stdout, stderr):
        return stdout.strip()

    def locate_command(self):
        for loc in itertools.chain(self.known_locations, os.environ['PATH'].split(":")):
            pathname = os.path.join(loc, self.command_name)
            if os.path.isfile(pathname) and os.access(pathname, os.X_OK):
                return pathname

    def __call__(self, *args, **kwargs):
        cwd = kwargs.pop("cwd", None)
        command = self.compose(*args, **kwargs)
        return self.execute(command, cwd=cwd)

    def execute(self, command, cwd):
        p = subprocess.Popen(args=command,
                             stdin=None,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             cwd=cwd)
        if self.log_execution:
            logging.debug("Executing: {0}".format(" ".join(command)))
        stdout, stderr = p.communicate()
        if (self.log_stdout and stdout) or (self.log_stderr and stderr):
            logging.debug("Output from {0}".format(" ".join(command)))
        if self.log_stdout and stdout:
            for line in stdout.splitlines():
                logging.debug("STDOUT: {0}".format(line))
        if self.log_stderr and stderr:
            for line in stderr.splitlines():
                logging.debug("STDERR: {0}".format(line))
        if p.returncode != 0:
            raise RunnerException("Command execution of {0} failed with error code {1} and error output: {2}".format(" ".join(command), p.returncode, stderr))
        return self.parse(stdout, stderr)
