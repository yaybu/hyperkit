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


class Hardware(object):
    def __init__(self, memory=1024, cpus=1):
        self.memory = memory
        self.cpus = cpus

    @property
    def cpu_plural(self):
        if self.cpus != 1:
            return "s"
        return ""

    def __str__(self):
        return "%s CPU%s %s RAM" % (self.cpus, self.cpu_plural, self.memory)

__all__ = [Hardware]
