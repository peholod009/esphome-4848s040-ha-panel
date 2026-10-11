# tools/ — генератор прошивки и превью без железа

## gen_panel.py — генератор `panel-saray.yaml`

Прошивка в `firmware/` не писалась руками: её собирает этот скрипт. Все
координаты, размеры и цвета взяты из макетов (HTML в `design/`, картинки — `docs/screenshots/`) и
переведены в LVGL по одним правилам (описаны в шапке скрипта), поэтому менять
состав экранов удобнее здесь, а не в 5000 строках YAML.

```bash
python3 tools/gen_panel.py firmware/panel-saray.yaml
```

Что где менять:

| Что | Где в `gen_panel.py` |
|---|---|
| Свет на экране «Сарай» (5 плиток + LED-лента) | список `LIGHTS` |
| Свет во дворе (10 плиток) | список `YARD` |
| Кнопки радио/плейлистов | список `PRESETS` (поле `preset` уходит в скрипт HA) |
| Температура парной, тренд, занятость бани/туалета | блоки `sensor:` / `text_sensor:` (поиск по `entity_id:`) |
| Погода | `weather.forecast_troitskaia` (поиск по тексту) |
| Плеер | `media_player.sarai` (поиск по тексту) |
| Цвета | словарь `C` в начале |
| Поворот экрана | подстановка `rotation` |

Количество плиток зашито в раскладку: 5+1 на «Сарае» и 10 на «Дворе». Если
у тебя их другое число — поменяй сетку (`TILES`, `YCOLS`/`YROWS`) или попроси
LLM (см. `docs/LLM_PROMPT.md`).

## make_sdl.py + shoot.sh — скриншоты настоящей LVGL на компьютере

Делает из прошивки тестовый вариант под SDL (экран — окно на ПК, данные HA —
подставные). Так сделаны скриншоты `docs/screenshots/lvgl-*.png`.

```bash
python3 tools/make_sdl.py firmware/panel-saray.yaml sdl-test.yaml main_page
esphome compile sdl-test.yaml          # нужна платформа host/native и SDL2
# снять кадры (секунды от старта программы):
BUILD=.esphome/build/panel-saray tools/shoot.sh shots main:4 light:10
```

Это инструмент для разработки, а не обязательная часть: для прошивки панели
он не нужен. Использует `hardware/SDL-lvgl.yaml` и компонент `lvgl_screenshot`
из библиотеки esphome-modular-lvgl-buttons.
