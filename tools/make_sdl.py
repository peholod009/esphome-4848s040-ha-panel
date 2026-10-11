#!/usr/bin/env python3
"""Делает из panel-saray.yaml тестовый SDL-вариант для рендера скриншотов на хосте.
Разметка страниц/шрифты/лямбды — те же самые; меняется только «железо»:
SDL-экран вместо ST7701S, без Wi-Fi/OTA, демо-значения из HA подставляются
через publish_state (идут те же on_value-цепочки, что на панели)."""
import re, sys
src, dst, page = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding="utf-8").read()

# пакеты железа -> SDL
s = s.replace("  wifi:           !include esphome-modular-lvgl-buttons/common/wifi.yaml\n", "")
s = s.replace("  ota_screen:     !include esphome-modular-lvgl-buttons/common/ota.yaml\n", "")
s = s.replace("common/sensors_base.yaml", "common/sensors_base_sdl.yaml")
s = s.replace("hardware/guition-esp32-s3-4848s040.yaml", "hardware/SDL-lvgl.yaml")
s = re.sub(r"\nwifi:\n(  .*\n|\n)*?(?=\S)", "\n", s)
s = re.sub(r"\nota:\n  - platform: esphome\n", "\n", s)
s = s.replace("\ncaptive_portal:\n", "\n")
s = re.sub(r"api:\n  encryption:\n    key: !secret panel_saray_api_key\n", "api:\n", s)
s = s.replace("https://github.com/Templarian/MaterialDesign-Webfont/raw/",
              "https://raw.githubusercontent.com/Templarian/MaterialDesign-Webfont/")

# в SDL нет HA/времени -> подсветка остаётся выключенной, и on_turn_off ставит LVGL
# на паузу (анимации слайдеров замирают). Для рендера паузу убираем.
s = s.replace("""    on_turn_off:
      - lvgl.pause:
""", "")

# обход бага ST7701S (повтор init_sequence) к SDL-экрану не относится
s = re.sub(r"\ndisplay:\n  - id: !extend my_display\n    init_sequence:\n(      - .*\n)+", "\n", s)

subs_extra = '''  screen_height: '480'
  screen_width:  '480'
'''
s = s.replace('  bg_color: white\n', '  bg_color: white\n' + subs_extra, 1)

demo = f'''
external_components:
  - source:
      type: local
      path: esphome-modular-lvgl-buttons/components
    components: [lvgl_screenshot]

lvgl_screenshot:
  port: 8080

interval_demo:
  - interval: 1s
    then:
      - lambda: |-
          static int n = 0;
          n++;
          if (n == 9) {{ lv_scr_load(id(light_page)->obj); return; }}
          if (n == 15) {{ lv_scr_load(id(yard_page)->obj); return; }}
          if (n == 21) {{ lv_scr_load(id(music_page)->obj); return; }}
          if (n == 27) {{ lv_scr_load(id(settings_page)->obj); return; }}
          if (n != 3) return;
          id(ha_sauna_temp).publish_state(68.4);
          id(ha_sauna_trend).publish_state("rising");
          id(ha_out_temp).publish_state(22.9);
          id(ha_out_hum).publish_state(46);
          id(ha_weather_cond).publish_state("partlycloudy");
          id(ha_banya_status).publish_state("Занята");
          id(ha_toilet_status).publish_state("Свободен");
          id(ha_sarai_media_title).publish_state("It's A Beautiful Day");
          id(ha_sarai_play_state).publish_state("playing");
          id(ha_sarai_volume).publish_state(0.5);
          id(ha_led_brightness).publish_state("102");
          id(ha_naves_state).publish_state(true);
          id(ha_vnutri_state).publish_state(false);
          id(ha_verstak_state).publish_state(false);
          id(ha_mangal_state).publish_state(true);
          id(ha_drovnik_state).publish_state(false);
          id(ha_led_state).publish_state(true);
          id(ha_y_krylco_state).publish_state(true);
          id(ha_y_kalitka_state).publish_state(true);
          id(ha_y_sredniy_state).publish_state(false);
          id(ha_y_osnovnye_state).publish_state(false);
          id(ha_y_torec_state).publish_state(false);
          id(ha_y_valya_state).publish_state(false);
          id(ha_y_ploshadka_state).publish_state(false);
          id(ha_y_veranda_state).publish_state(false);
          id(ha_y_tualet_in_state).publish_state(false);
          id(ha_y_tualet_out_state).publish_state(false);
          lv_label_set_text(id(connected_ssid_label), "my_wifi");
          lv_label_set_text(id(wifi_signal_db_percent_label), "74%");
          lv_label_set_text(id(ip_address_label), "192.168.1.50");
          lv_label_set_text(id(lbl_clock), "16:40");
          lv_label_set_text(id(lbl_date), "сб, 10 октября");
          lv_scr_load(id({page})->obj);
'''
s = s.replace("esphome:\n  name: ${name}\n", "esphome:\n  name: ${name}\n  platformio_options:\n    platform: https://github.com/platformio/platform-native.git\n", 1)
s = s.rstrip() + "\n" + demo
# в основном файле уже есть свой interval: (автовозврат) -> демо-элемент кладём в тот же список
demo_item = s[s.index("interval_demo:\n") + len("interval_demo:\n"):]
s = s[:s.index("interval_demo:\n")]
s = s.replace("\ninterval:\n", "\ninterval:\n" + demo_item, 1)
open(dst, "w", encoding="utf-8").write(s)
print("ok", dst)
