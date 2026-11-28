# Рисува персоните от chovek.py: Петър, Мария, Тодор, Георги, Ники, дядо Коле, Борис.
# Пускане от папката "Real Life":   python tools/pixelart/make_hora.py
#   assets/persons/<id>.png (64x64), <id>_walk.png (512x256: надолу, нагоре, надясно, наляво),
#   <id>_dance.png (хоро, 512x64), art_src/<id>_walk.piskel и <id>_dance.piskel за Piskel.
import os
import sys

ТУК = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ТУК)
import make_baba as обща
import make_stoyan
import chovek
import pygame


def главна(кои=None):
    pygame.init()
    pygame.display.set_mode((1, 1))
    п = os.path.join(обща.ИГРА, "assets", "persons")
    for пид, х in chovek.ХОРА.items():
        if кои and пид not in кои:
            continue
        надолу = [chovek.front(х, i) for i in range(8)]
        нагоре = [chovek.front(х, i, True) for i in range(8)]
        надясно = [chovek.side(х, i) for i in range(8)]
        наляво = [[ред[::-1] for ред in к] for к in надясно]
        хоро = [chovek.dance(х, i) for i in range(8)]
        pygame.image.save(обща.към_повърхност(надолу[0]), os.path.join(п, пид + ".png"))
        pygame.image.save(обща.лист([надолу, нагоре, надясно, наляво]), os.path.join(п, пид + "_walk.png"))
        pygame.image.save(обща.лист([хоро]), os.path.join(п, пид + "_dance.png"))
        pygame.image.save(обща.лист([надолу, нагоре, надясно, наляво, хоро], 3, (58, 140, 62)),
                          os.path.join(обща.ИГРА, "art_src", пид + "_preview.png"))
        make_stoyan.piskel(пид + "_walk", надолу + нагоре + надясно + наляво,
                           "Real Life - %s: 1-8 надолу, 9-16 нагоре, 17-24 надясно, 25-32 наляво" % пид)
        make_stoyan.piskel(пид + "_dance", хоро, "Real Life - %s играе хоро: 8 кадъра" % пид)
        print("Готово:", пид)


if __name__ == "__main__":
    главна(sys.argv[1:])
