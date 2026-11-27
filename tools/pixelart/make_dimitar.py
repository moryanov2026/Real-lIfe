# Рисува Димитър (собственика) в празнична носия. Пускане от папката "Real Life":
#     python tools/pixelart/make_ivan.py
#   assets/persons/sobstvenik.png         отпред, неподвижен (64x64)
#   assets/persons/sobstvenik_walk.png    ходене: надолу, нагоре, надясно, наляво (512x256)
#   assets/persons/sobstvenik_dance.png   хоро: 8 кадъра (512x64)
#   art_src/sobstvenik_walk.piskel, art_src/sobstvenik_dance.piskel, art_src/sobstvenik_preview.png
import os
import sys

ТУК = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ТУК)
import make_baba as обща
import make_stoyan
import dimitar as ivan
import pygame

ИГРА = обща.ИГРА


def главна():
    pygame.init()
    pygame.display.set_mode((1, 1))
    надолу = [ivan.front(i) for i in range(8)]
    нагоре = [ivan.front(i, True) for i in range(8)]
    надясно = [ivan.side(i) for i in range(8)]
    наляво = [[ред[::-1] for ред in к] for к in надясно]      # симетричен е: огледало стига
    хоро = [ivan.dance(i) for i in range(8)]
    п = os.path.join(ИГРА, "assets", "persons")
    pygame.image.save(обща.към_повърхност(надолу[0]), os.path.join(п, "sobstvenik.png"))
    pygame.image.save(обща.лист([надолу, нагоре, надясно, наляво]), os.path.join(п, "sobstvenik_walk.png"))
    pygame.image.save(обща.лист([хоро]), os.path.join(п, "sobstvenik_dance.png"))
    pygame.image.save(обща.лист([надолу, нагоре, надясно, наляво, хоро], 3, (58, 140, 62)),
                      os.path.join(ИГРА, "art_src", "sobstvenik_preview.png"))
    make_stoyan.piskel("sobstvenik_walk", надолу + нагоре + надясно + наляво,
                       "Real Life - Димитър (собственик) в носия: 1-8 надолу, 9-16 нагоре, 17-24 надясно, 25-32 наляво")
    make_stoyan.piskel("sobstvenik_dance", хоро, "Real Life - Димитър играе хоро: 8 кадъра")
    print("Готово: sobstvenik.png, sobstvenik_walk.png, sobstvenik_dance.png")


if __name__ == "__main__":
    главна()
