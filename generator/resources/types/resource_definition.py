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

import os

from resources.types.resource_declaration import ResourceDeclaration


class StorageType(object):
    pbpack = 1
    builtin = 2
    pfs = 3


class ResourceDefinition(ResourceDeclaration):
    def __init__(self, type, name, data, storage=StorageType.pbpack,
                 target_platforms=None, aliases=()):
        self.type = type
        self.name = name

        self.data = data

        self.storage = storage

        # A list of platforms this resource is valid for. None means all platforms. [] means none.
        self.target_platforms = target_platforms
        self.aliases = list(aliases)

    def is_in_target_platform(self, bld):
        if self.target_platforms is None:
            return True

        return bld.env.PLATFORM_NAME in self.target_platforms

    def find_specific_filename(self, task_gen):
        return find_most_specific_filename(task_gen.bld, task_gen.env, task_gen.bld.path, self.file)

    def __repr__(self):
        return '<ResourceDefinition %r>' % self.__dict__
