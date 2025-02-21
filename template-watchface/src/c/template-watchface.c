#include <pebble.h>

#if defined(PBL_ROUND)
  #define Y_OFFSET 5
#else
  #define Y_OFFSET 0
#endif


static Window *s_main_window;

static BitmapLayer *s_background_layer;
static GBitmap *s_background_bitmap;

static TextLayer *s_time_layer;
static GFont s_time_font;

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
  s_time_layer = text_layer_create(GRect(0, 2 + Y_OFFSET, bounds.size.w, 56));
  // create and load time font
  s_time_font = fonts_load_custom_font(resource_get_handle(RESOURCE_ID_FONT_TIME_52));
  // stylize the text
  text_layer_set_background_color(s_time_layer, GColorClear);
  text_layer_set_text_color(s_time_layer, GColorWhite);
  text_layer_set_font(s_time_layer, s_time_font);
  text_layer_set_text_alignment(s_time_layer, GTextAlignmentCenter);

  // bitmaps
  // bg
  s_background_layer = bitmap_layer_create(GRect((bounds.size.w - 180) / 2, (bounds.size.h - 180) / 2, 180, 180));
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
  // Create main Window element and assign to pointer
  s_main_window = window_create();

  // Set handlers to manage the elements inside the Window
  window_set_window_handlers(s_main_window, (WindowHandlers) {
    .load = main_window_load,
    .unload = main_window_unload
  });
  
  window_set_background_color(s_main_window, PBL_IF_BW_ELSE(GColorDarkGray, GColorBlue));

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