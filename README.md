# Pebble Watchface Generator

This is a project for creating a watchface generator for pebble

#### Table of Contents
* [The design](#the-design)
    * [The watchface](#the-watchface)
    * [The web designer](#the-web-designer)
    * [The generator](#the-generator)
* [Current state of affairs](#current-state-of-affairs)
    * [Generated samples](#generated-samples)
    * [Using the generator](#using-the-generator)
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
* .png for the background
    * or multiple pngs if the designer creates one for each platform, e.g. doing automatic grayscale dithering
* .ttf for each of the fonts
* Data for alllll of the customization (could be converted into binary file on web or in generator, tbd)
* New appinfo:
    * targetPlatforms
    * displayName
    * name
    * companyName 
    * longName (just display name?)
    * shortName (just display name?)
    * uuid (needs to start with `13371337`!)

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
* a directory with the new assets
* a json blob of all of the required information
* the template pbw (extracted?)

Generating (done by a script obviously, `create_watchface.py`?):
1. Copy and update `appinfo.json` with the new watchface information
2. Then for each platform in `targetPlatforms` (`aplite`, `basalt`, ...):
    1. Create a `<platform>` directory
    2. Generate a new `app_resources.pbpack`
    3. Generate a new `manifest.json`
    4. Copy and update `pebble-app.bin` with the resource checksum
5. Zip it up into a pretty .pbw and give it to the user/appstore

## Current state of affairs

As it stands, I have successfully set up `create_watchface.py` to generate a watchface using a new `background.png`. It creates `app_resources.pbpack`, `manifest.json`, and `pebble-app.bin` for a given platform. These files will need to be manually organized and zipped up into a .pbw. `appinfo.json` will need to be manually moved over as well.

### Generated samples

I've set up a few samples in `generated-samples/` that are ready to run, and can be used for testing the generator.
* `resources` contains an extracted template watchface, and resources for the two generated watchfaces
* `*-stripes-watchface` are generated watchfaces, and I've manually copied over `appinfo.json` and manually packaged them into .pbws

### Using the generator

Prereqs:
* Use WSL (or linux idk I haven't tested anything else)
* set up a python3 environment (i'm using 3.8, don't know how much it matters)
* use pip to install requirements.txt
* cd to `generator`

Run it
1. Run ```python3 create_watchface.py <platform> <resource_path> <app_path> <output_dir>```
    * `<platform>` is the platform to build for, e.g. `basalt`
    * `<resource_path>` is the directory containing the new app resources
    * `<app_path>` is the path of the template app binary
    * `<output_dir>` is where to save the generated files
3. Copy over `appinfo.json`, and maybe update it too
2. Arrange the directory to match a .pbw structure
3. Zip it all together

## TODOs

### Generator

- [x] Understand resource packs
- [x] Generate resource pack without SDK
- [x] Generate manifest
- [x] Patch binary to work with new resource pack
- [x] Get PNGs working
- [ ] Get fonts working
- [ ] Get raw data working
- [ ] Run against multiple platforms
- [ ] Read in information from json
- [ ] Update appinfo
    - [ ] Figure out how appinfo is baked into binary
- [ ] Generate full .pbw
- [ ] ... without writing to disk
- [ ] Match with final template watchface, web designer
- [ ] And more...

### Watchface

- [x] Create basic watchface with only background png
- [ ] Add time and corresponding font
- [ ] Add raw data and update bg color, font color
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

The crc of the resources is baked into the app binary. If it differs, the watch will reject the application: `Checksum for resources differs...` Through some analysis I found the crc is stored at `0x78` in the binary. The generator overwrites the old value with the crc of the new resource pack.