from io import BytesIO
from pebble_image_routines import nearest_color_to_pebble64_palette, rgba32_triplet_to_argb8

def int_to_bytes(value):
    return value.to_bytes(2, "little")

# as hex string "#FFFFFF"
def color_to_bytes(color):
    r_int = int(color[1:3], 16)
    g_int = int(color[3:5], 16)
    b_int = int(color[5:7], 16)
    a_int = 255

    r, g, b, a = nearest_color_to_pebble64_palette(r_int, g_int, b_int, a_int)

    rgba = rgba32_triplet_to_argb8(r, g, b, a)
    return int_to_bytes(rgba)

# returns byte array
def convert_config(conf):
    conf_buffer = BytesIO()
    # Background
    bg_conf = conf["background"]
    conf_buffer.write(color_to_bytes(bg_conf["colour"]))
    conf_buffer.write(int_to_bytes(bg_conf["x"]))
    conf_buffer.write(int_to_bytes(bg_conf["y"]))
    conf_buffer.write(int_to_bytes(bg_conf["width"]))
    conf_buffer.write(int_to_bytes(bg_conf["height"]))

    # Clocks
    clock_conf = conf["clocks"]
    # - Analog
    ana_conf = clock_conf["analogue"]
    conf_buffer.write(int_to_bytes(int(ana_conf["enabled"])))
    conf_buffer.write(int_to_bytes(ana_conf["x"]))
    conf_buffer.write(int_to_bytes(ana_conf["y"]))
    conf_buffer.write(int_to_bytes(int(ana_conf["second_hand"])))
    conf_buffer.write(int_to_bytes(int(ana_conf["pips"])))
    conf_buffer.write(color_to_bytes(ana_conf["hands_colour"]))
    # - Digital
    dig_conf = clock_conf["digital"]
    conf_buffer.write(int_to_bytes(int(dig_conf["enabled"])))
    conf_buffer.write(int_to_bytes(dig_conf["font_size"]))
    conf_buffer.write(color_to_bytes(dig_conf["colour"]))
    conf_buffer.write(int_to_bytes(dig_conf["x"]))
    conf_buffer.write(int_to_bytes(dig_conf["y"]))

    return conf_buffer