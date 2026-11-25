# Рисува баба Стана и записва картинките в играта. Ползва само Pygame (без нови библиотеки).
# Пускане от папката "Real Life":   python tools/pixelart/make_baba.py
# Резултат:
#   assets/persons/baba_stana.png        - отпред, неподвижна (64x64)
#   assets/persons/baba_stana_walk.png   - ходене: ред 1 надолу, ред 2 нагоре, ред 3 надясно (512x192)
#   art_src/baba_stana_walk.piskel       - проект за Piskel с всичките 24 кадъра
#   art_src/baba_stana_preview.png       - уголемен преглед на зелен фон
# Идея за учениците: копирайте baba.py като нов файл и сменете цветовете, косата, дрехите...
import base64
import json
import os
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

ТУК = os.path.dirname(os.path.abspath(__file__))
ИГРА = os.path.dirname(os.path.dirname(ТУК))
sys.path.insert(0, ТУК)
import baba


def към_повърхност(пиксели):
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    for y in range(64):
        for x in range(64):
            if пиксели[y][x]:
                s.set_at((x, y), пиксели[y][x])
    return s


def лист(редове, мащаб=1, фон=None):
    s = pygame.Surface((64 * len(редове[0]), 64 * len(редове)), pygame.SRCALPHA)
    if фон:
        s.fill(фон)
    for r, ред in enumerate(редове):
        for c, кадър in enumerate(ред):
            s.blit(към_повърхност(кадър), (c * 64, r * 64))
    if мащаб != 1:
        s = pygame.transform.scale(s, (s.get_width() * мащаб, s.get_height() * мащаб))
    return s


def главна():
    pygame.init()
    pygame.display.set_mode((1, 1))
    надолу = [baba.front(i) for i in range(8)]
    нагоре = [baba.front(i, True) for i in range(8)]
    надясно = [baba.side(i) for i in range(8)]
    os.makedirs(os.path.join(ИГРА, "assets", "persons"), exist_ok=True)
    os.makedirs(os.path.join(ИГРА, "art_src"), exist_ok=True)
    pygame.image.save(към_повърхност(надолу[0]), os.path.join(ИГРА, "assets", "persons", "baba_stana.png"))
    pygame.image.save(лист([надолу, нагоре, надясно]), os.path.join(ИГРА, "assets", "persons", "baba_stana_walk.png"))
    pygame.image.save(лист([надолу, надясно, нагоре], 3, (58, 140, 62)), os.path.join(ИГРА, "art_src", "baba_stana_preview.png"))
    # .piskel: всички 24 кадъра в една лента
    временен = os.path.join(ИГРА, "art_src", "_strip.png")
    pygame.image.save(лист([надолу + нагоре + надясно]), временен)
    with open(временен, "rb") as f:
        данни = f.read()
    os.replace(временен, os.path.join(ИГРА, "art_src", "baba_stana_walk_strip.png"))
    слой = {"name": "Layer 1", "opacity": 1, "frameCount": 24,
            "chunks": [{"layout": [[k] for k in range(24)],
                        "base64PNG": "data:image/png;base64," + base64.b64encode(данни).decode()}]}
    проект = {"modelVersion": 2, "piskel": {"name": "baba_stana_walk",
              "description": "Real Life - баба Стана ходи: кадри 1-8 надолу, 9-16 нагоре, 17-24 надясно",
              "fps": 8, "height": 64, "width": 64, "layers": [json.dumps(слой)], "hiddenFrames": []}}
    with open(os.path.join(ИГРА, "art_src", "baba_stana_walk.piskel"), "w", encoding="utf-8") as f:
        json.dump(проект, f)
    print("Готово: assets/persons/baba_stana.png, baba_stana_walk.png и art_src/baba_stana_walk.piskel")


if __name__ == "__main__":
    главна()
