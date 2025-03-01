#ifndef WATCH_DATA_H
#define WATCH_DATA_H

#include <pebble.h>

#define MAX_STRING_LEN 32

// All data is 2 bytes because differing lengths of data add unknown padding to the struct
// Exception is strings of known lengths
typedef struct {
    // Background data
    unsigned short int background_color;
    short int background_x;
    short int background_y;
    unsigned short int background_width;
    unsigned short int background_height;

    // Clocks
    // Analog
    unsigned short int analog_enabled;
    short int analog_x;
    short int analog_y;
    unsigned short int analog_radius;
    unsigned short int analog_hand_size;
    unsigned short int analog_seconds_enabled;
    unsigned short int analog_pips_enabled;
    unsigned short int analog_hands_color; 
    // Digital
    unsigned short int digital_enabled;
    unsigned short int digital_font_size;
    unsigned short int digital_font_color;
    short int digital_x;
    short int digital_y;
    unsigned short int digital_use_system_font;
    char digital_system_font[MAX_STRING_LEN];

    // Date
    unsigned short int date_enabled;
    unsigned short int date_font_size;
    unsigned short int date_font_color;
    short int date_x;
    short int date_y;
    char date_format[MAX_STRING_LEN];
    unsigned short int date_use_system_font;
    char date_system_font[MAX_STRING_LEN];

    // Text
    unsigned short int text_enabled;
    unsigned short int text_font_size;
    unsigned short int text_font_color;
    short int text_x;
    short int text_y;
    char text_text[MAX_STRING_LEN];
    unsigned short int text_use_system_font;
    char text_system_font[MAX_STRING_LEN];
} WatchData;

#endif