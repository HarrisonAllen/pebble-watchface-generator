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

from pebble_sdk_platform import pebble_platforms

import png2pblpng

class PngResourceGenerator(ResourceGenerator):
    type = 'png'

    @staticmethod
    def generate_object(platform, definition):
        is_color = 'color' in pebble_platforms[platform]['TAGS']
        palette_name = png2pblpng.get_ideal_palette(is_color=is_color)
        image_bytes = png2pblpng.convert_png_to_pebble_png_bytes(definition.data,
                                                                 palette_name)
        return ResourceObject(definition, image_bytes)
