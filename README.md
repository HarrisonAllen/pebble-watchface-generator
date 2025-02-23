# Pebble Watchface Generator

This is a project for creating a watchface generator for pebble

#### Table of Contents
* [The design](#the-design)
    * [The watchface](#the-watchface)
    * [The web designer](#the-web-designer)
    * [The generator](#the-generator)
* [Current state of affairs](#current-state-of-affairs)
    * [Generated samples](#generated-samples)
    * [Using the generator (as a human)](#using-the-generator-as-a-human)
    * [Using the generator (as a non-human)](#using-the-generator-as-a-non-human)
* [TODOs](#todos)
    * [Generator](#generator)
    * [Watchface](#watchface)
* [Random learnings](#random-learnings)
    * [Resource pack structure](#resource-pack-structure)
    * [App binary](#app-binary)


## The design

### The watchface

The goal is for this watchface to be changed without having to recompile. This can be done by modifying the resource packs and app binary.

The templated watchface should be able to handle whatever customization assets are contained within the web interface. That means we need placeholder assets and resource definitions in package.json for:
* Background image
* Digital time font
* Date font
* Misc. text font
* etc.

Beyond that, we will need to keep track of other data. This data gets stored into a binary file, and read by the watchface when it loads. For example:
* Background color (rgb byte)
* Image x pos (int16?)
* Image y pos (int16?)
* Digital time font size (uint8)
* Digital time color (rgb byte)
* Digital time x pos (int16?)
* Digital time y pos (in16?)
* Date visible (bool)
* etc.

The watchface needs to be compiled into a .pbw for modification

### The web designer

This is more WillO's wheelhouse, but it's a web interface for designing the watchface. Spits out a json blob with info.

What I want out of this blob:
* .png for the background in base64
    * or multiple pngs if the designer creates one for each platform, e.g. doing automatic grayscale dithering
* .ttf for each of the fonts in base64
* Parameters for alllll of the customization
* New appinfo:
    * targetPlatforms
    * name
    * author 
    * uuid (optional, omit to autogenerate for updating existing watchfaces, starts with `13371337`)

### The generator

This generator acts as a bridge between the web designer and the end-result watchface. Right now it's written in Python, but would be super slick to convert to JS to keep everything client side.

The generator will modify a .pbw. Really, it will take the base components, use them to generate the appropriate assets, and rezip them up. A .pbw file contains:
* appinfo.json (metadata about the app)
* platform directories (e.g. `basalt/`)
    * app_resources.pbpack (all of the apps resources)
    * manifest.json (metadata about the app binary and the resources)
    * pebble-app.bin (the app binary)

Most of the code is derived from [pebble-firmware](https://github.com/pebble-dev/pebble-firmware/tree/main)

#### The generation process

Prerequisites:
* a json blob of all of the required information
* the template pbw

The core generation logic:
1. Copy and update `appinfo.json` with the new watchface information
2. Then for each platform in `targetPlatforms` (`aplite`, `basalt`, ...):
    1. Create a `<platform>` directory
    2. Generate a new `app_resources.pbpack`
    3. Generate a new `manifest.json`
    4. Copy and update `pebble-app.bin` with metadata
5. Zip it up into a pretty .pbw and give it to the user/appstore

## Current state of affairs

As it stands, I have successfully set up `create_watchface.py` to generate a new watchface:
* Takes in a string of the watch info json
    * Includes background image (base64), fonts (base64), and all of the watch data
    * When running the script manually it accepts a json filename
* Takes in a bytestream of a template .pbw
* Generates a pbpack containing all of the resources and data
* Generates all files for functioning watchface (app info, then for each platform: pbpack, manifest, app binary)
* Zips them all up into a pbw

The watchface is set up to work with whatever image and font are thrown at it, and actively works with the following:
* Background information (image, color, x, y, width, height)
* Digital clock information (font size, color, x, y)

### Generated samples

I've set up a few samples in `samples/` that are ready to run, and can be used for testing the generator.
* `resources` contains an extracted template watchface, and resources for the sample watchfaces
* `pbws` contains generated pbws based on the sample `watchface_info.json`s

### Using the generator (as a human)

Prereqs:
* set up a python3 environment (i'm using 3.8, don't know how much it matters)
* use pip to install requirements.txt
* cd to `generator`

Run it
1. Create a modified version of `watchface_info.json`
    * The `image_data` and `font_data` should be encoded with base64
    * optional: add `uuid` to `metadata` to force a specific uuid
2. Run ```python3 create_watchface.py <template_dir> <info_path> <output_dir>```
    * `<template_pbw_path>` is the path to the template pbw
    * `<info_path>` is the path to `watchface_info.json`
    * `<output_dir>` is the output directory for the final .pbw
2. The .pbw will be written to `output_dir/<watchface name>.pbw`

For example:
```
python3 create_watchface.py \
    ../samples/resources/template-watchface.pbw/ \
    ../samples/resources/hollow-knight/watchface_info.json \
    ../samples/pbws/
```

### Using the generator (as a non-human)

Prereqs:
* set up a python3 environment (i'm using 3.8, don't know how much it matters)
* use pip to install requirements.txt

Run it
1. Generate a json string containing watchface info
2. Generate a bytestream (io.BytesIO specifically) containing the template pbw
2. Use the function `create_watchface` with the following parameters:
    * `watchface_info_string` - The string version of the json output
    * `template_pbw_stream` - The bytestream version of the template pbw
    * This generates a pbw object as bytes
3. Either write the pbw object to disk or send it elsewhere (e.g. back to the user)

## TODOs

### Generator

- [x] Understand resource packs
- [x] Generate resource pack without SDK
- [x] Generate manifest
- [x] Patch binary to work with new resource pack
- [x] Get PNGs working
- [x] Get fonts working
- [x] Get raw data working
- [x] Run against multiple platforms
- [x] Read in information from json
- [x] Update appinfo.json
    - [x] Figure out how appinfo is baked into binary and update there, too
- [x] Generate full .pbw
    - [x] ... without writing to disk
- [x] Generate by loading in a template pbw rather than an extracted one
- [x] Read png, fonts from base64 instead of file
- [ ] Add error handling and proper messages for failures (will need to check with frontend on how to implement):
    - [ ] Font too large (`Glyph too large!`)
        * Resolution: reduce font size, use different font
    - [ ] Image processing failure
    - [ ] Invalid values
- [ ] Match with final template watchface, web designer
- [ ] And more...

### Watchface

- [x] Create basic watchface with only background png
- [x] Add time and corresponding font
- [x] Add raw data and update bg color, font color
- [ ] Add digital toggle
- [ ] Add date
- [ ] Add text
- [ ] add analog
- [ ] Add all placeholder resources
- [ ] Add template logic for all watch cases
- [ ] And more...

## Random learnings

Not sure where to put this, but too important to lose track of.

### Resource pack structure

Manifest (first 12 bytes, little endian):
* Number of table entries (i.e. # of resources)
* crc of entire resource pack
* timestamp (always zero, unused)

Table entries (16 bytes each, max 256 entries, unused table entries zeroed out):
* Resource index 
    * Starts from 1 (not zero)
    * Same order as in `package.json`
* Offset of resource data in bytes 
    * Relative to start of resources, 0x100C
    * E.g. 1st resource has offset of 0x0000
* Length of resource data in bytes
* crc of resource data

Resources come after these, starting at 0x100C (that offset is manifest (0x000C) + table (0x1000)). Each resource is serialized in a certain way, which is why I'm reusing some of the existing serializing scripts

### App binary

There's metadata baked into the binary. The important ones for us are:
* name @ `0x18`, format `<32s` (display name truncated to 32 length byte string)
* company @ `0x38` format `<32s` (company name truncated to 32 length byte string)
* uuid @ `0x68` format `<16s` (we'll want to create a new uuid and replace bytes 0:4 with "13371337")
* resources crc @ `0x78` format `<I` (generated from resource pack)
