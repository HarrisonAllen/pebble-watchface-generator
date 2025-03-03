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

from resources.find_resource_filename import find_most_specific_filename
from resources.types.resource_definition import ResourceDefinition, StorageType

# This is all the classes that have been registered by inheriting from the ResourceGenerator
# metaclass with a 'type' attribute set.
_ResourceGenerators = {}


class ResourceGeneratorMetaclass(type):
    type = None

    def __init__(cls, name, bases, dict):
        super(ResourceGeneratorMetaclass, cls).__init__(name, bases, dict)

        if cls.type:
            _ResourceGenerators[cls.type] = cls

# Instatiate the metaclass into a baseclass we can use elsewhere.
ResourceGeneratorBase = ResourceGeneratorMetaclass('ResourceGenerator', (object,), {})


# Take in platform (str, "aplite" etc.), definition_dict (dict of definitions), data as bytes
class ResourceGenerator(ResourceGeneratorBase):
    @staticmethod
    def definitions_from_dict(platform, definition_dict):
        """
        Default implementation of definitions_from_dict. Subclasses of ResourceGenerator can
        override this implementation if they'd like to customize this. Returns a list of definitions.
        """
        resource = {'name': definition_dict['name'],
                    'data': definition_dict['data']}
        resources = [resource]

        # Now generate ResourceDefintion objects for each resource
        target_platforms = definition_dict.get('targetPlatforms', None)
        aliases = definition_dict.get('aliases', [])

        definitions = []
        for r in resources:
            storage = StorageType.pbpack

            d = ResourceDefinition(definition_dict['type'], r['name'],
                                   r['data'], storage=storage,
                                   target_platforms=target_platforms,
                                   aliases=aliases)

            if 'size' in r:
                d.size = r['size']

            definitions.append(d)


        return definitions

    @classmethod
    def generate_object(cls, platform, definition):
        """
        Stub implementation of generate_object. Subclasses must override this method.
        """
        raise NotImplemented('%r missing a generate_object implementation' % cls)
