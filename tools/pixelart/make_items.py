# Рисува храната и питиетата за поръчките (Claude). Пускане от папката "Real Life":
#     python tools/pixelart/make_items.py
#   assets/items/rakia.png    32x32  ракия: шише и чашка
#   assets/items/vino.png     32x32  вино: глинена каничка и чаша
#   assets/items/shopska.png  32x32  шопска салата: домати, краставици, настърганo сирене
#   assets/items/bob.png      32x32  боб чорба в глинено гърне, с джоджен
import os
import sys

ТУК = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ТУК)
from pix import *
import make_baba as обща
import pygame

def към_повърхност(пиксели):
    s = pygame.Surface((len(пиксели[0]), len(пиксели)), pygame.SRCALPHA)
    for y, ред in enumerate(пиксели):
        for x, ц in enumerate(ред):
            if ц:
                s.set_at((x, y), към_палитра(ц))
    return s


M = lambda *a: tuple(hx(c) for c in a)
OUT = hx('#2a1d16')
GLASS = M('#f4fbff', '#d6eef6', '#a8d0dc', '#7aa8b8')
RAKIA = M('#fff2b0', '#f6dc78', '#e0b84a', '#b88c2a')
WINE = M('#c8424e', '#9a1e2e', '#6e1020', '#480814')
CLAY = M('#e8a070', '#c87a48', '#9a5430', '#6a3420')
BOWL = M('#ffffff', '#eeeae2', '#cfc8ba', '#a39a8a')
TOM = M('#ff8a70', '#e83a2e', '#b02020', '#781414')
CUC = M('#b8e888', '#6cb83e', '#3e8a2a', '#265a1c')
SOUP = M('#e8a858', '#c47a30', '#94541c', '#6a3810')
WHITE = hx('#fffdf4'); PARS = hx('#3a9a3a'); STEAM = hx('#e8eef2')


def ракия():
    cv = Canvas(32, 32)
    capsule(cv, (11, 22), (11, 12), 5.0, 5.0, GLASS, 1)                 # шишето
    capsule(cv, (11, 12), (11, 6), 2.0, 2.0, GLASS, 1.2)                # гърлото
    ellipse(cv, 11, 4.5, 2.2, 1.6, CLAY, 1.4)                            # тапата
    capsule(cv, (11, 24), (11, 15), 4.2, 4.2, RAKIA, 1.1)                # ракията вътре
    poly(cv, [(18, 18), (27, 18), (26, 27), (19, 27)], GLASS, 2)         # чашката
    poly(cv, [(18.6, 21), (26.4, 21), (25.8, 26.4), (19.2, 26.4)], RAKIA, 2.1)
    cv.plot(9, 13, WHITE, 3, 990); cv.plot(9, 14, WHITE, 3, 990); cv.plot(20, 19, WHITE, 3, 990)
    return finish(cv, OUT)


def вино():
    cv = Canvas(32, 32)
    ellipse(cv, 11, 19, 7.0, 7.5, CLAY, 1)                               # каничката
    capsule(cv, (11, 12), (11, 8), 3.6, 4.2, CLAY, 1.2)
    ellipse(cv, 11, 7.5, 4.4, 1.6, CLAY, 1.3, extra=-0.3)
    capsule(cv, (17, 14), (19, 21), 1.2, 1.2, CLAY, 0.8)                 # дръжката
    for x in range(6, 17):                                               # шарка
        cv.plot(x, 17, hx('#f2e2b0') if x % 2 else CLAY[3], 2, 991)
    ellipse(cv, 24, 15, 4.6, 4.0, GLASS, 2, mask=lambda x, y: y >= 13)   # чашата
    ellipse(cv, 24, 15.5, 3.8, 3.0, WINE, 2.1, mask=lambda x, y: y >= 15)
    capsule(cv, (24, 19), (24, 25), 0.8, 0.8, GLASS, 2)
    ellipse(cv, 24, 26, 3.4, 1.2, GLASS, 2)
    cv.plot(22, 14, WHITE, 3, 990)
    return finish(cv, OUT)


def шопска():
    cv = Canvas(32, 32)
    ellipse(cv, 16, 21, 13.5, 7.5, BOWL, 1)                              # купата
    ellipse(cv, 16, 18, 12.5, 5.0, BOWL, 1.2, extra=-0.5)
    for (x, y) in ((10, 17), (19, 16), (15, 20), (23, 19)):              # домати
        ellipse(cv, x, y, 2.8, 2.2, TOM, 2)
    for (x, y) in ((14, 16), (8, 19), (21, 20), (25, 17), (18, 19)):     # краставици
        ellipse(cv, x, y, 2.0, 1.6, CUC, 2.1)
    ellipse(cv, 16, 13, 6.5, 3.6, M('#ffffff', '#f7f4ea', '#e6e0cc', '#c8c0a8'), 2.4)   # сиренето отгоре
    for (x, y) in ((12, 12), (15, 11), (19, 12), (17, 14), (13, 14), (20, 14), (10, 15), (22, 15)):
        cv.plot(x, y, WHITE, 3, 990)
    cv.plot(16, 9, PARS, 3, 990); cv.plot(17, 9, PARS, 3, 990); cv.plot(16, 8, PARS, 3, 990)   # магданоз
    return finish(cv, OUT)


def боб():
    cv = Canvas(32, 32)
    ellipse(cv, 16, 21, 12.5, 8.0, CLAY, 1)                              # гърнето
    ellipse(cv, 16, 16, 12.0, 4.4, CLAY, 1.3, extra=0.3)                 # ръбът
    ellipse(cv, 16, 16.4, 10.0, 3.2, SOUP, 1.4)                          # чорбата
    for (x, y) in ((11, 16), (14, 15), (18, 17), (21, 16), (16, 17)):    # бобчета
        cv.plot(x, y, hx('#fbe6c0'), 2, 990); cv.plot(x + 1, y, hx('#d8b888'), 2, 990)
    for (x, y) in ((13, 17), (19, 15), (16, 15)):                        # джоджен
        cv.plot(x, y, PARS, 2, 990)
    for x in range(5, 28):                                               # шарка по гърнето
        if x % 3 == 0:
            cv.plot(x, 23, hx('#f2e2b0'), 2, 991)
    for k, x in enumerate((11, 16, 21)):                                 # пара
        for y in range(4, 11):
            cv.plot(x + (1 if (y + k) % 4 < 2 else 0), y, STEAM, 0.5, 992)
    return finish(cv, OUT, inner=False)


def главна():
    print("Иконките вече ги рисува make_ikoni.py (пиксел по пиксел, 16x16). Този файл остава за пример.")
    return
    pygame.init()
    pygame.display.set_mode((1, 1))
    папка = os.path.join(обща.ИГРА, "assets", "items")
    os.makedirs(папка, exist_ok=True)
    for име, ф in (("rakia", ракия), ("vino", вино), ("shopska", шопска), ("bob", боб)):
        pygame.image.save(към_повърхност(ф()), os.path.join(папка, име + ".png"))
        print("assets/items/%s.png" % име)


if __name__ == "__main__":
    главна()
