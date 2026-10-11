#!/bin/bash
# shoot.sh OUTDIR name:sec name:sec ...  — запускает SDL-программу и снимает экраны в заданные секунды
O=$1; shift; mkdir -p $O
# BUILD — папка сборки SDL-варианта (.esphome/build/<name> рядом с sdl-test.yaml)
BUILD=${BUILD:-.esphome/build/panel-saray}
cd "$BUILD"
SDL_VIDEODRIVER=offscreen ./.pio/build/panel-saray/program > program.log 2>&1 &
P=$!
t=0
for spec in "$@"; do n=${spec%%:*}; s=${spec##*:}; sleep $((s - t)); t=$s; curl -s -o $O/$n.png localhost:8080/screenshot; done
kill $P
