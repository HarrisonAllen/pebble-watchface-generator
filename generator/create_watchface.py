import argparse
from resources.waftools.generate_pbpack import generate_pbpack
from resources.resource_map.resource_generator_png import PngResourceGenerator
from resources.resource_map.resource_generator_font import FontResourceGenerator
from resources.resource_map.resource_generator_raw import ResourceGeneratorRaw
import time
import os
import stm32_crc
import json
import shutil
import struct
import sys

PBPACK_FILENAME = "app_resources.pbpack"
GENERATOR_NAME = "WatchfaceGenerator"
MANIFEST_FILENAME = "manifest.json"
MANIFEST_VERSION = 2
RESOURCE_CHECKSUM_OFFSET = 0x78
FONT_SIZE = 52

def flen(path):
    statinfo = os.stat(path)
    return statinfo.st_size

def stm32crc(path):
    with open(path, 'r+b') as f:
        binfile = f.read()
        return stm32_crc.crc32(binfile) & 0xFFFFFFFF
    
def generate_manifest(watchapp_path, resources_path, out_path):
    timestamp = int(time.time())
    
    manifest = {
        'manifestVersion' : MANIFEST_VERSION,
        'generatedAt' : timestamp,
        'generatedBy' : GENERATOR_NAME,
        'debug' : {},
    }
    manifest['application'] = {
        'timestamp': timestamp,
        'sdk_version': {
            "major": 5,
            "minor": 86
        },
        'name' : os.path.basename(watchapp_path),
        'size': flen(watchapp_path),
        'crc': stm32crc(watchapp_path),
    }
        
    manifest['resources'] = {
        'name' : os.path.basename(resources_path),
        'timestamp' : timestamp,
        'size' : flen(resources_path),
        'crc' : stm32crc(resources_path),
    }

    with open(out_path, "w") as f: 
        json.dump(manifest, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='generate pbpack and manifest')

    parser.add_argument('platform', help='platform to generate for')
    parser.add_argument('resource_path', help='path to resources')
    parser.add_argument('app_path', help='path to original application binary')
    parser.add_argument('output_dir', help='path to save pbpack and manifest')

    args = parser.parse_args()

    if not args.platform in ('aplite', 'basalt', 'chalk', 'diorite', 'emery'):
        raise Exception(f"Unknown platform {args.platform}")
    
    # Set up resource data. These should reflect the appinfo/package.json
    background_png_dict = {
        'name': 'IMAGE_BACKGROUND',
        'type': 'png',
        'file': 'background.png',
        'targetPlatforms': [args.platform]
    }
    time_font_dict = {
        'name': f'FONT_TIME_{FONT_SIZE}',
        'type': 'font',
        'file': 'font.ttf',
        'characterRegex': '[0-9:]',
        'targetPlatforms': [args.platform]
    }
    data_dict = {
        'name': 'DATA',
        'type': 'raw',
        'file': 'data.bin',
        'targetPlatforms': [args.platform]
    }
    resource_data = [ # like so: (resource info dict, resource generator type)
        (background_png_dict, PngResourceGenerator),
        # (time_font_dict, FontResourceGenerator)
        # (data_dict, ResourceGeneratorRaw)
    ]
    
    # Generate resource pack, write to pbpack_path
    pbpack_path = os.path.join(args.output_dir, PBPACK_FILENAME)
    resource_pack = generate_pbpack(args.platform, resource_data, args.resource_path, pbpack_path)

    # Copy and update binary with resource pack checksum
    binary_filename = os.path.basename(args.app_path)
    binary_copy_path = os.path.join(args.output_dir, binary_filename)
    shutil.copy(args.app_path, binary_copy_path)
    res_crc = struct.pack('<I',  resource_pack.crc)
    with open(binary_copy_path, "r+b") as f:
        f.seek(RESOURCE_CHECKSUM_OFFSET)
        f.write(res_crc)

    # Generate manifest, write to manifest_path
    manifest_path = os.path.join(args.output_dir, MANIFEST_FILENAME)
    generate_manifest(binary_copy_path, pbpack_path, manifest_path)
