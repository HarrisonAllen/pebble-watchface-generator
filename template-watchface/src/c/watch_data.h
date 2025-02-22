#ifndef WATCH_DATA_H
#define WATCH_DATA_H

#include <pebble.h>

// All data is 2 bytes because differing lengths of data add unknown padding to the struct
typedef struct {
    // Background data
    uint16_t background_color;
    int16_t background_x;
    int16_t background_y;
    uint16_t background_width;
    uint16_t background_height;

    // Clocks
    // Analog
    uint16_t analog_enabled;
    int16_t analog_x;
    int16_t analog_y;
    uint16_t analog_seconds_enabled;
    uint16_t analog_pips_enabled;
    uint16_t analog_hands_color; 
    // Digital
    uint16_t digital_enabled;
    uint16_t digital_font_size;
    uint16_t digital_color;
    int16_t digital_x;
    int16_t digital_y;
} WatchData;

#endif