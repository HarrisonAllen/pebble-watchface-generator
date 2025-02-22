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

from resources.types.resource_object import ResourceObject
from resources.resource_map.resource_generator import ResourceGenerator

class ResourceGeneratorRaw(ResourceGenerator):
    type = 'raw'
    
    @staticmethod
    def definitions_from_dict(platform, definition_dict, resource_source_path):
        definitions = ResourceGenerator.definitions_from_dict(platform,
                                                              definition_dict,
                                                              resource_source_path)

        # Parse additional raw data specific fields
        for d in definitions:
            d.data = definition_dict.get('data')

        return definitions

    @staticmethod
    def generate_object(platform, definition):
        return ResourceObject(definition, definition.data.getvalue())
