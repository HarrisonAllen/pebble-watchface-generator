from io import BytesIO
from pebble_image_routines import nearest_color_to_pebble64_palette, rgba32_triplet_to_argb8

BW_PREFIX = "bw_"
MAX_STRING_SIZE = 31

DATE_FORMAT_CONVERSIONS = {
    "dd": "%d",
    "mm": "%m",
    "yy": "%y",
    "YYYY": "%Y",
    "mon": "%b",
    "dow": "%a",
}

SYSTEM_FONTS = (
    "FONT_FALLBACK_INTERNAL",
    "GOTHIC_18_BOLD",
    "GOTHIC_24",
    "GOTHIC_09",
    "GOTHIC_14",
    "GOTHIC_14_BOLD",
    "GOTHIC_18",
    "GOTHIC_24_BOLD",
    "GOTHIC_28",
    "GOTHIC_28_BOLD",
    "BITHAM_30_BLACK",
    "BITHAM_42_BOLD",
    "BITHAM_42_LIGHT",
    "BITHAM_42_MEDIUM_NUMBERS",
    "BITHAM_34_MEDIUM_NUMBERS",
    "BITHAM_34_LIGHT_SUBSET",
    "BITHAM_18_LIGHT_SUBSET",
    "ROBOTO_CONDENSED_21",
    "ROBOTO_BOLD_SUBSET_49",
    "DROID_SERIF_28_BOLD",
    "LECO_20_BOLD_NUMBERS",
    "LECO_26_BOLD_NUMBERS_AM_PM",
    "LECO_32_BOLD_NUMBERS",
    "LECO_36_BOLD_NUMBERS",
    "LECO_38_BOLD_NUMBERS",
    "LECO_42_NUMBERS",
    "LECO_28_LIGHT_NUMBERS",
    "FONT_FALLBACK",
)

def int_to_bytes(value, signed=False):
    return value.to_bytes(2, "little", signed=signed)

def bool_to_bytes(value):
    return int_to_bytes(int(value))

# as hex string "#FFFFFF"
def color_to_bytes(color):
    r_int = int(color[1:3], 16)
    g_int = int(color[3:5], 16)
    b_int = int(color[5:7], 16)
    a_int = 255

    r, g, b, a = nearest_color_to_pebble64_palette(r_int, g_int, b_int, a_int)

    rgba = rgba32_triplet_to_argb8(r, g, b, a)
    return int_to_bytes(rgba)

def get_bw_or_color(data, platform, base_key):
    bw_key = BW_PREFIX + base_key
    if platform in ('aplite', 'diorite') and bw_key in data:
        return data[bw_key]
    return data[base_key]

def string_to_bytes(data):
    trunc_str = data[:MAX_STRING_SIZE]
    str_bytes = trunc_str.encode("utf-8")
    return str_bytes + bytes((MAX_STRING_SIZE - len(str_bytes)) + 1)

def font_to_bytes(value):
    return string_to_bytes("RESOURCE_ID_" + value)

def generate_datestr(base_format, spacer):
    new_datestr = base_format.replace("-", spacer)
    for old, new in DATE_FORMAT_CONVERSIONS.items():
        new_datestr = new_datestr.replace(old, new)
    return new_datestr

# returns byte array
def convert_config(conf, platform):
    conf_buffer = BytesIO()
    # Background
    bg_conf = conf["background"]
    conf_buffer.write(color_to_bytes(get_bw_or_color(bg_conf, platform, "colour")))
    conf_buffer.write(int_to_bytes(bg_conf["x"], True))
    conf_buffer.write(int_to_bytes(bg_conf["y"], True))
    conf_buffer.write(int_to_bytes(bg_conf["width"]))
    conf_buffer.write(int_to_bytes(bg_conf["height"]))

    # Clocks
    clock_conf = conf["clocks"]
    # - Analog
    ana_conf = clock_conf["analogue"]
    conf_buffer.write(bool_to_bytes(ana_conf["enabled"]))
    conf_buffer.write(int_to_bytes(ana_conf["x"], True))
    conf_buffer.write(int_to_bytes(ana_conf["y"], True))
    conf_buffer.write(int_to_bytes(ana_conf["radius"]))
    conf_buffer.write(int_to_bytes(ana_conf["hand_size"]))
    conf_buffer.write(bool_to_bytes(ana_conf["second_hand"]))
    conf_buffer.write(bool_to_bytes(ana_conf["pips"]))
    conf_buffer.write(color_to_bytes(get_bw_or_color(ana_conf, platform, "hands_colour")))
    # - Digital
    dig_conf = clock_conf["digital"]
    conf_buffer.write(bool_to_bytes(dig_conf["enabled"]))
    conf_buffer.write(int_to_bytes(dig_conf["font_size"]))
    conf_buffer.write(color_to_bytes(get_bw_or_color(dig_conf, platform, "colour")))
    conf_buffer.write(int_to_bytes(dig_conf["x"], True))
    conf_buffer.write(int_to_bytes(dig_conf["y"], True))
    conf_buffer.write(bool_to_bytes(dig_conf.get("system_font", "") in SYSTEM_FONTS))
    conf_buffer.write(font_to_bytes(dig_conf.get("system_font", "")))

    # Date
    date_conf = conf["date"]
    conf_buffer.write(bool_to_bytes(date_conf["enabled"]))
    conf_buffer.write(int_to_bytes(date_conf["font_size"]))
    conf_buffer.write(color_to_bytes(get_bw_or_color(date_conf, platform, "colour")))
    conf_buffer.write(int_to_bytes(date_conf["x"], True))
    conf_buffer.write(int_to_bytes(date_conf["y"], True))
    conf_buffer.write(string_to_bytes(generate_datestr(date_conf["format"], date_conf["spacer"])))
    conf_buffer.write(bool_to_bytes(date_conf.get("system_font", "") in SYSTEM_FONTS))
    conf_buffer.write(font_to_bytes(date_conf.get("system_font", "")))

    # Text
    text_conf = conf["text"]
    conf_buffer.write(bool_to_bytes(text_conf["enabled"]))
    conf_buffer.write(int_to_bytes(text_conf["font_size"]))
    conf_buffer.write(color_to_bytes(get_bw_or_color(text_conf, platform, "colour")))
    conf_buffer.write(int_to_bytes(text_conf["x"], True))
    conf_buffer.write(int_to_bytes(text_conf["y"], True))
    conf_buffer.write(string_to_bytes(text_conf["text"]))
    conf_buffer.write(bool_to_bytes(text_conf.get("system_font", "") in SYSTEM_FONTS))
    conf_buffer.write(font_to_bytes(text_conf.get("system_font", "")))

    return conf_buffer