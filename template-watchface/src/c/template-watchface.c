#include <pebble.h>
#include "watch_data.h"

#if defined(PBL_ROUND)
  #define CENTER_X 90
  #define CENTER_Y 90
#else
  #define CENTER_X 72
  #define CENTER_Y 84
#endif
#define FONT_BUFFER_Y 4 // How much extra space to give the font to render
#define HOUR_MODIFIER 0.6 // Ratio of hour hand length to minute hand length
#define MAJOR_PIP_RAD 2 // Radius of the cardinal hour pips
#define MINOR_PIP_RAD 1 // Radius of the other hour pips


static Window *s_main_window;

static WatchData s_watch_data;

static BitmapLayer *s_background_layer;
static GBitmap *s_background_bitmap;

static TextLayer *s_time_layer;
static GFont s_time_font;

static TextLayer *s_date_layer;
static GFont s_date_font;

static TextLayer *s_text_layer;
static GFont s_text_font;

static Layer *s_analog_layer;
static uint8_t s_sec, s_min, s_hour;
static GRect s_hour_bounds;
static GRect s_minute_bounds;

// Given a line and its center, reposition value relative to that
static int center_value(int value, int center_value, int size) {
  return value + center_value - size / 2;
}

// Load watch data from the data file
static void load_data(WatchData *watch_data) {
  ResHandle handle = resource_get_handle(RESOURCE_ID_DATA);
  size_t res_size = resource_size(handle);
  resource_load(handle, (uint8_t *)(watch_data), res_size);
}

static void update_time() {
  time_t temp = time(NULL);
  struct tm *tick_time = localtime(&temp);

  if (s_watch_data.digital_enabled) {
    // put hours and minutes into buffer
    static char s_buffer[8];
    strftime(s_buffer, sizeof(s_buffer), clock_is_24h_style() ?
                                          "%H:%M" : "%I:%M", tick_time);
    // display it
    text_layer_set_text(s_time_layer, s_buffer);
  }

  if (s_watch_data.analog_enabled) {
    s_hour = tick_time->tm_hour % 12;
    s_min = tick_time->tm_min;
    s_sec = tick_time->tm_sec;
    
    layer_mark_dirty(s_analog_layer);
  }
}

// This is where we draw the analog clock
static void analog_update_proc(Layer *layer, GContext *ctx) {
  if (!s_watch_data.analog_enabled) return;
  
  graphics_context_set_antialiased(ctx, false);
  GPoint center = GPoint((s_minute_bounds.origin.x + s_minute_bounds.size.w) / 2, 
                         (s_minute_bounds.origin.y + s_minute_bounds.size.h) / 2);

  // Draw pips for the hours
  if (s_watch_data.analog_pips_enabled) {
    GPoint point;
    for (uint8_t i = 0; i < 12; i++) {
      graphics_context_set_fill_color(ctx, (GColor8)((uint8_t)s_watch_data.analog_hands_color));
      point = gpoint_from_polar(s_minute_bounds, GOvalScaleModeFitCircle, DEG_TO_TRIGANGLE(i*(360/12)));
      graphics_fill_circle(ctx, point, i % 3 == 0 ? MAJOR_PIP_RAD : MINOR_PIP_RAD);
    }
  }

  // Calculate the hand angles
  int32_t hour_angle = TRIG_MAX_ANGLE * s_hour / 12 + TRIG_MAX_ANGLE / 12 * s_min / 60;
  int32_t minute_angle = TRIG_MAX_ANGLE * s_min / 60;
  int32_t second_angle = TRIG_MAX_ANGLE * s_sec / 60;

  // Calculate hand end points
  GPoint hour_endpoint = gpoint_from_polar(s_hour_bounds, GOvalScaleModeFitCircle, hour_angle);
  GPoint min_endpoint = gpoint_from_polar(s_minute_bounds, GOvalScaleModeFitCircle, minute_angle);
  GPoint sec_endpoint = gpoint_from_polar(s_minute_bounds, GOvalScaleModeFitCircle, second_angle);
  
  // Draw the hour hand
  graphics_context_set_stroke_width(ctx, s_watch_data.analog_hand_size);
  graphics_context_set_stroke_color(ctx, (GColor8)((uint8_t)s_watch_data.analog_hands_color));
  graphics_draw_line(ctx, center, hour_endpoint);

  // Draw the minute hand
  graphics_context_set_stroke_width(ctx, s_watch_data.analog_hand_size);
  graphics_context_set_stroke_color(ctx, (GColor8)((uint8_t)s_watch_data.analog_hands_color));
  graphics_draw_line(ctx, center, min_endpoint);

  // Draw the second hand
  if (s_watch_data.analog_seconds_enabled) {
    graphics_context_set_stroke_width(ctx, 1);
    graphics_context_set_stroke_color(ctx, (GColor8)((uint8_t)s_watch_data.analog_hands_color));
    graphics_draw_line(ctx, center, sec_endpoint);
  }
}

static void update_date(){
  if (!s_watch_data.date_enabled) return;
  time_t temp = time(NULL);
  struct tm *tick_time = localtime(&temp);

  static char s_date_buffer[16];
  strftime(s_date_buffer, sizeof(s_date_buffer), s_watch_data.date_format, tick_time);
  
  text_layer_set_text(s_date_layer, s_date_buffer);
}

static void time_handler(struct tm *tick_time, TimeUnits units_changed) {
  update_time();
  update_date();
}

static void main_window_load(Window *window) {
  Layer *window_layer = window_get_root_layer(window);
  GRect bounds = layer_get_bounds(window_layer);

  // time
  // digital
  s_time_layer = text_layer_create(GRect(center_value(s_watch_data.digital_x, CENTER_X, bounds.size.w), 
                                         center_value(s_watch_data.digital_y, CENTER_Y, s_watch_data.digital_font_size + FONT_BUFFER_Y), 
                                         bounds.size.w, 
                                         s_watch_data.digital_font_size + FONT_BUFFER_Y));
  if (s_watch_data.digital_use_system_font) {
    s_time_font = fonts_get_system_font(s_watch_data.digital_system_font);
  } else {
    s_time_font = fonts_load_custom_font(resource_get_handle(RESOURCE_ID_FONT_TIME_52));
  }
  text_layer_set_background_color(s_time_layer, GColorClear);
  text_layer_set_text_color(s_time_layer, (GColor8)((uint8_t)s_watch_data.digital_font_color));
  text_layer_set_font(s_time_layer, s_time_font);
  text_layer_set_text_alignment(s_time_layer, GTextAlignmentCenter);
  // analog
  GPoint center = GPoint(center_value(s_watch_data.analog_x, CENTER_X, 0), 
                         center_value(s_watch_data.analog_y, CENTER_Y, 0));
  GRect analog_bounds = GRect(center.x - s_watch_data.analog_radius - MAJOR_PIP_RAD, 
                              center.y - s_watch_data.analog_radius - MAJOR_PIP_RAD,
                              s_watch_data.analog_radius * 2 + MAJOR_PIP_RAD * 2,
                              s_watch_data.analog_radius * 2 + MAJOR_PIP_RAD * 2);
  // These are relative to the analog layer
  s_minute_bounds = GRect(MAJOR_PIP_RAD, 
                          MAJOR_PIP_RAD,
                          s_watch_data.analog_radius * 2,
                          s_watch_data.analog_radius * 2);
  s_hour_bounds = GRect(s_minute_bounds.origin.x + s_watch_data.analog_radius * ( 1 - HOUR_MODIFIER), 
                        s_minute_bounds.origin.y + s_watch_data.analog_radius * ( 1 - HOUR_MODIFIER),
                        s_watch_data.analog_radius * 2 * HOUR_MODIFIER, 
                        s_watch_data.analog_radius * 2 * HOUR_MODIFIER);
  s_analog_layer = layer_create(analog_bounds);
  layer_set_update_proc(s_analog_layer, analog_update_proc);

  // date
  s_date_layer = text_layer_create(GRect(center_value(s_watch_data.date_x, CENTER_X, bounds.size.w),
                                         center_value(s_watch_data.date_y, CENTER_Y, s_watch_data.date_font_size + FONT_BUFFER_Y), 
                                         bounds.size.w, 
                                         s_watch_data.date_font_size + FONT_BUFFER_Y));
  if (s_watch_data.date_use_system_font) {
    s_date_font = fonts_get_system_font(s_watch_data.date_system_font);
  } else {
    s_date_font = fonts_load_custom_font(resource_get_handle(RESOURCE_ID_FONT_DATE_32));
  }
  text_layer_set_background_color(s_date_layer, GColorClear);
  text_layer_set_text_color(s_date_layer, (GColor8)((uint8_t)s_watch_data.date_font_color));
  text_layer_set_font(s_date_layer, s_date_font);
  text_layer_set_text_alignment(s_date_layer, GTextAlignmentCenter);

  // text
  s_text_layer = text_layer_create(GRect(center_value(s_watch_data.text_x, CENTER_X, bounds.size.w),
                                         center_value(s_watch_data.text_y, CENTER_Y, s_watch_data.text_font_size + FONT_BUFFER_Y), 
                                         bounds.size.w, 
                                         s_watch_data.text_font_size + FONT_BUFFER_Y));
  if (s_watch_data.text_use_system_font) {
    s_text_font = fonts_get_system_font(s_watch_data.text_system_font);
  } else {
    s_text_font = fonts_load_custom_font(resource_get_handle(RESOURCE_ID_FONT_TEXT_20));
  }
  text_layer_set_background_color(s_text_layer, GColorClear);
  text_layer_set_text_color(s_text_layer, (GColor8)((uint8_t)s_watch_data.text_font_color));
  text_layer_set_font(s_text_layer, s_text_font);
  text_layer_set_text_alignment(s_text_layer, GTextAlignmentCenter);
  if (s_watch_data.text_enabled) {
    text_layer_set_text(s_text_layer, s_watch_data.text_text);
  }

  // bitmaps
  // bg
  s_background_layer = bitmap_layer_create(GRect(center_value(s_watch_data.background_x, CENTER_X, s_watch_data.background_width),
                                                 center_value(s_watch_data.background_y, CENTER_Y, s_watch_data.background_height), 
                                                 s_watch_data.background_width, 
                                                 s_watch_data.background_height));
  bitmap_layer_set_compositing_mode(s_background_layer, GCompOpSet);
  s_background_bitmap = gbitmap_create_with_resource(RESOURCE_ID_IMAGE_BACKGROUND);
  bitmap_layer_set_bitmap(s_background_layer, s_background_bitmap);

  // stack up the layers
  layer_add_child(window_layer, bitmap_layer_get_layer(s_background_layer));
  layer_add_child(window_layer, text_layer_get_layer(s_time_layer));
  layer_add_child(window_layer, text_layer_get_layer(s_date_layer));
  layer_add_child(window_layer, text_layer_get_layer(s_text_layer));
  layer_add_child(window_layer, s_analog_layer);
}

static void main_window_unload(Window *window) {
  // unload text layers
  text_layer_destroy(s_time_layer);
  text_layer_destroy(s_date_layer);
  text_layer_destroy(s_text_layer);

  // unload custom fonts
  if (!s_watch_data.digital_use_system_font)
  {
    fonts_unload_custom_font(s_time_font);
  }
  if (!s_watch_data.date_use_system_font)
  {
    fonts_unload_custom_font(s_date_font);
  }
  if (!s_watch_data.text_use_system_font)
  {
    fonts_unload_custom_font(s_text_font);
  }

  // unload bitmap layers
  bitmap_layer_destroy(s_background_layer);
  
  // unload gbitmaps
  gbitmap_destroy(s_background_bitmap);

  // unload other layers
  layer_destroy(s_analog_layer);
}

static void init() {
  load_data(&s_watch_data);
  
  // Create main Window element and assign to pointer
  s_main_window = window_create();

  // Set handlers to manage the elements inside the Window
  window_set_window_handlers(s_main_window, (WindowHandlers) {
    .load = main_window_load,
    .unload = main_window_unload
  });
  
  window_set_background_color(s_main_window, (GColor8)((uint8_t)s_watch_data.background_color));

  // Show the Window on the watch, with animated=true
  window_stack_push(s_main_window, true);

  // set up tick_handler to run every minute (or second if seconds enabled)
  if (s_watch_data.analog_enabled && s_watch_data.analog_seconds_enabled) {
    tick_timer_service_subscribe(SECOND_UNIT, time_handler);
  } else {
    tick_timer_service_subscribe(MINUTE_UNIT, time_handler);
  }
  // want to display time and date at the start
  update_time();
  update_date();
}

static void deinit() {
  // Destroy Window
  window_destroy(s_main_window);
}

int main(void) {
  init();
  app_event_loop();
  deinit();
}