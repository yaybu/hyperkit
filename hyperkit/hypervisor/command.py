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

logger = logging.getLogger(__name__)


class CommandException(Exception):
    pass


class Command(object):

    known_locations = ()
    command_name = None
    subcommands = {}
    log_execution = False
    log_stdout = False
    log_stderr = False

    @property
    def pathname(self):
        candidates = itertools.chain(self.known_locations, os.environ['PATH'].split(":"))
        for loc in candidates:
            pathname = os.path.join(loc, self.command_name)
            if os.path.isfile(pathname) and os.access(pathname, os.X_OK):
                return pathname
        raise OSError("Cannot find command %r" % self.command_name)

    def compose(self, subcommand, *args, **kwargs):
        cmd_args = [self.pathname]
        for a in self.subcommands[subcommand]:
            cmd_args.append(a.format(**kwargs))
        cmd_args.extend(args)
        return cmd_args

    def parse(self, stdout, stderr):
        return stdout.strip()

    def execute(self, command, cwd):
        p = subprocess.Popen(args=command,
                             stdin=None,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             cwd=cwd)
        if self.log_execution:
            logger.debug("Executing: {0}".format(" ".join(command)))
        stdout, stderr = p.communicate()
        if (self.log_stdout and stdout) or (self.log_stderr and stderr):
            logger.debug("Output from {0}".format(" ".join(command)))
        if self.log_stdout and stdout:
            for line in stdout.splitlines():
                logger.debug("STDOUT: {0}".format(line))
        if self.log_stderr and stderr:
            for line in stderr.splitlines():
                logger.debug("STDERR: {0}".format(line))
        if p.returncode != 0:
            raise CommandException("Command execution of {0} failed with error code {1} and error output: {2}".format(" ".join(command), p.returncode, stderr))
        return self.parse(stdout, stderr)

    def __call__(self, subcommand, *args, **kwargs):
        cwd = kwargs.pop("cwd", None)
        command = self.compose(subcommand, *args, **kwargs)
        return self.execute(command, cwd=cwd)
