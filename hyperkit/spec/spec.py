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

from auth import PasswordAuth
from image import CanonicalImage
from hardware import Hardware


class MachineSpec(object):
    def __init__(self, name="myvm",
                 auth=None, image=None, hardware=None, options=None):
        if auth is None:
            auth = PasswordAuth()
        if image is None:
            image = CanonicalImage()
        if hardware is None:
            hardware = Hardware()
        self.name = name
        self.auth = auth
        self.image = image
        self.hardware = hardware
        self.options = options
