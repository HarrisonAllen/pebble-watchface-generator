#include <pebble.h>

static Window *s_main_window;

static BitmapLayer *s_background_layer;
static GBitmap *s_background_bitmap;

static void main_window_load(Window *window) {
  Layer *window_layer = window_get_root_layer(window);
  GRect bounds = layer_get_bounds(window_layer);

  // bitmaps
  // bg
  s_background_layer = bitmap_layer_create(GRect((bounds.size.w - 180) / 2, (bounds.size.h - 180) / 2, 180, 180));
  // bitmap_layer_set_compositing_mode(s_background_layer, GCompOpSet);
  s_background_bitmap = gbitmap_create_with_resource(RESOURCE_ID_IMAGE_BACKGROUND);
  bitmap_layer_set_bitmap(s_background_layer, s_background_bitmap);

  // stack up the layers
  layer_add_child(window_layer, bitmap_layer_get_layer(s_background_layer));
}

static void main_window_unload(Window *window) {
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

  // Show the Window on the watch, with animated=true
  window_stack_push(s_main_window, true);
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