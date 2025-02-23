#ifndef WATCH_DATA_H
#define WATCH_DATA_H

#include <pebble.h>

#define MAX_STRING_LEN 32

// All data is 2 bytes because differing lengths of data add unknown padding to the struct
// Exception is strings of known lengths
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
    uint16_t digital_font_color;
    int16_t digital_x;
    int16_t digital_y;

    // Date
    uint16_t date_enabled;
    uint16_t date_font_size;
    uint16_t date_font_color;
    int16_t date_x;
    int16_t date_y;
    char date_format[MAX_STRING_LEN];

    // Text
    uint16_t text_enabled;
    uint16_t text_font_size;
    uint16_t text_font_color;
    int16_t text_x;
    int16_t text_y;
    char text_text[MAX_STRING_LEN];
} WatchData;

#endif