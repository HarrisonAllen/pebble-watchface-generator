#include <pebble.h>
#include "watch_data.h"

#if defined(PBL_ROUND)
  #define Y_OFFSET 5
#else
  #define Y_OFFSET 0
#endif


static Window *s_main_window;

static WatchData s_watch_data;

static BitmapLayer *s_background_layer;
static GBitmap *s_background_bitmap;

static TextLayer *s_time_layer;
static GFont s_time_font;

// static bool load(WatchData *data) {
//   return persist_read_data(SAVE_KEY, data, sizeof(PokemonSaveData)) != E_DOES_NOT_EXIST;
// }

static void load_data(WatchData *watch_data) {
  ResHandle handle = resource_get_handle(RESOURCE_ID_DATA);
  size_t res_size = resource_size(handle);
  resource_load(handle, (uint8_t *)(watch_data), res_size);
}

static void update_time() {
  time_t temp = time(NULL);
  struct tm *tick_time = localtime(&temp);

  // put hours and minutes into buffer
  static char s_buffer[8];
  strftime(s_buffer, sizeof(s_buffer), clock_is_24h_style() ?
                                        "%H:%M" : "%I:%M", tick_time);
  // display it
  text_layer_set_text(s_time_layer, s_buffer);    
}

static void time_handler(struct tm *tick_time, TimeUnits units_changed) {
  update_time();
}

static void main_window_load(Window *window) {
  Layer *window_layer = window_get_root_layer(window);
  GRect bounds = layer_get_bounds(window_layer);

  // time
  s_time_layer = text_layer_create(GRect(s_watch_data.digital_x, s_watch_data.digital_y + Y_OFFSET, bounds.size.w, s_watch_data.digital_font_size + 4));
  // create and load time font
  s_time_font = fonts_load_custom_font(resource_get_handle(RESOURCE_ID_FONT_TIME_52));
  // stylize the text
  text_layer_set_background_color(s_time_layer, GColorClear);
  text_layer_set_text_color(s_time_layer, (GColor8)((uint8_t)s_watch_data.digital_color));
  text_layer_set_font(s_time_layer, s_time_font);
  text_layer_set_text_alignment(s_time_layer, GTextAlignmentCenter);

  // bitmaps
  // bg
  s_background_layer = bitmap_layer_create(GRect(s_watch_data.background_x + (bounds.size.w - 180) / 2, s_watch_data.background_y + (bounds.size.h - 180) / 2, s_watch_data.background_width, s_watch_data.background_height));
  bitmap_layer_set_compositing_mode(s_background_layer, GCompOpSet);
  s_background_bitmap = gbitmap_create_with_resource(RESOURCE_ID_IMAGE_BACKGROUND);
  bitmap_layer_set_bitmap(s_background_layer, s_background_bitmap);

  // stack up the layers
  layer_add_child(window_layer, bitmap_layer_get_layer(s_background_layer));
  layer_add_child(window_layer, text_layer_get_layer(s_time_layer));
}

static void main_window_unload(Window *window) {
  // unload text layers
  text_layer_destroy(s_time_layer);

  // unload custom fonts
  fonts_unload_custom_font(s_time_font);

  // unload bitmap layers
  bitmap_layer_destroy(s_background_layer);
  
  // unload gbitmaps
  gbitmap_destroy(s_background_bitmap);
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

  // set up tick_handler to run every minute
  tick_timer_service_subscribe(MINUTE_UNIT, time_handler);
  // want to display time and at the start
  update_time();
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