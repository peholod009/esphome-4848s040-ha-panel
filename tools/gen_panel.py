#!/usr/bin/env python3
"""Генератор panel-saray.yaml из макета Mix-* (канвас «Итог»).

Все координаты/размеры взяты из Mix-Main/Light/Music.dc.html.
Правила переноса CSS -> LVGL:
  * «клавиша» (border 2px + нижняя губа 6px): LVGL-кнопка высотой h-4,
    рамка 2px, губа = жёсткая тень shadow_offset_y 4 (width 1, spread 0, opa COVER).
    У большой паузы губа 8px -> h-6 и offset 6.
  * текст: CSS line-height L, размер S -> LVGL label.y = top + (L - 1.364*S)/2
    (1.364 = (ascender+descender)/UPM у Nunito: (1011+353)/1000).
  * MDI-иконки: line-height = размер шрифта, глиф занимает тот же квадрат, что SVG.
  * Дочерние x/y в LVGL отсчитываются от внутреннего края рамки — как в CSS.
"""
import sys

OUT = sys.argv[1]

def ty(top, lh, size):
    """CSS top/line-height -> LVGL label y."""
    return int(round(top + (lh - 1.364 * size) / 2))

L = []          # строки YAML
def w(s=""):
    L.append(s)

def block(text, indent):
    pad = " " * indent
    for line in text.strip("\n").split("\n"):
        L.append(pad + line if line.strip() else "")

# --------------------------------------------------------------------------
# Цвета (текущая палитра панели)
C = dict(
    white="0xFFFFFF", text="0x212121", mut="0x606682", card="0xF3F4F8",
    orange="0xF37320", orange_dk="0xB4500E", lip_or="0xC85A12", tint_or="0xFDECD9",
    border="0xC7CCDE", lip="0xA9AFC4", track="0xE3E5EC",
    busy_bg="0xFCE4E4", busy_ic="0xEB5757", busy_tx="0xB3261E",
    free_bg="0xE3F4EA", free_ic="0x219653", free_tx="0x1B7A43",
    parn_bg="0xFDEEE3", blue="0x3FA7F3", blue_tx="0x1F6FA8",
)

MDI_URL = "https://github.com/Templarian/MaterialDesign-Webfont/raw/v7.4.47/fonts/materialdesignicons-webfont.ttf"
NUNITO = "esphome-modular-lvgl-buttons/assets/fonts/Nunito-SemiBold.ttf"

# ==========================================================================
HEADER = r'''
# ============================================================================
# Панель "Сарай" — Guition ESP32-S3-4848S040C_I (480x480, ST7701S + GT911)
# Дизайн "Итог" (канвас): структура и размеры зумерского варианта + текущая
# светлая палитра (оранжевый #F37320, серо-синий #606682, подложка плиток
# #F7F7FB->#E8EBF4 с обводкой #C7CCDE).
#
# 5 страниц: 4 во вкладках таб-бара внизу (Главная / Сарай / Двор / Музыка;
# свайп — запасной) + «Настройки» (вход с «Музыки»).
#   1. main_page   — часы/дата | улица; парная (тренд) | баня, туалет;
#                    мини-плеер на всю ширину: трек + слайдер громкости | пауза
#   2. light_page  — свет в сарае: 5 плиток-выключателей + LED-лента и яркость
#   3. yard_page   — свет во дворе: 10 плиток-выключателей на всю высоту
#   4. music_page  — трек | «Настройки»; назад/пауза/вперёд; громкость;
#                    2 радио + 2 плейлиста Яндекс Музыки (через Music Assistant)
#   5. settings_page — яркость день/ночь, режим, возврат на главную, гашение
#                    экрана, Wi-Fi/IP; вход только с «Музыки»
#
# Разметка перенесена из макета автоматически (генератором) — координаты
# совпадают с макетом пиксель в пиксель. Правила переноса:
#   * "клавиша" (всё, что нажимается): рамка 2px + толстая нижняя "губа" —
#     в LVGL губа сделана жёсткой тенью (shadow_offset_y 4, width 1), при
#     нажатии кнопка "вдавливается" (translate_y 4, тень 0).
#   * показания (не кнопки) — плоские светлые карточки без рамки и губы.
#
# ПЕРЕД ПРОШИВКОЙ:
#   1. Рядом с этим файлом — клон https://github.com/agillis/esphome-modular-lvgl-buttons
#   2. secrets.yaml: wifi_ssid, wifi_password, ap_password, panel_saray_api_key,
#      latitude, longitude (координаты — для расчёта солнца / яркости день-ночь)
#   3. Нужен интернет на машине с ESPHome: MDI-иконки качаются с GitHub,
#      Nunito ExtraBold (крупные цифры/заголовки) — с Google Fonts (gfonts).
#   4. ESPHome >= 2026.7.0. OTA работает (первая прошивка была по USB).
#   5. В HA у устройства должна стоять галочка "Allow the device to perform
#      Home Assistant actions", иначе нажатия молча не выполняются.
#
# Сущности HA (только эти):
#   свет:   light.sarai_troitskaya_saray_relay_light_1 (Навес), _3 (Внутри),
#           _4 (Верстак), _2 (Мангал), _5 (Дровник), light.troitskaya_saray_led_saray
#   двор:   light.bania_troitskaya_banya_banya_relay3 (Свет средний), _relay4 (Свет
#           основные), _relay5 (Калитка), _relay1 (Веранда),
#           light.khata_hata_2025_relay_light_3 (Крыльцо), _1 (Торец), _4 (Валя),
#           light.troitskaya_banya_banya_relay2 (Площадка),
#           light.tualet_troitskaya_toilet_toilet_relay1 / _relay2 (Туалет внутри/снаружи)
#   баня:  sensor.troitskaya_banya_banya_temperature, sensor.bania_temperatura_trend,
#           sensor.zaniatost_bani_2, sensor.zaniatost_tualeta_2
#   музыка: media_player.sarai (плеер Music Assistant); кнопки быстрого запуска —
#           script.sarai_muzyka_bystryi_zapusk (preset: russkoe / avto /
#           nravitsya / volna) — адреса станций и плейлистов живут в этом скрипте
#   улица:  weather.forecast_troitskaia
# ============================================================================
'''

w(HEADER.strip("\n"))
w()

block(r'''
substitutions:
  name: "panel-saray"
  friendly_name: "Панель Сарай"

  # --- светлая тема для библиотечных частей (поповеры, экран загрузки) ---
  icon_font:          mdi_icons_40
  text_font:          nunito_20
  button_on_color:    ep_orange
  button_off_color:   white
  icon_on_color:      white
  icon_off_color:     steel_blue
  label_on_color:     white
  label_off_color:    gray900
  button_text_color:  gray900
  popup_timeout_seconds: '120'
  bg_color: white

  # Кириллица: по умолчанию шрифты собираются только с GF_Latin_Kernel.
  glyphsets: ["GF_Latin_Kernel", "GF_Cyrillic_Core"]
  # Для названий треков — ещё и расширенная латиница (апострофы, ударения).
  title_glyphsets: ["GF_Latin_Core", "GF_Cyrillic_Core"]

  # Поворот изображения (по часовой стрелке): 0 / 90 / 180 / 270.
  # Библиотека по умолчанию ставит 180; 90 = картинка повёрнута на 90° влево
  # относительно прежней. Если повернулось не в ту сторону — поставь "270".
  rotation: "90"

  # Ночь — солнце ниже этого угла (−3°, как у автоматизации «Сарай LED ВКЛ»).
  night_sun_elevation: "-3"
  # Остальные настройки поведения (яркость днём/ночью, возврат на главную,
  # гашение экрана) — НЕ здесь: они на экране «Настройки» и в HA, значения
  # хранятся в самой панели (переживают перезагрузку).

esphome:
  name: ${name}
  friendly_name: ${friendly_name}
  # после setup всех компонентов: разрешаем обновлять виджеты настроек
  # (значения number/select восстанавливаются раньше, чем готов LVGL)
  on_boot:
    - priority: -100
      then:
        - lambda: 'id(ui_ready) = true;'
        - script.execute: settings_refresh
''', 0)
w()

# ==========================================================================
# ШРИФТЫ
w("# ----------------------------------------------------------------------------")
w("# Шрифты. Каждый размер из макета — отдельный шрифт (LVGL растеризует при сборке).")
w("#   nunito_N — Nunito SemiBold (файл из библиотеки): подписи, названия, статусы.")
w("#   nb_N     — Nunito ExtraBold (Google Fonts): крупные цифры и заголовки.")
w("#              Где текст заранее известен (цифры, СВЕТ, ПАРНАЯ, ВКЛ) — только")
w("#              нужные глифы, чтобы не тратить флеш.")
w("#   mdi_N    — Material Design Icons, только нужные глифы.")
w("# Библиотечные nunito_12/14/18/20/24/36/42/48/72 объявлены в пакете theme.")
w("# ----------------------------------------------------------------------------")
w("font:")

def sb_font(fid, size, gs="${glyphsets}"):
    w(f'  - file: "{NUNITO}"')
    w(f"    id: {fid}")
    w(f"    size: {size}")
    w(f"    bpp: 8")
    w(f"    glyphsets: {gs}")
    w()

def xb_font(fid, size, glyphs=None, gs=None):
    w("  - file:")
    w("      type: gfonts")
    w("      family: Nunito")
    w("      weight: 800")
    w(f"    id: {fid}")
    w(f"    size: {size}")
    w(f"    bpp: 8")
    if glyphs:
        glyphs = "".join(dict.fromkeys(glyphs))   # без повторов (ESPHome ругается на дубли)
        esc = glyphs.replace('"', '\\"')
        w(f'    glyphs: "{esc}"')
    if gs:
        w(f"    glyphsets: {gs}")
    w()

def mdi_font(fid, size, glyphs, comment=""):
    if comment:
        w(f"  # {comment}")
    w(f"  - file: '{MDI_URL}'")
    w(f"    id: {fid}")
    w(f"    size: {size}")
    w(f"    bpp: 8")
    w("    glyphs: [" + ", ".join(f"$mdi_{g}" for g in glyphs) + "]")
    w()

sb_font("nunito_16", 16)
sb_font("nunito_17", 17)
sb_font("nunito_19", 19, "${title_glyphsets}")

xb_font("nb_16", 16, glyphs="ПАРНАЯВКЛ")
xb_font("nb_20", 20, gs="${glyphsets}")
xb_font("nb_24", 24, glyphs="0123456789%-")
xb_font("nb_26", 26, gs="${title_glyphsets}")
xb_font("nb_28", 28, glyphs="0123456789%-")
xb_font("nb_44", 44, glyphs="0123456789°-.,+")
xb_font("nb_48", 48, glyphs="0123456789:-")
xb_font("nb_64", 64, glyphs="0123456789°-")

mdi_font("mdi_icons_40", 40,
         ["brightness_6", "circle_opacity", "eyedropper", "white_balance_sunny", "lightbulb"],
         "нужен библиотечному поповеру color-picker (substitution icon_font)")
mdi_font("mdi_16", 16, ["equalizer"], "значок «играет»")
mdi_font("mdi_20", 20, ["trending_up", "trending_down", "trending_neutral", "water", "wifi", "ip_network",
                        "heart", "waveform"],
         "тренд парной, капля влажности")
mdi_font("mdi_24", 24, ["thermometer", "volume_medium"], "парная, громкость в мини-плеере")
mdi_font("mdi_26", 26, ["home", "lightbulb", "post_lamp", "music", "cog", "volume_high",
                        "weather_sunny", "weather_night"], "таб-бар, радио, настройки")
mdi_font("mdi_28", 28, ["pot_steam", "toilet", "radio"], "баня/туалет, кнопки радио")
mdi_font("mdi_30", 30, ["pause", "play", "lightbulb", "lightbulb_outline"], "мини-плеер, плитки двора")
mdi_font("mdi_34", 34, ["lightbulb", "lightbulb_outline", "led_strip_variant"], "плитки света")
mdi_font("mdi_32", 32, ["skip_previous", "skip_next"], "назад/вперёд на странице музыки")
mdi_font("mdi_46", 46, ["weather_sunny", "weather_night", "weather_partly_cloudy",
                        "weather_night_partly_cloudy", "weather_cloudy", "weather_rainy",
                        "weather_pouring", "weather_snowy", "weather_snowy_rainy",
                        "weather_lightning", "weather_lightning_rainy", "weather_fog",
                        "weather_hail", "weather_windy", "weather_windy_variant",
                        "alert_circle_outline"], "погода")
mdi_font("mdi_40", 40, ["pause", "play"], "пауза на странице музыки")

# ==========================================================================
block(r'''
packages:
  # popup_system — первым: остальные пакеты расширяют его виджеты через !extend.
  popup_system:   !include esphome-modular-lvgl-buttons/ui/popup/popup_system.yaml
  wifi:           !include esphome-modular-lvgl-buttons/common/wifi.yaml
  ota_screen:     !include esphome-modular-lvgl-buttons/common/ota.yaml
  theme:          !include esphome-modular-lvgl-buttons/common/theme/index.yaml
  sensors:        !include esphome-modular-lvgl-buttons/common/sensors_base.yaml
  # backlight_time.yaml библиотеки НЕ подключаем: его логика яркости перенесена
  # ниже (блок «ЯРКОСТЬ ЭКРАНА ПО СОЛНЦУ») и переделана под порог −3°.
  hardware:       !include esphome-modular-lvgl-buttons/hardware/guition-esp32-s3-4848s040.yaml
  loading_screen: !include esphome-modular-lvgl-buttons/pages/loading.yaml
  # Погодный пакет библиотеки: используем только его подписку на HA. Его
  # картинки и подписи обязаны существовать (иначе "ID not found"), но на
  # экране они скрыты — иконка/температура/состояние на главной свои (MDI +
  # русские подписи, как в макете). size: 16 — картинки мелкие, флеш не тратим.
  tile_weather: !include
    file: esphome-modular-lvgl-buttons/ui/weather/today.yaml
    vars:
      size: 16
      weather_entity: "weather.forecast_troitskaia"
      # без этой переменной пакет при каждом подключении к HA вызывает
      # homeassistant.update_entity с буквальным "${weather_summary}" (ошибка в логе HA)
      weather_summary: "weather.forecast_troitskaia"

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  ap:
    ssid: "${friendly_name} Fallback"
    password: !secret ap_password

api:
  encryption:
    key: !secret panel_saray_api_key

ota:
  - platform: esphome

captive_portal:

logger:
  level: WARN

# ----------------------------------------------------------------------------
# Подсветку включает/гасит Home Assistant (автоматизации «Экран сарай ВКЛ/ВЫКЛ»:
# движение + таймер 10 мин). Когда HA гасит подсветку — ставим LVGL на паузу:
# касание тёмного экрана тогда не нажмёт невидимую кнопку (не переключит свет),
# а только разбудит панель (resume_on_input по умолчанию) — lvgl on_resume
# сам включит подсветку, HA увидит это и запустит таймер.
# Включение подсветки снимает паузу (on_turn_on ниже).
# ----------------------------------------------------------------------------
# ============================================================================
# ЯРКОСТЬ ЭКРАНА ПО СОЛНЦУ (вместо библиотечного backlight_time.yaml)
#   Day   — солнце выше −3°: яркость «Яркость днём» (экран «Настройки» / HA)
#   Night — солнце ниже −3°: яркость «Яркость ночью»
# Порог −3° — тот же, что у автоматизации «Сарай LED ВКЛ» в HA
# (sensor.sun_solar_elevation below −3): панель темнеет вместе с тем, как
# в сарае начинает включаться свет. Считает сама панель (компонент sun по
# координатам из secrets) — от HA нужна только синхронизация времени.
# Режим виден и переключается вручную в HA: select «Brightness mode»;
# ручной выбор держится до следующего перехода солнца через −3°.
# Отличия от библиотеки:
#   * один порог −3° утром и вечером (у библиотеки −3.5° вечером, −0.83° утром);
#   * нет "Evening" и перехода в Night в полночь;
#   * смена режима при ПОГАШЕННОМ экране его не включает (библиотека будила
#     экран на закате/в полночь/на рассвете, и HA держал его 10 минут) —
#     нужная яркость применяется в момент следующего включения.
# ============================================================================
globals:
  - id: boot_restart_published
    type: bool
    restore_value: no
    initial_value: 'false'
  # LVGL готов (см. esphome: on_boot) — до этого виджеты трогать нельзя
  - id: ui_ready
    type: bool
    restore_value: no
    initial_value: 'false'

sun:
  id: sun_sun
  latitude: !secret latitude
  longitude: !secret longitude
  on_sunset:
    - elevation: ${night_sun_elevation}°
      then:
        - select.set:
            id: brightness_mode
            option: "Night"
  on_sunrise:
    - elevation: ${night_sun_elevation}°
      then:
        - select.set:
            id: brightness_mode
            option: "Day"

select:
  - platform: template
    name: "Brightness mode"
    id: brightness_mode
    icon: mdi:television-shimmer
    optimistic: true
    # Evening оставлен в списке только ради совместимости с HA (сущность
    # уже есть); сама панель его не выбирает — он работает как Night.
    options:
      - Day
      - Evening
      - Night
    initial_option: Day
    on_value:
      then:
        # экран горит -> сразу новая яркость; погашен -> не будим
        - if:
            condition:
              light.is_on: display_backlight
            then:
              - script.execute: apply_brightness_mode
        - if:
            condition:
              lambda: return id(ui_ready);
            then:
              - script.execute: settings_show_mode

  # ---- НАСТРОЙКИ ПОВЕДЕНИЯ (экран «Настройки» <-> HA, значения в панели) ----
  # Через сколько без касаний панель сама возвращается на «Главную».
  - platform: template
    name: "Возврат на главную"
    id: cfg_home_return
    icon: mdi:home-clock
    entity_category: config
    optimistic: true
    restore_value: true
    options:
      - "1 мин"
      - "2 мин"
      - "5 мин"
      - "Выкл"
    initial_option: "2 мин"
    on_value:
      - if:
          condition:
            lambda: return id(ui_ready);
          then:
            - script.execute: settings_show_home_return

number:
  # Таймаут гашения библиотеки (в минутах, −1 = выкл). Экраном управляет HA,
  # поэтому в HA он стоит −1; оставлен, чтобы не пропала сущность.
  - platform: template
    id: display_backlight_timeout
    name: Backlight timeout
    icon: "mdi:timer-outline"
    optimistic: true
    unit_of_measurement: "min"
    initial_value: -1
    restore_value: true
    min_value: -1
    max_value: 720
    step: 1
    mode: box

  # Яркость экрана днём / ночью, %. Меняется слайдером на экране «Настройки»
  # или из HA — в обе стороны синхронно.
  - platform: template
    name: "Яркость днём"
    id: cfg_day_brightness
    icon: mdi:white-balance-sunny
    entity_category: config
    optimistic: true
    restore_value: true
    initial_value: 100
    min_value: 10
    max_value: 100
    step: 5
    unit_of_measurement: "%"
    mode: slider
    on_value:
      - if:
          condition:
            lambda: return id(ui_ready);
          then:
            - lvgl.slider.update:
                id: slider_cfg_day
                value: !lambda return x;
            - lvgl.label.update:
                id: lbl_cfg_day
                text: !lambda return str_sprintf("%d%%", (int) x);
      # действует сейчас -> сразу применяем (если экран горит)
      - if:
          condition:
            lambda: return id(brightness_mode).current_option() == "Day" && id(display_backlight).current_values.is_on();
          then:
            - script.execute: apply_brightness_mode

  - platform: template
    name: "Яркость ночью"
    id: cfg_night_brightness
    icon: mdi:weather-night
    entity_category: config
    optimistic: true
    restore_value: true
    initial_value: 50
    min_value: 5
    max_value: 100
    step: 5
    unit_of_measurement: "%"
    mode: slider
    on_value:
      - if:
          condition:
            lambda: return id(ui_ready);
          then:
            - lvgl.slider.update:
                id: slider_cfg_night
                value: !lambda return x;
            - lvgl.label.update:
                id: lbl_cfg_night
                text: !lambda return str_sprintf("%d%%", (int) x);
      - if:
          condition:
            lambda: return id(brightness_mode).current_option() != "Day" && id(display_backlight).current_values.is_on();
          then:
            - script.execute: apply_brightness_mode

  # Через сколько минут без движения HA гасит экран. Само гашение — в HA
  # (автоматизации «Экран сарай ВКЛ/ВЫКЛ» берут длительность таймера отсюда).
  - platform: template
    name: "Экран гаснет через"
    id: cfg_screen_off
    icon: mdi:timer-outline
    entity_category: config
    optimistic: true
    restore_value: true
    initial_value: 10
    min_value: 1
    max_value: 60
    step: 1
    unit_of_measurement: "min"
    mode: box
    on_value:
      - if:
          condition:
            lambda: return id(ui_ready);
          then:
            - script.execute: settings_show_screen_off

time:
  - platform: homeassistant
    id: system_time
    on_time_sync:
      - script.execute: time_update
      # один раз после загрузки: время рестарта + режим яркости по солнцу
      - if:
          condition:
            lambda: 'return id(boot_restart_published) == false;'
          then:
            - lambda: 'id(boot_restart_published) = true;'
            - text_sensor.template.publish:
                id: device_last_restart
                state: !lambda 'return id(system_time).now().strftime("%a %d %b %Y - %I:%M:%S %p");'
            - script.execute: set_brightness_mode_on_boot
    on_time:
      # часы и дата на главной — раз в минуту
      - seconds: 0
        minutes: '*'
        then:
          - script.execute: time_update

light:
  - id: !extend display_backlight
    on_turn_on:
      - lvgl.resume:
      # HA включает экран без яркости -> ставим яркость текущего режима
      - script.execute: apply_brightness_mode
    on_turn_off:
      - lvgl.pause:


# ----------------------------------------------------------------------------
# ОБХОД БАГА ESPHome (ST7701S, mipi_rgb): чёрный экран после OTA / Restart.
# Драйвер шлёт экрану программный сброс (0x01) и СРАЗУ, без паузы, всю
# настройку. После холодного старта контроллер спит и сбрасывается за ~5 мс —
# настройка доходит. После программной перезагрузки ESP32 контроллер экрана
# остаётся включённым (sleep-out), и его сброс длится ~120 мс: вся настройка
# уходит «в глухой» контроллер, экран остаётся чёрным до передёргивания питания.
# Исправлено в ESPHome PR #17646 (пауза после сброса), но в релизы ещё не
# попало. Обход: ПОСЛЕ стандартной настройки ждём 120 мс и отправляем ту же
# настройку модели GUITION-4848S040 ещё раз (дальше драйвер сам допишет формат
# пикселя, ориентацию, SLPOUT и DISPON). На холодном старте — просто повтор.
# Когда выйдет ESPHome с #17646 (ожидается 2026.10), блок можно удалить.
# ----------------------------------------------------------------------------
display:
  - id: !extend my_display
    init_sequence:
      - delay 120ms
      - [0xFF, 0x77, 0x01, 0x00, 0x00, 0x10]
      - [0xC0, 0x3B, 0x00]
      - [0xC1, 0x0D, 0x02]
      - [0xC2, 0x31, 0x05]
      - [0xB0, 0x00, 0x11, 0x18, 0x0E, 0x11, 0x06, 0x07, 0x08, 0x07, 0x22, 0x04, 0x12, 0x0F, 0xAA, 0x31, 0x18]
      - [0xB1, 0x00, 0x11, 0x19, 0x0E, 0x12, 0x07, 0x08, 0x08, 0x08, 0x22, 0x04, 0x11, 0x11, 0xA9, 0x32, 0x18]
      - [0xFF, 0x77, 0x01, 0x00, 0x00, 0x11]
      - [0xB0, 0x60]
      - [0xB1, 0x32]
      - [0xB2, 0x07]
      - [0xB3, 0x80]
      - [0xB5, 0x49]
      - [0xB7, 0x85]
      - [0xB8, 0x21]
      - [0xC1, 0x78]
      - [0xC2, 0x78]
      - [0xE0, 0x00, 0x1B, 0x02]
      - [0xE1, 0x08, 0xA0, 0x00, 0x00, 0x07, 0xA0, 0x00, 0x00, 0x00, 0x44, 0x44]
      - [0xE2, 0x11, 0x11, 0x44, 0x44, 0xED, 0xA0, 0x00, 0x00, 0xEC, 0xA0, 0x00, 0x00]
      - [0xE3, 0x00, 0x00, 0x11, 0x11]
      - [0xE4, 0x44, 0x44]
      - [0xE5, 0x0A, 0xE9, 0xD8, 0xA0, 0x0C, 0xEB, 0xD8, 0xA0, 0x0E, 0xED, 0xD8, 0xA0, 0x10, 0xEF, 0xD8, 0xA0]
      - [0xE6, 0x00, 0x00, 0x11, 0x11]
      - [0xE7, 0x44, 0x44]
      - [0xE8, 0x09, 0xE8, 0xD8, 0xA0, 0x0B, 0xEA, 0xD8, 0xA0, 0x0D, 0xEC, 0xD8, 0xA0, 0x0F, 0xEE, 0xD8, 0xA0]
      - [0xEB, 0x02, 0x00, 0xE4, 0xE4, 0x88, 0x00, 0x40]
      - [0xEC, 0x3C, 0x00]
      - [0xED, 0xAB, 0x89, 0x76, 0x54, 0x02, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x20, 0x45, 0x67, 0x98, 0xBA]
      - [0xFF, 0x77, 0x01, 0x00, 0x00, 0x13]
      - [0xE5, 0xE4]
      - [0xFF, 0x77, 0x01, 0x00, 0x00, 0x10]
      - [0xCD, 0x08]
      - [0xCD, 0x00]

# ----------------------------------------------------------------------------
# Автовозврат на «Главную»: раз в 5 с смотрим, сколько LVGL не трогали.
# Если дольше, чем выбрано в «Возврат на главную», и открыт не главный экран —
# показываем его. «Выкл» — не возвращаемся.
# Сделано через interval, а не через lvgl on_idle: on_idle отвечает за
# гашение по таймауту (блок яркости).
# Касание любого места экрана сбрасывает отсчёт; обновления из HA — нет.
# ----------------------------------------------------------------------------
interval:
  - interval: 5s
    then:
      - if:
          condition:
            lambda: |-
              auto o = id(cfg_home_return).current_option();
              uint32_t sec = (o == "1 мин") ? 60 : (o == "2 мин") ? 120 : (o == "5 мин") ? 300 : 0;
              if (sec == 0) return false;
              return lv_scr_act() != id(main_page)->obj &&
                     lv_display_get_inactive_time(NULL) > sec * 1000UL;
          then:
            - lvgl.page.show: main_page
''', 0)
w()

# ==========================================================================
# СКРИПТЫ
block(r'''
# ----------------------------------------------------------------------------
# time_update — вызывается раз в минуту (time: on_time) и после синхронизации.
# Дата по-русски, как в макете: "сб, 10 октября".
# ----------------------------------------------------------------------------
script:
  - id: time_update
    then:
      - lvgl.label.update:
          id: lbl_clock
          text: !lambda |-
            auto t = id(system_time).now();
            if (!t.is_valid()) return std::string("--:--");
            return t.strftime("%H:%M");
      - lvgl.label.update:
          id: lbl_date
          text: !lambda |-
            static const char *const dows[] = {"вс", "пн", "вт", "ср", "чт", "пт", "сб"};
            static const char *const months[] = {"января", "февраля", "марта", "апреля", "мая", "июня",
                                                 "июля", "августа", "сентября", "октября", "ноября", "декабря"};
            auto t = id(system_time).now();
            if (!t.is_valid()) return std::string("");
            return str_sprintf("%s, %d %s", dows[(t.day_of_week + 6) % 7], t.day_of_month, months[(t.month + 11) % 12]);

  # Включить подсветку с яркостью текущего режима (Day / Night).
  # Вызывается: при включении экрана (HA или касание после паузы) и при смене
  # режима, если экран горит.
  - id: apply_brightness_mode
    mode: restart
    then:
      - if:
          condition:
            lambda: 'return id(brightness_mode).current_option() == "Day";'
          then:
            - light.turn_on:
                id: display_backlight
                brightness: !lambda return id(cfg_day_brightness).state / 100.0f;
          else:
            - light.turn_on:
                id: display_backlight
                brightness: !lambda return id(cfg_night_brightness).state / 100.0f;

  # Кнопки быстрого запуска музыки: пока Music Assistant стартует (1–5 с,
  # плейлистам Яндекса бывает нужно больше), в шапке «Играет» пишем «Запускаю…»,
  # а вместо трека — что нажали. Придут новые данные из HA — они это заменят;
  # если за 20 с ничего не пришло (сбой), возвращаем то, что сейчас в HA.
  - id: preset_feedback
    mode: restart
    parameters:
      name: string
    then:
      - lvgl.label.update:
          id: lbl_music_state
          text: "Запускаю…"
      - lvgl.label.update:
          id: lbl_music_title
          text:
            format: "%s"
            args: ['name.c_str()']
      - delay: 20s
      # вернуть то, что сейчас в HA (если новое название так и не пришло)
      - lvgl.label.update:
          id: lbl_music_state
          text: !lambda |-
            auto x = id(ha_sarai_play_state).state;
            if (x == "playing") return std::string("Играет · Сарай");
            if (x == "paused") return std::string("Пауза · Сарай");
            return std::string("Не играет · Сарай");
      - lvgl.label.update:
          id: lbl_music_title
          text: !lambda |-
            auto t = id(ha_sarai_media_title).state;
            return t.empty() ? std::string("—") : t;

  # После загрузки (первая синхронизация времени): режим по текущей высоте солнца
  - id: set_brightness_mode_on_boot
    then:
      - select.set:
          id: brightness_mode
          option: !lambda |-
            return std::string(id(sun_sun).elevation() < ${night_sun_elevation} ? "Night" : "Day");
''', 0)


# ---------- группы-переключатели экрана «Настройки» ----------
# gid: [(подпись, иконка|None, действие YAML, условие «выбрано» на C++)]
SEGS = {
    "mode": [
        ("День", "weather_sunny", 'select.set:\n    id: brightness_mode\n    option: "Day"',
         'id(brightness_mode).current_option() == "Day"'),
        ("Ночь", "weather_night", 'select.set:\n    id: brightness_mode\n    option: "Night"',
         'id(brightness_mode).current_option() != "Day"'),
    ],
    "home_return": [(t, None, f'select.set:\n    id: cfg_home_return\n    option: "{t}"',
                     f'id(cfg_home_return).current_option() == "{t}"')
                    for t in ["1 мин", "2 мин", "5 мин", "Выкл"]],
    "screen_off": [(f"{m} мин", None, f'number.set:\n    id: cfg_screen_off\n    value: {m}',
                    f'(int) id(cfg_screen_off).state == {m}')
                   for m in [5, 10, 15, 30]],
}
SEG_SCRIPT_ID = {"mode": "settings_show_mode", "home_return": "settings_show_home_return",
                 "screen_off": "settings_show_screen_off"}

# скрипты: подсветить выбранный вариант в группе (кнопка «вдавлена» и залита
# серо-синим, подпись и иконка белые; остальные — обычные клавиши)
w()
for gid, opts in SEGS.items():
    w(f"  - id: {SEG_SCRIPT_ID[gid]}")
    w("    then:")
    w("      - lambda: |-")
    for i, (lab, glyph, act, cond) in enumerate(opts):
        w(f"          {{")
        w(f"            bool on = {cond};")
        w(f"            lv_obj_t *b = id(seg_{gid}_{i});")
        w(f"            if (on) lv_obj_add_state(b, LV_STATE_CHECKED); else lv_obj_clear_state(b, LV_STATE_CHECKED);")
        w(f"            lv_obj_set_style_text_color(id(lbl_seg_{gid}_{i}), on ? lv_color_hex(0xFFFFFF) : lv_color_hex(0x212121), 0);")
        if glyph:
            off = "0xF37320" if glyph == "weather_sunny" else "0x606682"
            w(f"            lv_obj_set_style_text_color(id(icon_seg_{gid}_{i}), on ? lv_color_hex(0xFFFFFF) : lv_color_hex({off}), 0);")
        w(f"          }}")
w()
# всё сразу — после загрузки
block(r'''
- id: settings_refresh
  then:
    - lvgl.slider.update:
        id: slider_cfg_day
        value: !lambda return id(cfg_day_brightness).state;
    - lvgl.label.update:
        id: lbl_cfg_day
        text: !lambda return str_sprintf("%d%%", (int) id(cfg_day_brightness).state);
    - lvgl.slider.update:
        id: slider_cfg_night
        value: !lambda return id(cfg_night_brightness).state;
    - lvgl.label.update:
        id: lbl_cfg_night
        text: !lambda return str_sprintf("%d%%", (int) id(cfg_night_brightness).state);
    - script.execute: settings_show_mode
    - script.execute: settings_show_home_return
    - script.execute: settings_show_screen_off
''', 2)
w()

# свет во дворе: key, подпись, entity
YARD = [
    ("y_sredniy",   "Свет средний",   "light.bania_troitskaya_banya_banya_relay3"),
    ("y_osnovnye",  "Свет основные",  "light.bania_troitskaya_banya_banya_relay4"),
    ("y_krylco",    "Крыльцо",        "light.khata_hata_2025_relay_light_3"),
    ("y_kalitka",   "Калитка",        "light.bania_troitskaya_banya_banya_relay5"),
    ("y_torec",     "Торец",          "light.khata_hata_2025_relay_light_1"),
    ("y_valya",     "Валя",           "light.khata_hata_2025_relay_light_4"),
    ("y_ploshadka", "Площадка",       "light.troitskaya_banya_banya_relay2"),
    ("y_veranda",   "Веранда",        "light.bania_troitskaya_banya_banya_relay1"),
    ("y_tualet_in", "Туалет внутри",  "light.tualet_troitskaya_toilet_toilet_relay1"),
    ("y_tualet_out","Туалет снаружи", "light.tualet_troitskaya_toilet_toilet_relay2"),
]
w()
w()

# ==========================================================================
# SENSORS
block(r'''
# ----------------------------------------------------------------------------
# Числовые сенсоры из HA. ВЕЗДЕ проверка isnan(x): у выключенного
# плеера/ленты атрибут пропадает, и (int)NaN даёт мусор вроде 2147483647.
# ----------------------------------------------------------------------------
sensor:
  # Температура в парной (большая цифра на главной)
  - platform: homeassistant
    id: ha_sauna_temp
    entity_id: sensor.troitskaya_banya_banya_temperature
    on_value:
      - lvgl.label.update:
          id: lbl_sauna_temp
          text: !lambda |-
            if (isnan(x)) return std::string("--°");
            return str_sprintf("%d°", (int) lroundf(x));

  # Улица: своя подписка (а не подписи погодного пакета) — нужен формат
  # макета: целые градусы "23°" и "46%".
  - platform: homeassistant
    id: ha_out_temp
    entity_id: weather.forecast_troitskaia
    attribute: temperature
    on_value:
      - lvgl.label.update:
          id: lbl_out_temp
          text: !lambda |-
            if (isnan(x)) return std::string("--°");
            return str_sprintf("%d°", (int) lroundf(x));

  - platform: homeassistant
    id: ha_out_hum
    entity_id: weather.forecast_troitskaia
    attribute: humidity
    on_value:
      - lvgl.label.update:
          id: lbl_out_hum
          text: !lambda |-
            if (isnan(x)) return std::string("--%");
            return str_sprintf("%d%%", (int) lroundf(x));

  # Громкость плеера (0.0–1.0) -> оба слайдера (главная + музыка) и их "50%"
  - platform: homeassistant
    id: ha_sarai_volume
    entity_id: media_player.sarai
    attribute: volume_level
    on_value:
      - lvgl.slider.update:
          id: slider_volume
          value: !lambda |-
            if (isnan(x)) return 0;
            return (int) lroundf(x * 100);
      - lvgl.label.update:
          id: lbl_volume_pct
          text: !lambda |-
            int p = isnan(x) ? 0 : (int) lroundf(x * 100);
            return str_sprintf("%d%%", p);
      - lvgl.slider.update:
          id: slider_mini_volume
          value: !lambda |-
            if (isnan(x)) return 0;
            return (int) lroundf(x * 100);
      - lvgl.label.update:
          id: lbl_mini_volume_pct
          text: !lambda |-
            int p = isnan(x) ? 0 : (int) lroundf(x * 100);
            return str_sprintf("%d%%", p);

''', 0)
w()

# ==========================================================================
# BINARY SENSORS — свет
LIGHTS = [
    # key, label, entity, icon_on, icon_off
    ("naves",   "Навес",   "light.sarai_troitskaya_saray_relay_light_1", "lightbulb", "lightbulb_outline"),
    ("vnutri",  "Внутри",  "light.sarai_troitskaya_saray_relay_light_3", "lightbulb", "lightbulb_outline"),
    ("verstak", "Верстак", "light.sarai_troitskaya_saray_relay_light_4", "lightbulb", "lightbulb_outline"),
    ("mangal",  "Мангал",  "light.sarai_troitskaya_saray_relay_light_2", "lightbulb", "lightbulb_outline"),
    ("drovnik", "Дровник", "light.sarai_troitskaya_saray_relay_light_5", "lightbulb", "lightbulb_outline"),
    ("led",     "Лента",   "light.troitskaya_saray_led_saray",           "led_strip_variant", "led_strip_variant"),
]

w("# ----------------------------------------------------------------------------")
w("# Состояние света -> вид плиток. ВКЛ: светло-оранжевая плитка с оранжевой")
w("# рамкой и губой (state checked), лампа залита, тумблер вправо, \"ВКЛ\" жирным.")
w("# ВЫКЛ: серая плитка-клавиша, лампа контуром, тумблер влево, \"выкл\".")
w("# Нажатие на плитку шлёт light.toggle; эти сенсоры только рисуют состояние.")
w("# ----------------------------------------------------------------------------")
w("binary_sensor:")
def light_bs(key, ent, ion, ioff, kon, koff, count_script=None):
    """kon/koff = (x, y, size) ручки тумблера во вкл/выкл."""
    w("  - platform: homeassistant")
    w(f"    id: ha_{key}_state")
    w(f"    entity_id: {ent}")
    w("    # без этого on_state не срабатывает на ПЕРВОЕ состояние после загрузки —")
    w("    # плитки показывали бы «выкл», пока свет не переключат")
    w("    trigger_on_initial_state: true")
    w("    on_state:")
    block(f'''
- lvgl.widget.update:
    id: tile_{key}
    state:
      checked: !lambda return x;
- lvgl.label.update:
    id: icon_{key}
    text: !lambda |-
      return std::string(x ? "$mdi_{ion}" : "$mdi_{ioff}");
    text_color: !lambda |-
      return x ? Color(0xF3, 0x73, 0x20) : Color(0x60, 0x66, 0x82);
- lvgl.obj.update:
    id: sw_{key}
    bg_color: !lambda |-
      return x ? Color(0xF3, 0x73, 0x20) : Color(0xE3, 0xE5, 0xEC);
    border_width: !lambda return x ? 0 : 2;
- lvgl.obj.update:
    id: knob_{key}
    x: !lambda return x ? {kon[0]} : {koff[0]};
    y: !lambda return x ? {kon[1]} : {koff[1]};
    width: !lambda return x ? {kon[2]} : {koff[2]};
    height: !lambda return x ? {kon[2]} : {koff[2]};
    shadow_opa: !lambda return x ? 0 : 64;
- if:
    condition:
      lambda: return x;
    then:
      - lvgl.label.update:
          id: state_{key}
          text: "ВКЛ"
          text_font: nb_16
          text_color: {C["orange_dk"]}
    else:
      - lvgl.label.update:
          id: state_{key}
          text: "выкл"
          text_font: nunito_16
          text_color: {C["mut"]}
''', 6)
    if key == "led":
        block(r'''
# Полоска яркости: оранжевая, когда лента горит, серая — когда выключена
- lvgl.slider.update:
    id: slider_led_brightness
    indicator:
      bg_color: !lambda |-
        return x ? Color(0xF3, 0x73, 0x20) : Color(0xC7, 0xCC, 0xDE);
''', 6)
    if count_script:
        w(f"      - script.execute: {count_script}")
    w()

for key, label, ent, ion, ioff in LIGHTS:
    light_bs(key, ent, ion, ioff, (23, 3, 22), (2, 2, 20))
for key, label, ent in YARD:
    light_bs(key, ent, "lightbulb", "lightbulb_outline", (21, 3, 16), (2, 2, 14))

# ==========================================================================
# LVGL
w("# ----------------------------------------------------------------------------")
w("# Экраны. Всё позиционируется абсолютно, как в макете (x/y от левого верхнего")
w("# угла родителя, внутри его рамки). pad_all: 0 у всех контейнеров и кнопок —")
w("# у кнопок библиотечной темы по умолчанию pad_all: 10.")
w("# ----------------------------------------------------------------------------")
w("lvgl:")
block(r'''
# Гашение по таймауту бездействия (number «Backlight timeout», мин; −1 = никогда).
# Сейчас экраном управляет HA, таймаут в HA стоит −1 — блок спит.
on_idle:
  timeout: !lambda return (uint32_t)(id(display_backlight_timeout).state * 60000);
  then:
    - if:
        condition:
          lambda: 'return id(display_backlight_timeout).state > 0;'
        then:
          - light.turn_off: display_backlight
# Касание тёмного (приостановленного) экрана: будим и включаем подсветку
on_resume:
  then:
    - script.execute: apply_brightness_mode
''', 2)
block(f'''
gradients:
  # подложка клавиш (текущая, как у плиток света)
  - id: tile_card_gradient
    direction: ver
    stops:
      - color: 0xF7F7FB
        position: 0
      - color: 0xE8EBF4
        position: 255
  # включённая плитка — сплошной светло-оранжевый (градиент из одного цвета,
  # чтобы в состоянии checked просто подменить подложку)
  - id: tile_on_gradient
    direction: ver
    stops:
      - color: {C["tint_or"]}
        position: 0
      - color: {C["tint_or"]}
        position: 255
  # выбранный вариант в группе на экране «Настройки» — сплошной серо-синий
  - id: seg_on_gradient
    direction: ver
    stops:
      - color: {C["mut"]}
        position: 0
      - color: {C["mut"]}
        position: 255
  # оранжевая клавиша (пауза) — сплошной оранжевый
  - id: orange_gradient
    direction: ver
    stops:
      - color: {C["orange"]}
        position: 0
      - color: {C["orange"]}
        position: 255
  # карточка «сейчас играет»: от оранжевого тона к серому, слева направо
  - id: music_card_gradient
    direction: hor
    stops:
      - color: {C["tint_or"]}
        position: 0
      - color: {C["card"]}
        position: 255

style_definitions:
  - id: !extend page_style
    bg_color: white
    bg_opa: COVER
    pad_all: 0

  # показание: плоская светлая карточка без рамки, тени и губы
  - id: card_style
    bg_color: {C["card"]}
    bg_opa: COVER
    radius: 22
    border_width: 0
    shadow_width: 0
    pad_all: 0

  # клавиша: подложка-градиент, рамка 2px, губа 4px (жёсткая тень снизу)
  - id: key_style
    bg_grad: tile_card_gradient
    bg_opa: COVER
    border_width: 2
    border_color: {C["border"]}
    radius: 22
    pad_all: 0
    shadow_width: 1
    shadow_spread: 0
    shadow_offset_x: 0
    shadow_offset_y: 4
    shadow_color: {C["lip"]}
    shadow_opa: COVER

  # «вдавливание» при нажатии: кнопка опускается на губу
  - id: key_pressed_style
    translate_y: 4
    shadow_offset_y: 0

  # оранжевая клавиша (пауза)
  - id: key_orange_style
    bg_grad: orange_gradient
    border_color: {C["orange"]}
    shadow_color: {C["lip_or"]}

  # активная вкладка: залита серо-синим, без губы, опущена на 4 px
  - id: tab_on_style
    bg_color: {C["mut"]}
    bg_opa: COVER
    border_width: 2
    border_color: {C["mut"]}
    radius: 20
    pad_all: 0
    shadow_width: 0
''', 2)
w()
w("  pages:")

# ---------- helpers for widgets ----------
def lbl(ind, x, y, text, font, color, extra=None, id_=None):
    s = " " * ind
    w(f"{s}- label:")
    if id_:
        w(f"{s}    id: {id_}")
    w(f"{s}    x: {x}")
    w(f"{s}    y: {y}")
    w(f'{s}    text: "{text}"')
    w(f"{s}    text_font: {font}")
    w(f"{s}    text_color: {color}")
    for k, v in (extra or {}).items():
        w(f"{s}    {k}: {v}")

def icon(ind, x, y, glyph, font, color, id_=None):
    s = " " * ind
    w(f"{s}- label:")
    if id_:
        w(f"{s}    id: {id_}")
    w(f"{s}    x: {x}")
    w(f"{s}    y: {y}")
    w(f"{s}    text: $mdi_{glyph}")
    w(f"{s}    text_font: {font}")
    w(f"{s}    text_color: {color}")

def card(ind, x, y, wd, h, bg=None, id_=None, grad=None):
    s = " " * ind
    w(f"{s}- obj:")
    if id_:
        w(f"{s}    id: {id_}")
    w(f"{s}    x: {x}")
    w(f"{s}    y: {y}")
    w(f"{s}    width: {wd}")
    w(f"{s}    height: {h}")
    w(f"{s}    styles: card_style")
    if bg:
        w(f"{s}    bg_color: {bg}")
    if grad:
        w(f"{s}    bg_grad: {grad}")
    w(f"{s}    widgets:")

def key(ind, x, y, wd, h_css, id_=None, lip=4, radius=None, orange=False, extra=None):
    """CSS-высота h_css включает губу (6px низ = 2 рамка + 4 губа)."""
    s = " " * ind
    w(f"{s}- button:")
    if id_:
        w(f"{s}    id: {id_}")
    w(f"{s}    x: {x}")
    w(f"{s}    y: {y}")
    w(f"{s}    width: {wd}")
    w(f"{s}    height: {h_css - lip}")
    w(f"{s}    styles: [key_style" + (", key_orange_style" if orange else "") + "]")
    if lip != 4:
        w(f"{s}    shadow_offset_y: {lip}")
    if radius:
        w(f"{s}    radius: {radius}")
    w(f"{s}    pressed:")
    w(f"{s}      translate_y: {lip}")
    w(f"{s}      shadow_offset_y: 0")
    for k, v in (extra or {}).items():
        w(f"{s}    {k}: {v}")

def ha_action(ind, service, data):
    s = " " * ind
    w(f"{s}- homeassistant.service:")
    w(f"{s}    service: {service}")
    w(f"{s}    data:")
    for k, v in data.items():
        w(f"{s}      {k}: {v}")

TABS = [("main_page", "Главная", "home"), ("light_page", "Сарай", "lightbulb"),
        ("yard_page", "Двор", "post_lamp"), ("music_page", "Музыка", "music")]
TAB_X = [12, 128, 244, 360]   # 4 вкладки по 108 px, зазор 8
TAB_W = 108
TAB_ICON_OFF = {"home": C["mut"], "lightbulb": C["orange"], "post_lamp": C["orange"], "music": C["orange"]}

def tabbar(ind, active):
    s = " " * ind
    w(f"{s}# ===== Таб-бар: иконка + подпись всегда, активная вкладка вдавлена =====")
    for (page, title, glyph), x in zip(TABS, TAB_X):
        on = page == active
        w(f"{s}- button:")
        w(f"{s}    x: {x}")
        if on:
            w(f"{s}    y: 404")
            w(f"{s}    width: {TAB_W}")
            w(f"{s}    height: 64")
            w(f"{s}    styles: tab_on_style")
        else:
            w(f"{s}    y: 400")
            w(f"{s}    width: {TAB_W}")
            w(f"{s}    height: 64")
            w(f"{s}    styles: key_style")
            w(f"{s}    radius: 20")
            w(f"{s}    pressed:")
            w(f"{s}      translate_y: 4")
            w(f"{s}      shadow_offset_y: 0")
        w(f"{s}    layout:")
        w(f"{s}      type: flex")
        w(f"{s}      flex_flow: COLUMN")
        w(f"{s}      flex_align_main: CENTER")
        w(f"{s}      flex_align_cross: CENTER")
        w(f"{s}      flex_align_track: CENTER")
        w(f"{s}      pad_row: 2")
        w(f"{s}    widgets:")
        col_i = C["white"] if on else TAB_ICON_OFF[glyph]
        col_t = C["white"] if on else C["text"]
        w(f"{s}      - label:")
        w(f"{s}          text: $mdi_{glyph}")
        w(f"{s}          text_font: mdi_26")
        w(f"{s}          text_color: {col_i}")
        w(f"{s}      - label:")
        w(f'{s}          text: "{title}"')
        w(f"{s}          text_font: nunito_17")
        w(f"{s}          text_color: {col_t}")
        if not on:
            w(f"{s}    on_click:")
            w(f"{s}      - lvgl.page.show: {page}")

def page_head(pid, title):
    w(f"    # {'=' * 70}")
    w(f"    # {title}")
    w(f"    # {'=' * 70}")
    w(f"    - id: {pid}")
    w("      styles: page_style")
    w("      bg_color: white")
    w("      bg_opa: COVER")
    w("      pad_all: 0")
    w("      <<: !include esphome-modular-lvgl-buttons/common/swipe_navigation.yaml")
    w("      widgets:")

# ======================= MAIN PAGE =========================================
page_head("main_page", "1. ГЛАВНАЯ")
I = 8   # отступ элементов списка widgets страницы
w(" " * I + "# ===== Ряд A: время | улица =====")
card(I, 12, 12, 228, 116)
J = I + 6
lbl(J, 18, ty(14, 56, 48), "--:--", "nb_48", C["text"], id_="lbl_clock")
lbl(J, 20, ty(78, 22, 18), "", "nunito_18", C["mut"], id_="lbl_date")

card(I, 252, 12, 216, 116)
icon(J, 14, 16, "weather_partly_cloudy", "mdi_46", C["orange"], id_="icon_weather")
lbl(J, 72, ty(14, 52, 44), "--°", "nb_44", C["text"], id_="lbl_out_temp")
# (капля и влажность сдвинуты на 14px вправо от макета — чтобы влезло «малооблачно»)
lbl(J, 16, ty(78, 22, 18), "", "nunito_18", C["mut"], id_="lbl_weather_cond",
    extra={"width": 118, "long_mode": "DOT", "height": 25})
icon(J, 136, 79, "water", "mdi_20", C["blue"])
lbl(J, 158, ty(78, 22, 18), "--%", "nunito_18", C["text"], id_="lbl_out_hum")

# скрытые обязательные виджеты библиотечных пакетов
s = " " * I
w(s + "# Скрытый контейнер: виджеты, которые библиотечные пакеты (погода,")
w(s + "# диагностика sensors_base) обновляют по id. Без них сборка падает с")
w(s + "# \"ID not found\"; на экране они не нужны — скрыты целиком.")
w(s + "- obj:")
w(s + "    x: 0")
w(s + "    y: 0")
w(s + "    width: 1")
w(s + "    height: 1")
w(s + "    hidden: true")
w(s + "    widgets:")
w(s + "      - image:")
w(s + "          id: weather_condition_icon")
w(s + "          src: unknown_16")
for pid in ["weather_temperature_today", "weather_humidity_today", "weather_summary_today",
            "weather_wind_speed_today", "weather_wind_dir_today", "weather_pressure_today",
            "weather_visibility_today", "esphome_version_label",
            "connected_mac_label", "device_name_label"]:
    w(s + "      - label:")
    w(s + f"          id: {pid}")
    w(s + '          text: ""')
w(s + "      - qrcode:")
w(s + "          id: cp_login")
w(s + "          size: 10")
w(s + '          text: " "')

w()
w(" " * I + "# ===== Ряд B: парная (главная плашка) | баня + туалет =====")
card(I, 12, 140, 228, 150, bg=C["parn_bg"])
icon(J, 14, 14, "thermometer", "mdi_24", C["orange"])
lbl(J, 42, ty(16, 20, 16), "ПАРНАЯ", "nb_16", C["orange_dk"])
lbl(J, 14, ty(38, 68, 64), "--°", "nb_64", C["text"], id_="lbl_sauna_temp")
# пилюля тренда: ширина по содержимому (слово меняется)
s = " " * J
w(s + "# тренд: стрелка + слово, белая пилюля, ширина по содержимому")
w(s + "- obj:")
w(s + "    id: pill_trend")
w(s + "    x: 14")
w(s + "    y: 110")
w(s + "    width: SIZE_CONTENT")
w(s + "    height: 28")
w(s + "    radius: 14")
w(s + f"    bg_color: {C['white']}")
w(s + "    bg_opa: COVER")
w(s + "    border_width: 0")
w(s + "    pad_left: 8")
w(s + "    pad_right: 12")
w(s + "    pad_top: 0")
w(s + "    pad_bottom: 0")
w(s + "    layout:")
w(s + "      type: flex")
w(s + "      flex_flow: ROW")
w(s + "      flex_align_main: START")
w(s + "      flex_align_cross: CENTER")
w(s + "      flex_align_track: CENTER")
w(s + "      pad_column: 6")
w(s + "    widgets:")
w(s + "      - label:")
w(s + "          id: icon_trend")
w(s + "          text: $mdi_trending_neutral")
w(s + "          text_font: mdi_20")
w(s + f"          text_color: {C['mut']}")
w(s + "      - label:")
w(s + "          id: lbl_trend")
w(s + '          text: "стабильно"')
w(s + "          text_font: nunito_16")
w(s + f"          text_color: {C['mut']}")

for cid, ttl, glyph, yy, lid, iid in [("obj_banya_chip", "Баня", "pot_steam", 140, "lbl_banya_status", "icon_banya"),
                                      ("obj_toilet_chip", "Туалет", "toilet", 221, "lbl_toilet_status", "icon_toilet")]:
    card(I, 252, yy, 216, 69, bg=C["free_bg"], id_=cid)
    icon(J, 14, 20, glyph, "mdi_28", C["free_ic"], id_=iid)
    lbl(J, 54, ty(9, 20, 16), ttl, "nunito_16", C["mut"])
    lbl(J, 54, ty(31, 26, 20), "--", "nunito_20", C["free_tx"], id_=lid)

w()
w(" " * I + "# ===== Ряд C: мини-плеер на всю ширину: трек + громкость | пауза =====")
card(I, 12, 302, 456, 86, grad="music_card_gradient")
icon(J, 16, 15, "equalizer", "mdi_16", C["orange"])
s = " " * J
w(s + "# верхняя строка: «Играет ·» (мелко, оранжевым) + название трека (обрезается …)")
w(s + "- obj:")
w(s + "    x: 38")
w(s + "    y: 8")
w(s + "    width: 326")
w(s + "    height: 26")
w(s + "    bg_opa: TRANSP")
w(s + "    border_width: 0")
w(s + "    pad_all: 0")
w(s + "    clickable: false")
w(s + "    scrollable: false")
w(s + "    layout:")
w(s + "      type: flex")
w(s + "      flex_flow: ROW")
w(s + "      flex_align_main: START")
w(s + "      flex_align_cross: CENTER")
w(s + "      flex_align_track: CENTER")
w(s + "      pad_column: 5")
w(s + "    widgets:")
w(s + "      - label:")
w(s + "          id: lbl_mini_state")
w(s + '          text: "Играет ·"')
w(s + "          text_font: nunito_16")
w(s + f"          text_color: {C['orange_dk']}")
w(s + "      - label:")
w(s + "          id: lbl_mini_title")
w(s + '          text: "—"')
w(s + "          text_font: nunito_19")
w(s + f"          text_color: {C['text']}")
w(s + "          width: 10")
w(s + "          flex_grow: 1")
w(s + "          long_mode: DOT")
icon(J, 14, 46, "volume_medium", "mdi_24", C["mut"])
block(f"""
# громкость прямо на главной: дорожка 20px, ручка 32px (pad 6)
- slider:
    id: slider_mini_volume
    x: 58
    y: 48
    width: 234
    height: 20
    min_value: 0
    max_value: 100
    value: 0
    radius: 10
    bg_color: {C["track"]}
    bg_opa: COVER
    pad_all: 0
    indicator:
      bg_color: {C["orange"]}
      bg_opa: COVER
      radius: 10
    knob:
      bg_color: {C["white"]}
      bg_opa: COVER
      border_width: 4
      border_color: {C["mut"]}
      radius: 16
      pad_all: 6
      shadow_width: 0
    on_value:
      - lvgl.label.update:
          id: lbl_mini_volume_pct
          text: !lambda return str_sprintf("%d%%", (int) x);
    on_release:
      - homeassistant.service:
          service: media_player.volume_set
          data:
            entity_id: media_player.sarai
            volume_level: !lambda return to_string(x / 100.0f);
""", J)
# ручка (32px) на краях вылезает за дорожку на 16px — дорожка отодвинута от
# значка и от "100%", чтобы ручка их не перекрывала
lbl(J, 312, ty(44, 28, 20), "0%", "nb_20", C["text"], id_="lbl_mini_volume_pct",
    extra={"width": 54, "text_align": "RIGHT"})
key(J, 380, 10, 64, 66, id_="btn_mini_playpause", radius=20, orange=True)
w(s + "    widgets:")
w(s + "      - label:")
w(s + "          id: icon_mini_playpause")
w(s + "          align: CENTER")
w(s + "          text: $mdi_play")
w(s + "          text_font: mdi_30")
w(s + f"          text_color: {C['white']}")
w(s + "    on_click:")
ha_action(J + 6, "media_player.media_play_pause", {"entity_id": "media_player.sarai"})

w()
tabbar(I, "main_page")
w()

# ======================= LIGHT PAGE ========================================
page_head("light_page", "2. СВЕТ В САРАЕ")
TILES = [  # key, x, y, w, h_css, sw_x, icon_y, sw_y, name_top, state_top
    ("naves",   12, 12, 144, 116, 80, 10, 12, 54, 80),
    ("vnutri",  168, 12, 144, 116, 80, 10, 12, 54, 80),
    ("verstak", 324, 12, 144, 116, 80, 10, 12, 54, 80),
    ("mangal",  12, 140, 222, 116, 158, 10, 12, 54, 80),
    ("drovnik", 246, 140, 222, 116, 158, 10, 12, 54, 80),
    ("led",     12, 268, 144, 120, 80, 12, 14, 58, 84),
]
names = {k: n for k, n, *_ in LIGHTS}
ents = {k: e for k, _, e, *_ in LIGHTS}
offg = {k: g for k, _, _, _, g in LIGHTS}
for k, x, y, wd, hc, swx, iy, swy, nt, st in TILES:
    w(" " * I + f"# --- {names[k]} ---")
    key(I, x, y, wd, hc, id_=f"tile_{k}")
    s = " " * I
    # стиль включённого состояния
    w(s + "    checked:")
    w(s + "      bg_grad: tile_on_gradient")
    w(s + f"      bg_color: {C['tint_or']}")
    w(s + f"      border_color: {C['orange']}")
    w(s + f"      shadow_color: {C['lip_or']}")
    w(s + "    widgets:")
    icon(I + 6, 10, iy, offg[k], "mdi_34", C["mut"], id_=f"icon_{k}")
    # тумблер
    t = " " * (I + 6)
    w(t + "- obj:")
    w(t + f"    id: sw_{k}")
    w(t + f"    x: {swx}")
    w(t + f"    y: {swy}")
    w(t + "    width: 48")
    w(t + "    height: 28")
    w(t + "    radius: 14")
    w(t + f"    bg_color: {C['track']}")
    w(t + "    bg_opa: COVER")
    w(t + "    border_width: 2")
    w(t + f"    border_color: {C['border']}")
    w(t + "    pad_all: 0")
    w(t + "    clickable: false")
    w(t + "    widgets:")
    w(t + "      - obj:")
    w(t + f"          id: knob_{k}")
    w(t + "          x: 2")
    w(t + "          y: 2")
    w(t + "          width: 20")
    w(t + "          height: 20")
    w(t + "          radius: 11")
    w(t + f"          bg_color: {C['white']}")
    w(t + "          bg_opa: COVER")
    w(t + "          border_width: 0")
    w(t + "          clickable: false")
    w(t + "          shadow_width: 2")
    w(t + "          shadow_offset_y: 1")
    w(t + "          shadow_color: 0x000000")
    w(t + "          shadow_opa: 25%")
    lbl(I + 6, 14, ty(nt, 24, 20), names[k], "nunito_20", C["text"])
    lbl(I + 6, 14, ty(st, 20, 16), "выкл", "nunito_16", C["mut"], id_=f"state_{k}")
    w(s + "    on_click:")
    ha_action(I + 6, "light.toggle", {"entity_id": ents[k]})
    w()

w(" " * I + "# --- Яркость ленты: плоская карточка-показание со слайдером ---")
card(I, 168, 268, 300, 120)
lbl(J, 18, ty(16, 22, 17), "Яркость ленты", "nunito_17", C["mut"])
lbl(J, 196, ty(8, 34, 28), "0%", "nb_28", C["text"], id_="lbl_led_pct",
    extra={"width": 88, "text_align": "RIGHT"})
s = " " * J
block(f'''
# дорожка 36px, ручка 48px (pad 6 вокруг высоты дорожки) — вся полоса ловит палец
- slider:
    id: slider_led_brightness
    x: 18
    y: 62
    width: 264
    height: 36
    min_value: 0
    max_value: 100
    value: 0
    radius: 18
    bg_color: {C["track"]}
    bg_opa: COVER
    pad_all: 0
    indicator:
      bg_color: {C["border"]}
      bg_opa: COVER
      radius: 18
    knob:
      bg_color: {C["white"]}
      bg_opa: COVER
      border_width: 4
      border_color: {C["mut"]}
      radius: 24
      pad_all: 6
      shadow_width: 0
    on_value:
      - lvgl.label.update:
          id: lbl_led_pct
          text: !lambda return str_sprintf("%d%%", (int) x);
    on_release:
      - homeassistant.service:
          service: light.turn_on
          data:
            entity_id: light.troitskaya_saray_led_saray
            brightness_pct: !lambda return to_string((int) x);
''', J)
w()
tabbar(I, "light_page")
w()

# ======================= YARD PAGE =========================================
page_head("yard_page", "3. СВЕТ ВО ДВОРЕ")
# без заголовка: где мы — видно по нажатой вкладке «Двор»; плитки на всю высоту
w(" " * I + "# ===== 10 плиток 222×70: 2 колонки × 5 рядов (зазор 6) =====")
YCOLS = [12, 246]
YROWS = [12, 88, 164, 241, 318]   # 5 рядов по 70: низ на 388, как у экрана «Сарай»
for i, (k, name, ent) in enumerate(YARD):
    x, y = YCOLS[i % 2], YROWS[i // 2]
    w(" " * I + f"# --- {name} ---")
    key(I, x, y, 222, 70, id_=f"tile_{k}", radius=20)
    s_ = " " * I
    w(s_ + "    checked:")
    w(s_ + "      bg_grad: tile_on_gradient")
    w(s_ + f"      bg_color: {C['tint_or']}")
    w(s_ + f"      border_color: {C['orange']}")
    w(s_ + f"      shadow_color: {C['lip_or']}")
    w(s_ + "    widgets:")
    icon(I + 6, 12, 16, "lightbulb_outline", "mdi_30", C["mut"], id_=f"icon_{k}")
    lbl(I + 6, 54, ty(8, 24, 20), name, "nunito_20", C["text"])
    lbl(I + 6, 54, ty(34, 20, 16), "выкл", "nunito_16", C["mut"], id_=f"state_{k}")
    t = " " * (I + 6)
    w(t + "- obj:")
    w(t + f"    id: sw_{k}")
    w(t + "    x: 164")
    w(t + "    y: 33")
    w(t + "    width: 40")
    w(t + "    height: 22")
    w(t + "    radius: 11")
    w(t + f"    bg_color: {C['track']}")
    w(t + "    bg_opa: COVER")
    w(t + "    border_width: 2")
    w(t + f"    border_color: {C['border']}")
    w(t + "    pad_all: 0")
    w(t + "    clickable: false")
    w(t + "    widgets:")
    w(t + "      - obj:")
    w(t + f"          id: knob_{k}")
    w(t + "          x: 2")
    w(t + "          y: 2")
    w(t + "          width: 14")
    w(t + "          height: 14")
    w(t + "          radius: 8")
    w(t + f"          bg_color: {C['white']}")
    w(t + "          bg_opa: COVER")
    w(t + "          border_width: 0")
    w(t + "          clickable: false")
    w(t + "          shadow_width: 2")
    w(t + "          shadow_offset_y: 1")
    w(t + "          shadow_color: 0x000000")
    w(t + "          shadow_opa: 25%")
    w(s_ + "    on_click:")
    ha_action(I + 6, "light.toggle", {"entity_id": ent})
    w()
tabbar(I, "yard_page")
w()

# ======================= MUSIC PAGE ========================================
page_head("music_page", "4. МУЗЫКА")
w(" " * I + "# ===== Сейчас играет (показание) =====")
card(I, 12, 12, 336, 88, grad="music_card_gradient")
icon(J, 18, 15, "equalizer", "mdi_16", C["orange"])
lbl(J, 40, ty(12, 20, 16), "Играет · Сарай", "nunito_16", C["orange_dk"], id_="lbl_music_state")
lbl(J, 18, ty(40, 32, 26), "—", "nb_26", C["text"], id_="lbl_music_title",
    extra={"width": 300, "height": 35, "long_mode": "DOT"})
w()
w(" " * I + "# ===== Вход в «Настройки» (только отсюда) — клавиша в сетке вкладки «Музыка» =====")
key(I, 360, 22, 108, 68, id_="btn_open_settings", radius=20)
s_ = " " * I
w(s_ + "    layout:")
w(s_ + "      type: flex")
w(s_ + "      flex_flow: COLUMN")
w(s_ + "      flex_align_main: CENTER")
w(s_ + "      flex_align_cross: CENTER")
w(s_ + "      flex_align_track: CENTER")
w(s_ + "      pad_row: 2")
w(s_ + "    widgets:")
w(s_ + "      - label:")
w(s_ + "          text: $mdi_cog")
w(s_ + "          text_font: mdi_26")
w(s_ + f"          text_color: {C['mut']}")
w(s_ + "      - label:")
w(s_ + '          text: "Настройки"')
w(s_ + "          text_font: nunito_17")
w(s_ + f"          text_color: {C['text']}")
w(s_ + "    on_click:")
w(s_ + "      - lvgl.page.show: settings_page")
w()
w(" " * I + "# ===== Транспорт (компактный): назад / пауза / вперёд =====")
for kid, x, glyph, svc in [("btn_prev", 76, "skip_previous", "media_player.media_previous_track"),
                           ("btn_next", 316, "skip_next", "media_player.media_next_track")]:
    key(I, x, 116, 88, 66, id_=kid)
    s = " " * I
    w(s + "    widgets:")
    w(s + "      - label:")
    w(s + "          align: CENTER")
    w(s + f"          text: $mdi_{glyph}")
    w(s + "          text_font: mdi_32")
    w(s + f"          text_color: {C['mut']}")
    w(s + "    on_click:")
    ha_action(I + 6, svc, {"entity_id": "media_player.sarai"})
# пауза: губа 8px низ = 2 рамка + 6 губа
key(I, 180, 112, 120, 74, id_="btn_music_playpause", lip=6, radius=24, orange=True)
s = " " * I
w(s + "    widgets:")
w(s + "      - label:")
w(s + "          id: icon_music_playpause")
w(s + "          align: CENTER")
w(s + "          text: $mdi_play")
w(s + "          text_font: mdi_40")
w(s + f"          text_color: {C['white']}")
w(s + "    on_click:")
ha_action(I + 6, "media_player.media_play_pause", {"entity_id": "media_player.sarai"})
w()
w(" " * I + "# ===== Громкость (компактная) =====")
card(I, 12, 198, 456, 58)
icon(J, 16, 16, "volume_high", "mdi_26", C["mut"])
block(f'''
- slider:
    id: slider_volume
    x: 58
    y: 17
    width: 300
    height: 24
    min_value: 0
    max_value: 100
    value: 0
    radius: 12
    bg_color: {C["track"]}
    bg_opa: COVER
    pad_all: 0
    indicator:
      bg_color: {C["orange"]}
      bg_opa: COVER
      radius: 12
    knob:
      bg_color: {C["white"]}
      bg_opa: COVER
      border_width: 4
      border_color: {C["mut"]}
      radius: 18
      pad_all: 6
      shadow_width: 0
    on_value:
      - lvgl.label.update:
          id: lbl_volume_pct
          text: !lambda return str_sprintf("%d%%", (int) x);
    on_release:
      - homeassistant.service:
          service: media_player.volume_set
          data:
            entity_id: media_player.sarai
            volume_level: !lambda return to_string(x / 100.0f);
''', J)
lbl(J, 366, ty(13, 32, 24), "0%", "nb_24", C["text"], id_="lbl_volume_pct",
    extra={"width": 74, "text_align": "RIGHT"})
w()
w(" " * I + "# ===== Быстрый запуск через Music Assistant: 2 радио (MA → Radio) + 2 плейлиста Яндекс Музыки =====")
w(" " * I + "# URI — из библиотеки Music Assistant (music_assistant.get_library). Добавишь станцию — допиши сюда.")
# Что именно запускать, решает скрипт HA script.sarai_muzyka_bystryi_zapusk
# (поле preset): там адреса Music Assistant, повтор при сбое и защита от
# повторных нажатий. Панель только передаёт, какую кнопку нажали.
PRESETS = [  # id, x, y, подпись, подпись-2, вид, preset
    ("btn_preset_rusradio", 12, 268, "Русское радио", "радио", "radio", "russkoe"),
    ("btn_preset_avtoradio", 246, 268, "Авторадио", "радио", "radio", "avto"),
    ("btn_preset_favorites", 12, 332, "Мне нравится", "Яндекс Музыка", "heart", "nravitsya"),
    ("btn_preset_mywave", 246, 332, "Моя волна", "Яндекс Музыка", "waveform", "volna"),
]
for kid, x, y, name, cap, kind, preset in PRESETS:
    w(" " * I + f"# --- {name} (preset {preset}) ---")
    key(I, x, y, 222, 56, id_=kid)
    s = " " * I
    w(s + "    widgets:")
    t = " " * (I + 6)
    if kind == "radio":
        icon(I + 6, 14, 10, "radio", "mdi_28", C["orange"])
        tx = 54
    else:
        # плейлист: белая иконка в оранжевом круге — «моя музыка», а не эфир
        w(t + "- obj:")
        w(t + "    x: 14")
        w(t + "    y: 7")
        w(t + "    width: 34")
        w(t + "    height: 34")
        w(t + "    radius: 17")
        w(t + f"    bg_color: {C['orange']}")
        w(t + "    bg_opa: COVER")
        w(t + "    border_width: 0")
        w(t + "    pad_all: 0")
        w(t + "    clickable: false")
        w(t + "    scrollable: false")
        w(t + "    widgets:")
        w(t + "      - label:")
        w(t + "          align: CENTER")
        w(t + f"          text: $mdi_{kind}")
        w(t + "          text_font: mdi_20")
        w(t + f"          text_color: {C['white']}")
        tx = 60
    lbl(I + 6, tx, ty(5, 21, 18), name, "nunito_18", C["text"])
    lbl(I + 6, tx, ty(26, 17, 14), cap, "nunito_14", C["mut"])
    w(s + "    on_click:")
    # сразу видно, что нажатие принято: «Запускаю…» вместо названия трека
    w(s + "      - script.execute:")
    w(s + "          id: preset_feedback")
    w(s + f'          name: "{name}"')
    ha_action(I + 6, "script.sarai_muzyka_bystryi_zapusk", {"preset": preset})
w()
tabbar(I, "music_page")
w()

# ======================= SETTINGS PAGE =====================================
w("    # " + "=" * 70)
w("    # 5. НАСТРОЙКИ — вход только с экрана «Музыка»; без таб-бара и свайпа")
w("    # " + "=" * 70)
w("    - id: settings_page")
w("      styles: page_style")
w("      bg_color: white")
w("      bg_opa: COVER")
w("      pad_all: 0")
w("      skip: true      # свайп и page.next/previous эту страницу пропускают")
w("      widgets:")

def seg_group(gid, x0, w_each, gap, y=8, h_css=48):
    for i, (lab, glyph, act, cond) in enumerate(SEGS[gid]):
        x = x0 + i * (w_each + gap)
        key(J, x, y, w_each, h_css, id_=f"seg_{gid}_{i}", radius=16)
        t = " " * J
        w(t + "    checked:")
        w(t + "      bg_grad: seg_on_gradient")
        w(t + f"      bg_color: {C['mut']}")
        w(t + f"      border_color: {C['mut']}")
        w(t + "      shadow_opa: TRANSP")
        w(t + "      translate_y: 4")
        w(t + "    layout:")
        w(t + "      type: flex")
        w(t + "      flex_flow: ROW")
        w(t + "      flex_align_main: CENTER")
        w(t + "      flex_align_cross: CENTER")
        w(t + "      flex_align_track: CENTER")
        w(t + "      pad_column: 6")
        w(t + "    widgets:")
        if glyph:
            off = C["orange"] if glyph == "weather_sunny" else C["mut"]
            w(t + "      - label:")
            w(t + f"          id: icon_seg_{gid}_{i}")
            w(t + f"          text: $mdi_{glyph}")
            w(t + "          text_font: mdi_26")
            w(t + f"          text_color: {off}")
        w(t + "      - label:")
        w(t + f"          id: lbl_seg_{gid}_{i}")
        w(t + f'          text: "{lab}"')
        w(t + "          text_font: nunito_17")
        w(t + f"          text_color: {C['text']}")
        w(t + "    on_click:")
        a = act.split("\n")
        w(t + f"      - {a[0]}")
        for ln in a[1:]:
            w(t + f"        {ln.strip() and ln}")

def row_card(y, title, caption):
    card(I, 12, y, 456, 64)
    lbl(J, 18, ty(9, 24, 19), title, "nunito_19", C["text"])
    lbl(J, 18, ty(33, 20, 16), caption, "nunito_16", C["mut"])

def slider_row(cy, glyph, gcol, name, sid, lid, num_id):
    icon(J, 16, cy - 13, glyph, "mdi_26", gcol)
    lbl(J, 52, ty(cy - 12, 24, 19), name, "nunito_19", C["text"])
    block(f"""
- slider:
    id: {sid}
    x: 136
    y: {cy - 10}
    width: 216
    height: 20
    min_value: 5
    max_value: 100
    value: 50
    radius: 10
    bg_color: {C["track"]}
    bg_opa: COVER
    pad_all: 0
    indicator:
      bg_color: {C["orange"]}
      bg_opa: COVER
      radius: 10
    knob:
      bg_color: {C["white"]}
      bg_opa: COVER
      border_width: 4
      border_color: {C["mut"]}
      radius: 16
      pad_all: 6
      shadow_width: 0
    on_value:
      - lvgl.label.update:
          id: {lid}
          text: !lambda return str_sprintf("%d%%", (int) x);
    # отпустил палец -> в number (он применит яркость и сообщит HA)
    on_release:
      - number.set:
          id: {num_id}
          value: !lambda return x;
""", J)
    lbl(J, 372, ty(cy - 14, 28, 20), "--%", "nb_20", C["text"], id_=lid,
        extra={"width": 68, "text_align": "RIGHT"})

w(" " * I + "# ===== Яркость экрана днём / ночью =====")
card(I, 12, 12, 456, 140)
lbl(J, 18, ty(12, 22, 17), "Яркость экрана", "nunito_17", C["mut"])
slider_row(62, "weather_sunny", C["orange"], "Днём", "slider_cfg_day", "lbl_cfg_day", "cfg_day_brightness")
slider_row(108, "weather_night", C["mut"], "Ночью", "slider_cfg_night", "lbl_cfg_night", "cfg_night_brightness")
w()
w(" " * I + "# ===== Режим яркости сейчас (сам меняется по солнцу; можно выбрать вручную) =====")
row_card(164, "Режим", "сам по солнцу, −3°")
seg_group("mode", 216, 110, 8)
w()
w(" " * I + "# ===== Возврат на главную без касаний =====")
row_card(240, "На главную", "без касаний")
seg_group("home_return", 150, 69, 6)
w()
w(" " * I + "# ===== Гашение экрана без движения (таймер в HA) =====")
row_card(316, "Экран гаснет", "без движения")
seg_group("screen_off", 150, 69, 6)
w()
w(" " * I + "# ===== Служебное: Wi-Fi и IP (обновляет sensors_base по id) =====")
card(I, 12, 392, 336, 76)
icon(J, 16, 15, "wifi", "mdi_20", C["mut"])
lbl(J, 44, ty(13, 22, 17), "—", "nunito_17", C["text"], id_="connected_ssid_label",
    extra={"width": 206, "long_mode": "DOT", "height": 24})
lbl(J, 252, ty(13, 22, 17), "", "nunito_17", C["mut"], id_="wifi_signal_db_percent_label",
    extra={"width": 66, "text_align": "RIGHT"})
icon(J, 16, 45, "ip_network", "mdi_20", C["mut"])
lbl(J, 44, ty(43, 22, 17), "—", "nunito_17", C["text"], id_="ip_address_label")
w()
w(" " * I + "# ===== Возврат на главную (вместо таб-бара) =====")
key(I, 360, 392, 108, 76, id_="btn_settings_home", radius=20)
s_ = " " * I
w(s_ + "    layout:")
w(s_ + "      type: flex")
w(s_ + "      flex_flow: COLUMN")
w(s_ + "      flex_align_main: CENTER")
w(s_ + "      flex_align_cross: CENTER")
w(s_ + "      flex_align_track: CENTER")
w(s_ + "      pad_row: 2")
w(s_ + "    widgets:")
w(s_ + "      - label:")
w(s_ + "          text: $mdi_home")
w(s_ + "          text_font: mdi_26")
w(s_ + f"          text_color: {C['mut']}")
w(s_ + "      - label:")
w(s_ + '          text: "Главная"')
w(s_ + "          text_font: nunito_17")
w(s_ + f"          text_color: {C['text']}")
w(s_ + "    on_click:")
w(s_ + "      - lvgl.page.show: main_page")
w()

# ==========================================================================
# TEXT SENSORS
block(r'''
# ----------------------------------------------------------------------------
# Текстовые источники из HA.
# ----------------------------------------------------------------------------
text_sensor:
  # Яркость LED-ленты (0–255) -> слайдер и "40%" на странице света.
  # Текстовым датчиком, а не числовым: у выключенной ленты HA отдаёт яркость
  # "None", и числовой датчик сыпал в лог HA предупреждение «Can't convert
  # 'None' to number» на каждое переподключение.
  - platform: homeassistant
    id: ha_led_brightness
    entity_id: light.troitskaya_saray_led_saray
    attribute: brightness
    on_value:
      - lvgl.slider.update:
          id: slider_led_brightness
          value: !lambda |-
            char *end = nullptr;
            float v = strtof(x.c_str(), &end);
            if (x.empty() || end == x.c_str()) return 0;
            return (int) lroundf(v / 255.0f * 100);
      - lvgl.label.update:
          id: lbl_led_pct
          text: !lambda |-
            char *end = nullptr;
            float v = strtof(x.c_str(), &end);
            int p = (x.empty() || end == x.c_str()) ? 0 : (int) lroundf(v / 255.0f * 100);
            return str_sprintf("%d%%", p);

  # --- название трека: мини-плеер на главной + страница музыки ---
  - platform: homeassistant
    id: ha_sarai_media_title
    entity_id: media_player.sarai
    attribute: media_title
    on_value:
      - lvgl.label.update:
          id: lbl_mini_title
          text: !lambda |-
            return x.empty() ? std::string("—") : x;
      - lvgl.label.update:
          id: lbl_music_title
          text: !lambda |-
            return x.empty() ? std::string("—") : x;
      # пришло новое название — «Запускаю…» больше не нужен: шапку обратно
      - if:
          condition:
            script.is_running: preset_feedback
          then:
            - script.stop: preset_feedback
            - lvgl.label.update:
                id: lbl_music_state
                text: !lambda |-
                  auto s = id(ha_sarai_play_state).state;
                  if (s == "playing") return std::string("Играет · Сарай");
                  if (s == "paused") return std::string("Пауза · Сарай");
                  return std::string("Не играет · Сарай");

  # --- состояние плеера: значок на обеих кнопках + подписи "Играет" ---
  # играет -> на кнопке пауза (нажатие поставит на паузу), иначе — play
  - platform: homeassistant
    id: ha_sarai_play_state
    entity_id: media_player.sarai
    on_value:
      - lvgl.label.update:
          id: icon_mini_playpause
          text: !lambda |-
            return std::string((x == "playing") ? "$mdi_pause" : "$mdi_play");
      - lvgl.label.update:
          id: icon_music_playpause
          text: !lambda |-
            return std::string((x == "playing") ? "$mdi_pause" : "$mdi_play");
      - lvgl.label.update:
          id: lbl_mini_state
          text: !lambda |-
            if (x == "playing") return std::string("Играет ·");
            if (x == "paused") return std::string("Пауза ·");
            return std::string("Не играет ·");
      # слайдер громкости на главной: оранжевый, пока есть что слушать, иначе серый
      - lvgl.slider.update:
          id: slider_mini_volume
          indicator:
            bg_color: !lambda |-
              return (x == "playing" || x == "paused") ? Color(0xF3, 0x73, 0x20) : Color(0xC7, 0xCC, 0xDE);
      - lvgl.label.update:
          id: lbl_music_state
          text: !lambda |-
            if (x == "playing") return std::string("Играет · Сарай");
            if (x == "paused") return std::string("Пауза · Сарай");
            return std::string("Не играет · Сарай");

  # --- погода на улице: иконка MDI + состояние по-русски ---
  - platform: homeassistant
    id: ha_weather_cond
    entity_id: weather.forecast_troitskaia
    on_value:
      - lvgl.label.update:
          id: icon_weather
          text: !lambda |-
            if (x == "sunny") return std::string("$mdi_weather_sunny");
            if (x == "clear-night") return std::string("$mdi_weather_night");
            if (x == "partlycloudy") return std::string("$mdi_weather_partly_cloudy");
            if (x == "partlycloudy-night") return std::string("$mdi_weather_night_partly_cloudy");
            if (x == "cloudy") return std::string("$mdi_weather_cloudy");
            if (x == "rainy") return std::string("$mdi_weather_rainy");
            if (x == "pouring") return std::string("$mdi_weather_pouring");
            if (x == "snowy") return std::string("$mdi_weather_snowy");
            if (x == "snowy-rainy") return std::string("$mdi_weather_snowy_rainy");
            if (x == "lightning") return std::string("$mdi_weather_lightning");
            if (x == "lightning-rainy") return std::string("$mdi_weather_lightning_rainy");
            if (x == "fog") return std::string("$mdi_weather_fog");
            if (x == "hail") return std::string("$mdi_weather_hail");
            if (x == "windy") return std::string("$mdi_weather_windy");
            if (x == "windy-variant") return std::string("$mdi_weather_windy_variant");
            return std::string("$mdi_alert_circle_outline");
      - lvgl.label.update:
          id: lbl_weather_cond
          text: !lambda |-
            if (x == "sunny" || x == "clear-night") return std::string("ясно");
            if (x == "partlycloudy" || x == "partlycloudy-night") return std::string("малооблачно");
            if (x == "cloudy") return std::string("облачно");
            if (x == "rainy") return std::string("дождь");
            if (x == "pouring") return std::string("ливень");
            if (x == "snowy") return std::string("снег");
            if (x == "snowy-rainy") return std::string("мокрый снег");
            if (x == "lightning" || x == "lightning-rainy") return std::string("гроза");
            if (x == "fog") return std::string("туман");
            if (x == "hail") return std::string("град");
            if (x == "windy" || x == "windy-variant") return std::string("ветрено");
            if (x == "exceptional") return std::string("внимание");
            return std::string("—");

  # --- тренд парной из HA (sensor.bania_temperatura_trend: rising/falling/stable) ---
  - platform: homeassistant
    id: ha_sauna_trend
    entity_id: sensor.bania_temperatura_trend
    on_value:
      - lvgl.label.update:
          id: icon_trend
          text: !lambda |-
            if (x == "rising") return std::string("$mdi_trending_up");
            if (x == "falling") return std::string("$mdi_trending_down");
            return std::string("$mdi_trending_neutral");
          text_color: !lambda |-
            if (x == "rising") return Color(0xF3, 0x73, 0x20);
            if (x == "falling") return Color(0x3F, 0xA7, 0xF3);
            return Color(0x60, 0x66, 0x82);
      - lvgl.label.update:
          id: lbl_trend
          text: !lambda |-
            if (x == "rising") return std::string("греется");
            if (x == "falling") return std::string("остывает");
            return std::string("стабильно");
          text_color: !lambda |-
            if (x == "rising") return Color(0xB4, 0x50, 0x0E);
            if (x == "falling") return Color(0x1F, 0x6F, 0xA8);
            return Color(0x60, 0x66, 0x82);
''', 0)
w()

# занятость: баня/туалет — генерируем одинаковый код
def occupancy(sid, ent, chip, icon_id, lbl_id, free_word, busy_word):
    block(f'''
  # --- {"баня" if "bani" in ent else "туалет"}: {ent} ---
  # Занято: красная плашка, "{busy_word}" жирным капсом. Свободно: зелёная, "{free_word}".
  - platform: homeassistant
    id: {sid}
    entity_id: {ent}
    on_value:
      - if:
          condition:
            lambda: return x.rfind("Занят", 0) == 0;
          then:
            - lvgl.obj.update:
                id: {chip}
                bg_color: {C["busy_bg"]}
            - lvgl.label.update:
                id: {icon_id}
                text_color: {C["busy_ic"]}
            - lvgl.label.update:
                id: {lbl_id}
                text: "{busy_word}"
                text_font: nb_20
                text_color: {C["busy_tx"]}
          else:
            - lvgl.obj.update:
                id: {chip}
                bg_color: {C["free_bg"]}
            - lvgl.label.update:
                id: {icon_id}
                text_color: {C["free_ic"]}
            - lvgl.label.update:
                id: {lbl_id}
                text: !lambda |-
                  if (x.rfind("Свобод", 0) == 0) return std::string("{free_word}");
                  return x;
                text_font: nunito_20
                text_color: {C["free_tx"]}
''', 0)
    w()

occupancy("ha_banya_status", "sensor.zaniatost_bani_2", "obj_banya_chip", "icon_banya",
          "lbl_banya_status", "свободна", "ЗАНЯТА")
occupancy("ha_toilet_status", "sensor.zaniatost_tualeta_2", "obj_toilet_chip", "icon_toilet",
          "lbl_toilet_status", "свободен", "ЗАНЯТ")

# Инлайновые лямбды с " : " (тернарник) ломают YAML -> переводим в блочную форму
import re as _re
_fixed = []
for _ln in L:
    _m = _re.match(r"^(\s*)(- )?([A-Za-z_]+): !lambda (.+ : .+)$", _ln)
    if _m:
        _ind, _dash, _k, _body = _m.groups()
        _base = _ind + ("  " if _dash else "")
        _fixed.append(f"{_ind}{_dash or ''}{_k}: !lambda |-")
        _fixed.append(f"{_base}  {_body}")
    else:
        _fixed.append(_ln)
L[:] = _fixed

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(L).rstrip() + "\n")
print("written", OUT, len(L), "lines")
