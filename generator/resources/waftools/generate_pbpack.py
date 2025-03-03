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

from pbpack import ResourcePack
from io import BytesIO
# from resources.resource_map.my_resource_generator import definitions_from_dict, generate_object

# params:
#   platform: string in ['aplite', 'basalt', 'chalk', 'diorite', 'emery']
#   resource_data: tuple of (resource dict, resource generator type)
#   resource_source_path: resource directory
#   output_file: where to save the pbpack
# returns: ResourcePack, byte stream
def generate_pbpack(platform, resource_data):
    pack = ResourcePack(False)

    for rd, rt in resource_data:
        d = rt.definitions_from_dict(platform, rd)[0]
        resource = rt.generate_object(platform, d)
        pack.add_resource(resource.data)

    serialized_stream = BytesIO()
    pack.serialize(serialized_stream)

    return pack, serialized_stream