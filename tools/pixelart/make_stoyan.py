# Рисува музиканта Стоян (persons/muzikant) и записва картинките в играта.
# Пускане от папката "Real Life":   python tools/pixelart/make_stoyan.py
#   assets/persons/muzikant.png          отпред, неподвижен (64x64)
#   assets/persons/muzikant_walk.png     ходене: надолу, нагоре, надясно, наляво (512x256)
#   assets/persons/muzikant_play.png     свири: 2 кадъра (128x64)
#   assets/music/muzikant_golyam.png     голям Стоян за минииграта (192x192 = x3)
#   art_src/muzikant_walk.piskel, art_src/muzikant_play.piskel, art_src/muzikant_preview.png
import os
import sys

ТУК = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ТУК)
import make_baba as обща          # ползваме същите помощници (към_повърхност, лист, .piskel)
import stoyan

ИГРА = обща.ИГРА
import pygame


def piskel(име, кадри, описание):
    import base64, json
    временен = os.path.join(ИГРА, "art_src", "_strip.png")
    pygame.image.save(обща.лист([кадри]), временен)
    with open(временен, "rb") as f:
        данни = f.read()
    os.remove(временен) if False else os.replace(временен, os.path.join(ИГРА, "art_src", име + "_strip.png"))
    слой = {"name": "Layer 1", "opacity": 1, "frameCount": len(кадри),
            "chunks": [{"layout": [[k] for k in range(len(кадри))],
                        "base64PNG": "data:image/png;base64," + base64.b64encode(данни).decode()}]}
    проект = {"modelVersion": 2, "piskel": {"name": име, "description": описание, "fps": 8,
              "height": 64, "width": 64, "layers": [json.dumps(слой)], "hiddenFrames": []}}
    with open(os.path.join(ИГРА, "art_src", име + ".piskel"), "w", encoding="utf-8") as f:
        json.dump(проект, f)


def главна():
    pygame.init()
    pygame.display.set_mode((1, 1))
    надолу = [stoyan.front(i) for i in range(8)]
    нагоре = [stoyan.front(i, True) for i in range(8)]
    надясно = [stoyan.side(i, kaval_near=True) for i in range(8)]
    наляво = [[ред[::-1] for ред in stoyan.side(i, kaval_near=False)] for i in range(8)]
    свири = [stoyan.play(0), stoyan.play(1)]
    п = os.path.join(ИГРА, "assets", "persons")
    pygame.image.save(обща.към_повърхност(надолу[0]), os.path.join(п, "muzikant.png"))
    pygame.image.save(обща.лист([надолу, нагоре, надясно, наляво]), os.path.join(п, "muzikant_walk.png"))
    pygame.image.save(обща.лист([свири]), os.path.join(п, "muzikant_play.png"))
    голям = pygame.transform.scale(обща.към_повърхност(свири[0]), (192, 192))
    os.makedirs(os.path.join(ИГРА, "assets", "music"), exist_ok=True)
    pygame.image.save(голям, os.path.join(ИГРА, "assets", "music", "muzikant_golyam.png"))
    pygame.image.save(обща.лист([надолу, нагоре, надясно, наляво, свири + [надолу[0]] * 6], 3, (58, 140, 62)),
                      os.path.join(ИГРА, "art_src", "muzikant_preview.png"))
    piskel("muzikant_walk", надолу + нагоре + надясно + наляво,
           "Real Life - Стоян (музикант) ходи: 1-8 надолу, 9-16 нагоре, 17-24 надясно, 25-32 наляво")
    piskel("muzikant_play", свири, "Real Life - Стоян свири на кавал: 2 кадъра")
    print("Готово: muzikant.png, muzikant_walk.png, muzikant_play.png, muzikant_golyam.png")


if __name__ == "__main__":
    главна()
