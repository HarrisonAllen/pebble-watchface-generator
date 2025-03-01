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
from io import BytesIO, StringIO
from base64 import decodebytes
from string import Template
from resources.waftools.generate_pbpack import generate_pbpack
from resources.resource_map.resource_generator_png import PngResourceGenerator
from resources.resource_map.resource_generator_font import FontResourceGenerator
from resources.resource_map.resource_generator_raw import ResourceGeneratorRaw
from templates import *
from convert_config import convert_config, get_bw_or_color

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
RESOURCE_CRC_ADDR = (0x78, '<L') # 4 bytes
CRC_ADDR = (0x14, '<L')
STRUCT_SIZE_BYTES = 0x82

# JSON Data placeholders
FONT_SIZE = 52


def flen(path):
    statinfo = os.stat(path)
    return statinfo.st_size

def fstm32crc(path):
    with open(path, 'r+b') as f:
        binfile = f.read()
        return stm32_crc.crc32(binfile) & 0xFFFFFFFF
    
def blen(byte_stream):
    return byte_stream.getbuffer().nbytes

def stm32crc(byte_stream):
    binfile = byte_stream.getvalue()
    return stm32_crc.crc32(binfile) & 0xFFFFFFFF
    
def generate_manifest(binary, resources):
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
        'name' : APP_BINARY,
        'size': blen(binary),
        'crc': stm32crc(binary),
    }
        
    manifest['resources'] = {
        'name' : PBPACK_FILENAME,
        'timestamp' : timestamp,
        'size' : blen(resources),
        'crc' : stm32crc(resources),
    }

    manifest['type'] = 'application'

    manifest_stream = StringIO()
    json.dump(manifest, manifest_stream)
    return manifest_stream

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

def convert_base64_to_bytes(data):
    return BytesIO(decodebytes(bytes(data, "utf-8")))

def convert_name(name):
    return name.lower().replace(' ', '-')

def create_watchface(watchface_info_string, template_pbw_stream):
    # load the data
    watchface_info = json.loads(watchface_info_string)
    pbw_zip = zipfile.ZipFile(template_pbw_stream)

    # filename, relpath, data stream
    package_files = []

    # generate uuid try to use preexisting if exists
    data_uuid = watchface_info['metadata'].get('uuid')
    try:
        base_uuid = uuid.UUID(data_uuid)
    except:
        base_uuid = uuid.uuid1()
    uuid_str = generate_uuid_string(base_uuid, GENERATED_UUID_PREFIX_STR)
    uuid_bytes = generate_uuid_bytes(base_uuid, GENERATED_UUID_PREFIX_BYTES)
    print("UUID:", uuid_str)

    # setup names
    trunc_name = bytes(truncate_to_32_bytes(watchface_info['metadata']['name']), 'UTF8')
    trunc_comp = bytes(truncate_to_32_bytes(watchface_info['metadata']['author']), 'UTF8')

    # create app_info
    app_info_template = Template(APP_INFO_TEMPLATE)
    app_info_str = app_info_template.substitute(
        target_platforms=json.dumps(watchface_info['metadata']['target_platforms']),
        display_name=watchface_info['metadata']['name'],
        name=convert_name(watchface_info['metadata']['name']),
        author=watchface_info['metadata']['author'],
        version=watchface_info['metadata'].get('version', '1.0'),
        new_uuid=uuid_str
    )
    app_info_stream = StringIO(app_info_str)
    package_files.append((APP_INFO, "", app_info_stream))

    # create packages for each platform
    for platform in watchface_info['metadata']['target_platforms']:
        if not platform in ('aplite', 'basalt', 'chalk', 'diorite', 'emery'):
            raise ValueError(f"Unknown platform {platform}")
        
        # Set up resource data. These should reflect the appinfo/package.json
        # background png resource
        background_png_dict = BACKGROUND_PNG_DICT.copy()
        background_png_dict['data'] = convert_base64_to_bytes(get_bw_or_color(watchface_info["customization"]["background"], platform, "image_data")).getvalue()
        if platform in ('aplite', 'diorite') and "bw_image_data" in watchface_info["customization"]["background"]:
            background_png_dict['data'] = convert_base64_to_bytes(watchface_info["customization"]["background"]["bw_image_data"]).getvalue()
        else:
            background_png_dict['data'] = convert_base64_to_bytes(watchface_info["customization"]["background"]["image_data"]).getvalue()
        background_png_dict['targetPlatforms'] = platform

        # Time font resource
        time_font_dict = TIME_FONT_DICT.copy()
        time_font_dict['name'] = f'FONT_TIME_{watchface_info["customization"]["clocks"]["digital"]["font_size"]}'
        time_font_dict['data'] = convert_base64_to_bytes(watchface_info["customization"]["clocks"]["digital"]["font_data"])
        time_font_dict['targetPlatforms'] = platform

        # Date font resource
        date_font_dict = DATE_FONT_DICT.copy()
        date_font_dict['name'] = f'FONT_DATE_{watchface_info["customization"]["date"]["font_size"]}'
        date_font_dict['data'] = convert_base64_to_bytes(watchface_info["customization"]["date"]["font_data"])
        date_font_dict['targetPlatforms'] = platform

        # Text font resource
        text_font_dict = TEXT_FONT_DICT.copy()
        text_font_dict['name'] = f'FONT_TEXT_{watchface_info["customization"]["text"]["font_size"]}'
        text_font_dict['data'] = convert_base64_to_bytes(watchface_info["customization"]["text"]["font_data"])
        text_font_dict['targetPlatforms'] = platform

        # Raw Data resource
        data_dict = DATA_DICT.copy()
        data_dict['data'] = convert_config(watchface_info['customization'], platform)
        data_dict['targetPlatforms'] = platform

        resource_data = [ # like so: (resource info dict, resource generator type)
            (background_png_dict, PngResourceGenerator),
            (time_font_dict, FontResourceGenerator),
            (date_font_dict, FontResourceGenerator),
            (text_font_dict, FontResourceGenerator),
            (data_dict, ResourceGeneratorRaw)
        ]
        
        # Generate resource pack, write to pbpack_path
        resource_pack, pbpack_stream = generate_pbpack(platform, resource_data)
        package_files.append((PBPACK_FILENAME, f"{platform}/", pbpack_stream))

        # Copy and update binary
        with pbw_zip.open(os.path.join(f"{platform}/", APP_BINARY)) as f:
            binary_stream = BytesIO(f.read())
        write_value_at_offset(binary_stream, NAME_ADDR[0], NAME_ADDR[1], trunc_name)
        write_value_at_offset(binary_stream, COMPANY_ADDR[0], COMPANY_ADDR[1], trunc_comp)
        write_value_at_offset(binary_stream, UUID_ADDR[0], UUID_ADDR[1], uuid_bytes)
        write_value_at_offset(binary_stream, RESOURCE_CRC_ADDR[0], RESOURCE_CRC_ADDR[1], resource_pack.crc)
        package_files.append((APP_BINARY, f"{platform}/", binary_stream))

        # Generate manifest, write to manifest_path
        manifest_stream = generate_manifest(binary_stream, pbpack_stream)
        package_files.append((MANIFEST_FILENAME, f"{platform}/", manifest_stream))

    pbw_zip.close()

    # And wrap it all into a pbw
    pbw_name = convert_name(watchface_info['metadata']['name']) + '.pbw'
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for filename, rel_path, data_stream in package_files:
            file_path = os.path.join(rel_path, filename)
            zip_file.writestr(file_path, data_stream.getvalue())
        zip_file.comment = bytes(pbw_name, "UTF-8")

    return zip_buffer.getvalue(), pbw_name

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='generate pbpack and manifest')

    parser.add_argument('template_pbw_path', help='path to template pbw')
    parser.add_argument('info_path', help='path to watchface_info.json')
    parser.add_argument('output_dir', help='path to output directory')

    args = parser.parse_args()

    # load watchface info from file
    with open(args.info_path, 'r') as f:
        watchface_info_string = f.read()

    # load template pbw from file
    with open(args.template_pbw_path, "rb") as f:
        template_pbw_stream = BytesIO(f.read())
    
    # set up output directory
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    pbw, pbw_name = create_watchface(watchface_info_string, template_pbw_stream)
    
    with open(os.path.join(args.output_dir, pbw_name), 'wb') as f:
        f.write(pbw)