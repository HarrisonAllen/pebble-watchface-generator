# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pickle

class ResourceObject(object):
    """
    Defines a single resource object in a namespace. Must be serializable.
    """

    def __init__(self, definition, data):
        self.definition = definition

        if isinstance(data, list):
            self.data = b"".join(data)
        else:
            self.data = data

    def dump(self, output_node):
        output_node.parent.mkdir()
        with open(output_node.abspath(), 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, path):
        with open(path, 'rb') as f:
            return pickle.load(f)
