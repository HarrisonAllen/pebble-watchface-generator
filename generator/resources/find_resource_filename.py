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

from pebble_sdk_platform import pebble_platforms, maybe_import_internal

import os
import os.path
import sys
from glob import glob

__author__ = 'katharine'

def find_most_specific_filename(platform, resource_source_path, general_filename):
    if '~' in general_filename:
        raise Exception("Generic resource filenames cannot contain a tilde (~).")

    basename, extension = os.path.splitext(general_filename)

    # The filenames we get will have extra bits of folder at the start, so trim those.
    root_len = len(os.path.relpath(resource_source_path)) + 1
    if os.path.relpath(resource_source_path) == '.':
        root_len = 2

    glob_result = glob("{}*{}".format(os.path.join(os.path.relpath(resource_source_path), basename),  extension))
    options = [x[root_len:] for x in glob_result if os.path.isfile(x)]

    specificities = {}
    try:
        valid_tags = set(pebble_platforms[platform]['TAGS'])
    except KeyError:
        raise Exception("Unrecognized platform %s. Did you mean to configure with --internal_sdk_build?" %
                  platform)

    for option in options:
        # We can get names that don't match if the name we have is a prefix of other files. Drop those.
        if option.split('~', 1)[0] != basename:
            continue
        tags = set(os.path.splitext(option)[0].split('~')[1:])
        # If there exist tags that aren't valid, we skip this.
        if len(tags - valid_tags) > 0:
            continue
        # If it's valid, the specificity is the number of tags that exist in both sets.
        specificities[option] = len(valid_tags & tags)

    if len(specificities) == 0:
        return general_filename

    top_score = max(specificities.values())
    top_candidates = [k for k, v in specificities.items() if v == top_score]
    if len(top_candidates) > 1:
        raise Exception("The correct file for {general} on {platform} is ambiguous: {count} files have "
                  "specificity {score}:\n\t{files}".format(general=general_filename,
                  count=len(top_candidates), score=top_score, platform=platform,
                  files="\n\t".join(top_candidates)))

    return top_candidates[0]
