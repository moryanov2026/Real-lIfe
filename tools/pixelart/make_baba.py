# Рисува баба Стана и записва картинките в играта. Ползва само Pygame (без нови библиотеки).
# Пускане от папката "Real Life":   python tools/pixelart/make_baba.py
# Резултат:
#   assets/persons/baba_stana.png        - отпред, неподвижна (64x64)
#   assets/persons/baba_stana_walk.png   - ходене: ред 1 надолу, 2 нагоре, 3 надясно, 4 наляво (512x256)
#   art_src/baba_stana_walk.piskel       - проект за Piskel с всичките 32 кадъра
#   art_src/baba_stana_preview.png       - уголемен преглед на зелен фон
#   assets/persons/baba_stana_dance.png  - танцува хоро: 8 кадъра (512x64)
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
import pix


def към_повърхност(пиксели):
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    for y in range(64):
        for x in range(64):
            if пиксели[y][x]:
                s.set_at((x, y), pix.към_палитра(пиксели[y][x]))
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
    надясно = [baba.side(i, cane_near=False) for i in range(8)]
    # наляво = огледало на рисунка с бастуна в близката ръка -> пак е в дясната ѝ ръка
    наляво = [[ред[::-1] for ред in baba.side(i, cane_near=True)] for i in range(8)]
    os.makedirs(os.path.join(ИГРА, "assets", "persons"), exist_ok=True)
    os.makedirs(os.path.join(ИГРА, "art_src"), exist_ok=True)
    pygame.image.save(към_повърхност(надолу[0]), os.path.join(ИГРА, "assets", "persons", "baba_stana.png"))
    pygame.image.save(лист([надолу, нагоре, надясно, наляво]), os.path.join(ИГРА, "assets", "persons", "baba_stana_walk.png"))
    седи = [[baba.sit(посока, к) for к in range(4)] for посока in ("down", "up", "right")]   # сядане: 256x192
    pygame.image.save(лист(седи), os.path.join(ИГРА, "assets", "persons", "baba_stana_sit.png"))
    pygame.image.save(лист(седи, 3, (58, 140, 62)), os.path.join(ИГРА, "art_src", "baba_stana_sit_preview.png"))
    хоро = [baba.dance(i) for i in range(8)]                 # танцува хоро: 8 кадъра (512x64)
    pygame.image.save(лист([хоро]), os.path.join(ИГРА, "assets", "persons", "baba_stana_dance.png"))
    pygame.image.save(лист([хоро], 3, (58, 140, 62)), os.path.join(ИГРА, "art_src", "baba_stana_dance_preview.png"))
    временен = os.path.join(ИГРА, "art_src", "_dance.png")
    pygame.image.save(лист([хоро]), временен)
    with open(временен, "rb") as f:
        данни_хоро = f.read()
    os.replace(временен, os.path.join(ИГРА, "art_src", "baba_stana_dance_strip.png"))
    слой = {"name": "Layer 1", "opacity": 1, "frameCount": 8,
            "chunks": [{"layout": [[k] for k in range(8)],
                        "base64PNG": "data:image/png;base64," + base64.b64encode(данни_хоро).decode()}]}
    with open(os.path.join(ИГРА, "art_src", "baba_stana_dance.piskel"), "w", encoding="utf-8") as f:
        json.dump({"modelVersion": 2, "piskel": {"name": "baba_stana_dance",
                   "description": "Real Life - баба Стана играе хоро: 8 кадъра", "fps": 8,
                   "height": 64, "width": 64, "layers": [json.dumps(слой)], "hiddenFrames": []}}, f)
    pygame.image.save(лист([надолу, нагоре, надясно, наляво], 3, (58, 140, 62)), os.path.join(ИГРА, "art_src", "baba_stana_preview.png"))
    # .piskel: всички 32 кадъра в една лента
    временен = os.path.join(ИГРА, "art_src", "_strip.png")
    pygame.image.save(лист([надолу + нагоре + надясно + наляво]), временен)
    with open(временен, "rb") as f:
        данни = f.read()
    os.replace(временен, os.path.join(ИГРА, "art_src", "baba_stana_walk_strip.png"))
    слой = {"name": "Layer 1", "opacity": 1, "frameCount": 32,
            "chunks": [{"layout": [[k] for k in range(32)],
                        "base64PNG": "data:image/png;base64," + base64.b64encode(данни).decode()}]}
    проект = {"modelVersion": 2, "piskel": {"name": "baba_stana_walk",
              "description": "Real Life - баба Стана ходи: кадри 1-8 надолу, 9-16 нагоре, 17-24 надясно, 25-32 наляво",
              "fps": 8, "height": 64, "width": 64, "layers": [json.dumps(слой)], "hiddenFrames": []}}
    with open(os.path.join(ИГРА, "art_src", "baba_stana_walk.piskel"), "w", encoding="utf-8") as f:
        json.dump(проект, f)
    print("Готово: assets/persons/baba_stana.png, baba_stana_walk.png и art_src/baba_stana_walk.piskel")


if __name__ == "__main__":
    главна()
