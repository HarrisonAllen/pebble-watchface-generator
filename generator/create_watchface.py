import argparse
import time
import os
import stm32_crc
import json
import shutil
import struct
import sys
import uuid
import zipfile
from string import Template
from resources.waftools.generate_pbpack import generate_pbpack
from resources.resource_map.resource_generator_png import PngResourceGenerator
from resources.resource_map.resource_generator_font import FontResourceGenerator
from resources.resource_map.resource_generator_raw import ResourceGeneratorRaw
from templates import *

PBPACK_FILENAME = "app_resources.pbpack"
GENERATOR_NAME = "WatchfaceGenerator"
MANIFEST_FILENAME = "manifest.json"
WATCHFACE_INFO = "watchface_info.json"
APP_INFO = "appinfo.json"
APP_BINARY = "pebble-app.bin"
MANIFEST_VERSION = 2
GENERATED_UUID_PREFIX_BYTES = b'\x13\x37\x13\x37'
GENERATED_UUID_PREFIX_STR = "13371337"

# metadata: (addr, format)
NAME_ADDR = (0x18, '32s') # truncated to 32 length byte string
COMPANY_ADDR = (0x38, '32s') # truncated to 32 length byte string
UUID_ADDR = (0x68, '16s') # 16 bytes, serialize with uuid.bytes
RESOURCE_CRC_ADDR = (0x78, 'I') # 4 bytes

# JSON Data placeholders
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

def generate_uuid_string(base_uuid, prefix):
    uuid_str = str(base_uuid)
    return prefix + uuid_str[len(prefix):]

def generate_uuid_bytes(base_uuid, prefix):
    uuid_bytes = base_uuid.bytes
    return prefix + uuid_bytes[len(prefix):]

def truncate_to_32_bytes(name):
    return name[:30] + '..' if len(name) > 32 else name

def write_value_at_offset(opened_file, offset, format_str, value):
    opened_file.seek(offset)
    opened_file.write(struct.pack(format_str, value))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='generate pbpack and manifest')

    parser.add_argument('template_dir', help='path to template application')
    parser.add_argument('resource_dir', help='path to resources')
    parser.add_argument('output_dir', help='path to output')

    args = parser.parse_args()

    package_files = {}

    # load watchface info from designer
    watchface_info_file = os.path.join(args.resource_dir, WATCHFACE_INFO)
    with open(watchface_info_file, 'r') as f:
        watchface_info = json.load(f)

    # clear our output directory
    if os.path.exists(args.output_dir):
        raise Exception(f'Output directory "{args.output_dir}" already exists! Aborting...')
    os.makedirs(args.output_dir)

    # generate uuid try to use preexisting if exists
    data_uuid = watchface_info['metadata'].get('uuid')
    try:
        base_uuid = uuid.UUID(data_uuid)
    except:
        base_uuid = uuid.uuid1()
    uuid_str = generate_uuid_string(base_uuid, GENERATED_UUID_PREFIX_STR)
    uuid_bytes = generate_uuid_bytes(base_uuid, GENERATED_UUID_PREFIX_BYTES)

    # setup names
    trunc_name = bytes(truncate_to_32_bytes(watchface_info['metadata']['display_name']), 'UTF8')
    trunc_comp = bytes(truncate_to_32_bytes(watchface_info['metadata']['company_name']), 'UTF8')

    # create app_info
    app_info_file = os.path.join(args.output_dir, APP_INFO)
    app_info_template = Template(APP_INFO_TEMPLATE)
    app_info_str = app_info_template.substitute(
        target_platforms=json.dumps(watchface_info['metadata']['target_platforms']),
        display_name=watchface_info['metadata']['display_name'],
        name=watchface_info['metadata']['name'],
        company_name=watchface_info['metadata']['company_name'],
        new_uuid=uuid_str
    )
    with open(app_info_file, "w") as f:
        f.write(app_info_str)
    package_files[APP_INFO] = app_info_file

    # create packages for each platform
    for platform in watchface_info['metadata']['target_platforms']:
        if not platform in ('aplite', 'basalt', 'chalk', 'diorite', 'emery'):
            raise Exception(f"Unknown platform {platform}")
        
        platform_template_dir = os.path.join(args.template_dir, platform)
        platform_output_dir = os.path.join(args.output_dir, platform)
        os.makedirs(platform_output_dir)
        
        # Set up resource data. These should reflect the appinfo/package.json
        background_png_dict = BACKGROUND_PNG_DICT.copy()
        background_png_dict['targetPlatforms'] = platform

        time_font_dict = TIME_FONT_DICT.copy()
        time_font_dict['name'] = f'FONT_TIME_{watchface_info["customization"]["time"]["font_size"]}'
        time_font_dict['targetPlatforms'] = platform

        data_dict = DATA_DICT.copy()
        data_dict['targetPlatforms'] = platform

        resource_data = [ # like so: (resource info dict, resource generator type)
            (background_png_dict, PngResourceGenerator),
            # (time_font_dict, FontResourceGenerator)
            # (data_dict, ResourceGeneratorRaw)
        ]
        
        # Generate resource pack, write to pbpack_path
        pbpack_path = os.path.join(platform_output_dir, PBPACK_FILENAME)
        resource_pack = generate_pbpack(platform, resource_data, args.resource_dir, pbpack_path)
        package_files[PBPACK_FILENAME] = pbpack_path

        # Copy and update binary
        binary_source_path = os.path.join(platform_template_dir, APP_BINARY)
        binary_copy_path = os.path.join(platform_output_dir, APP_BINARY)
        shutil.copy(binary_source_path, binary_copy_path)
        with open(binary_copy_path, "r+b") as f:
            write_value_at_offset(f, NAME_ADDR[0], NAME_ADDR[1], trunc_name)
            write_value_at_offset(f, COMPANY_ADDR[0], COMPANY_ADDR[1], trunc_comp)
            write_value_at_offset(f, UUID_ADDR[0], UUID_ADDR[1], uuid_bytes)
            write_value_at_offset(f, RESOURCE_CRC_ADDR[0], RESOURCE_CRC_ADDR[1], resource_pack.crc)
        package_files[APP_BINARY] = binary_copy_path

        # Generate manifest, write to manifest_path
        manifest_path = os.path.join(platform_output_dir, MANIFEST_FILENAME)
        generate_manifest(binary_copy_path, pbpack_path, manifest_path)
        package_files[MANIFEST_FILENAME] = manifest_path

    # And wrap it all into a pbw
    pbw_name = watchface_info['metadata']['name'] + '.pbw'
    pbw_path = os.path.join(args.output_dir, pbw_name)
    with zipfile.ZipFile(pbw_path, 'w') as zip_file:
        for filename, file_path in package_files.items():
            rel_path = os.path.relpath(
                file_path, args.output_dir
            )
            zip_file.write(file_path, rel_path)
        zip_file.comment = bytes(pbw_name, "UTF-8")