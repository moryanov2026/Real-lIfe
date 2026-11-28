# Рисува мебелите от каталога за строене (Claude), в стила на масите и пейките.
# Пускане от папката "Real Life":   python tools/pixelart/make_mebeli.py
#   assets/bar.png 64x64 тезгях (парчетата се редят едно до друго)   assets/barrel.png 64x64 бъчва с канелка
#   assets/cash.png 64x64 каса (сандъче с пари)   assets/chest.png 64x64 сандък   assets/shelf.png 64x96 рафт с буркани
#   assets/stove.png 64x64 печка с гърне   assets/cauldron.png 64x64 котел на огън   assets/sink.png 64x64 каменно корито
#   assets/cutting_board.png 64x64 маса с дъска за рязане   assets/fireplace.png 64x96 огнище
#   assets/stage.png 128x64 сцена с черга   assets/menu_board.png 64x96 табло с меню
# Светлина горе вляво. Картинката се подравнява по долния ръб на клетката.
import math
import os
import sys

ТУК = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ТУК)
from pix import *
import make_baba as обща
import pygame

M = lambda *a: tuple(hx(c) for c in a)
OUT = hx('#2a1d16')
WOOD = M('#e2aa70', '#b8783f', '#8a5228', '#5a321a')
WOOD2 = M('#c99460', '#9a6232', '#70421e', '#482612')     # по-тъмно дърво (предни страни)
IRON = M('#7a7880', '#4a4850', '#302e36', '#1a1820')
STONE = M('#d8d2c4', '#aea696', '#857d6e', '#5a544a')
BRICK = M('#e08860', '#b85a3a', '#8a3c26', '#5c2416')
CLAY = M('#e8a070', '#c87a48', '#9a5430', '#6a3420')
WATER = M('#bfe6f2', '#7cc0dc', '#4a90b8', '#2c6488')
GOLD = M('#fff0a0', '#f2cc2e', '#c89a18', '#8a660c')
RED = M('#f0605a', '#d02c2a', '#9a1a1e', '#661014')
FIRE = (hx('#fff4a0'), hx('#ffc840'), hx('#f07820'), hx('#c83418'))
BOARD = M('#3e5a48', '#2e4638', '#22362a', '#16241c')
CHALK = hx('#f2f2e6'); GREEN = hx('#3c9a4a'); TOMATO = hx('#e83a2e'); PEPPER = hx('#f0b020')
JARS = [M('#f4fbff', '#d6eef6', '#a8d0dc', '#7aa8b8'), CLAY, M('#fff2b0', '#f6dc78', '#e0b84a', '#b88c2a')]


def пр(cv, x0, y0, x1, y1, мат, z, extra=0.0):
    return poly(cv, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], мат, z, extra=extra)


def дъски(cv, x0, y0, x1, y1, z, хоризонтални=True, през=6, мат=WOOD):
    """Дървена повърхност с тъмни шевове между дъските."""
    пр(cv, x0, y0, x1, y1, мат, z)
    if хоризонтални:
        for y in range(int(y0) + през, int(y1), през):
            for x in range(int(x0), int(x1)):
                cv.plot(x, y, мат[3], z + 0.1, 960)
    else:
        for x in range(int(x0) + през, int(x1), през):
            for y in range(int(y0), int(y1)):
                cv.plot(x, y, мат[3], z + 0.1, 960)


def огън(cv, cx, cy, ш, в, z, фаза=0):
    for k in range(4):
        r = 1 - k * 0.24
        ellipse(cv, cx, cy - в * 0.35 * k / 3, ш * r, в * r * 0.6, (FIRE[3 - k],) * 4, z + k * 0.1)
    for dx in (-ш * 0.5, 0, ш * 0.5):
        cv.plot(int(cx + dx), int(cy - в * 0.9), FIRE[1], z + 0.5, 961)


def тезгях():
    cv = Canvas(64, 64)
    дъски(cv, 0, 14, 64, 32, 2, хоризонтални=True, през=6)               # плотът отгоре
    пр(cv, 0, 32, 64, 36, WOOD2, 2.5, extra=0.3)                           # ръбът на плота
    дъски(cv, 2, 36, 62, 62, 1, хоризонтални=False, през=10, мат=WOOD2)   # предната страна
    пр(cv, 10, 42, 54, 56, WOOD2, 1.2, extra=-0.4)                        # изрязана табла
    for x in (10, 53):
        for y in range(42, 56):
            cv.plot(x, y, WOOD2[3], 1.3, 962)
    ellipse(cv, 32, 49, 4, 3, GOLD, 1.4)                                  # месингов кръг (украса)
    return finish(cv, OUT)


def бъчва():
    cv = Canvas(64, 64)
    пр(cv, 14, 54, 50, 60, WOOD2, 0.5)                                    # поставка
    capsule(cv, (32, 22), (32, 46), 17, 17, WOOD, 1)                      # тялото
    for y in (24, 44):                                                    # железни обръчи
        ellipse(cv, 32, y, 17.6, 3.0, IRON, 1.5, mask=lambda x, yy, y=y: yy >= y - 1)
    for x in (22, 32, 42):                                                # дъските на бъчвата
        for y in range(12, 58):
            cv.plot(x, y, WOOD[3], 1.2, 963)
    ellipse(cv, 32, 13, 14, 5, WOOD2, 2, extra=0.4)                      # капакът
    capsule(cv, (32, 40), (32, 46), 2.2, 2.2, GOLD, 2.2)                  # канелката
    return finish(cv, OUT)


def каса():
    cv = Canvas(64, 64)
    дъски(cv, 6, 30, 58, 44, 1)                                           # масичка
    пр(cv, 6, 44, 58, 48, WOOD2, 1.1)
    for x in (9, 52):
        пр(cv, x, 48, x + 4, 62, WOOD2, 0.8)
    пр(cv, 18, 14, 46, 34, WOOD2, 2)                                      # сандъчето с парите
    пр(cv, 17, 10, 47, 16, WOOD, 2.2, extra=0.4)
    for x in range(18, 46):
        cv.plot(x, 24, IRON[2], 2.3, 964)
    ellipse(cv, 32, 24, 3, 3, GOLD, 2.4)                                  # ключалка
    for (x, y) in ((12, 38), (15, 40), (49, 37), (52, 40), (46, 41)):     # монети
        ellipse(cv, x, y, 2.6, 1.8, GOLD, 2.5)
    return finish(cv, OUT)


def сандък():
    cv = Canvas(64, 64)
    пр(cv, 8, 30, 56, 60, WOOD2, 1)                                       # кутията
    ellipse(cv, 32, 30, 24, 10, WOOD, 1.5, mask=lambda x, y: y <= 30)    # заобленият капак
    пр(cv, 8, 26, 56, 32, WOOD, 1.4)
    for x in (16, 47):                                                    # железни ленти
        пр(cv, x, 20, x + 3, 60, IRON, 2)
    for x in range(8, 56):
        cv.plot(x, 32, IRON[2], 2, 965)
    пр(cv, 29, 33, 35, 40, GOLD, 2.2)                                     # ключалка
    return finish(cv, OUT)


def рафт():
    cv = Canvas(64, 96)
    пр(cv, 4, 8, 60, 92, WOOD2, 0.5, extra=-0.5)                          # гърбът
    for x in (4, 56):
        пр(cv, x, 6, x + 4, 94, WOOD, 1)
    for y in (30, 56, 82):                                                # полиците
        пр(cv, 4, y, 60, y + 4, WOOD, 1.2)
    for k, y in enumerate((30, 56, 82)):
        for j, x in enumerate((14, 26, 38, 50)):
            мат = JARS[(j + k) % 3]
            if (j + k) % 2:
                capsule(cv, (x, y - 4), (x, y - 14), 4.2, 4.2, мат, 1.5)  # буркан
                ellipse(cv, x, y - 18, 4.6, 1.6, RED, 1.6)
            else:
                capsule(cv, (x, y - 3), (x, y - 12), 3.6, 3.6, мат, 1.5)  # шише
                capsule(cv, (x, y - 12), (x, y - 19), 1.4, 1.4, мат, 1.6)
    return finish(cv, OUT)


def печка():
    cv = Canvas(64, 64)
    пр(cv, 6, 24, 58, 60, IRON, 1)                                        # тялото
    пр(cv, 4, 18, 60, 28, IRON, 1.5, extra=0.5)                           # плочата отгоре
    for x in (8, 54):
        пр(cv, x, 58, x + 4, 63, IRON, 0.8)
    пр(cv, 16, 36, 36, 52, IRON, 1.6, extra=-0.6)                         # вратичката
    огън(cv, 26, 49, 7, 8, 1.7)
    for x in range(42, 54, 3):                                            # решетка
        for y in range(36, 52):
            cv.plot(x, y, IRON[0], 1.7, 966)
    ellipse(cv, 22, 14, 11, 7, CLAY, 2)                                   # гърне с боб
    ellipse(cv, 22, 9, 9, 3, CLAY, 2.2, extra=0.5)
    ellipse(cv, 22, 9.5, 7, 2, M('#e8a858', '#c47a30', '#94541c', '#6a3810'), 2.3)
    for x in (18, 23, 28):                                                # пара
        for y in range(0, 6):
            cv.plot(x + (1 if y % 3 == 0 else 0), y, hx('#e8eef2'), 0.4, 967)
    ellipse(cv, 46, 21, 7, 3, IRON, 1.8, extra=-0.6)                      # втори котлон
    return finish(cv, OUT, inner=False)


def котел():
    cv = Canvas(64, 64)
    for (a, b) in (((10, 62), (24, 18)), ((54, 62), (40, 18)), ((32, 60), (32, 16))):   # триножник
        capsule(cv, a, b, 1.4, 1.4, IRON, 0.5)
    огън(cv, 32, 58, 14, 12, 0.8)
    for x in (20, 30, 40):                                                # дърва
        capsule(cv, (x - 6, 60), (x + 6, 58), 2, 2, WOOD2, 0.9)
    ellipse(cv, 32, 38, 18, 14, IRON, 1.5)                                # котелът
    ellipse(cv, 32, 27, 17, 5, IRON, 1.7, extra=0.6)
    ellipse(cv, 32, 27.5, 14, 3.4, M('#e8a858', '#c47a30', '#94541c', '#6a3810'), 1.8)
    for x in (24, 32, 40):
        for y in range(10, 22):
            cv.plot(x + (1 if (y // 3) % 2 else 0), y, hx('#e8eef2'), 0.4, 968)
    return finish(cv, OUT, inner=False)


def мивка():
    cv = Canvas(64, 64)
    пр(cv, 6, 26, 58, 58, STONE, 1)                                       # каменното корито
    пр(cv, 4, 20, 60, 30, STONE, 1.4, extra=0.5)
    пр(cv, 10, 22, 54, 30, WATER, 1.6)                                    # водата
    for x in range(12, 52, 7):
        cv.plot(x, 25, hx('#ffffff'), 1.7, 969); cv.plot(x + 1, 25, hx('#ffffff'), 1.7, 969)
    for x in range(6, 58, 13):                                            # фуги между камъните
        for y in range(32, 58):
            cv.plot(x, y, STONE[3], 1.2, 970)
    for x in range(6, 58):
        cv.plot(x, 44, STONE[3], 1.2, 970)
    capsule(cv, (50, 50), (50, 60), 5, 4, WOOD2, 2)                       # ведро отпред
    ellipse(cv, 50, 49, 5, 2, WATER, 2.2)
    return finish(cv, OUT)


def дъска_за_рязане():
    cv = Canvas(64, 64)
    дъски(cv, 2, 22, 62, 42, 1)                                           # работна маса
    пр(cv, 2, 42, 62, 47, WOOD2, 1.1)
    for x in (5, 55):
        пр(cv, x, 47, x + 4, 62, WOOD2, 0.8)
    пр(cv, 10, 24, 40, 38, WOOD, 1.5, extra=0.5)                          # дъската
    for y in (27, 31, 35):
        for x in range(12, 38):
            if x % 5:
                cv.plot(x, y, WOOD[2], 1.6, 971)
    for (x, y) in ((16, 30), (20, 32), (24, 29)):                         # нарязан домат
        ellipse(cv, x, y, 2.4, 1.8, (hx('#ff8a70'), TOMATO, hx('#b02020'), hx('#781414')), 1.8)
    capsule(cv, (30, 33), (38, 28), 0.9, 0.9, IRON, 1.9)                  # нож
    capsule(cv, (38, 28), (42, 26), 1.3, 1.3, WOOD2, 1.9)
    ellipse(cv, 49, 30, 4.5, 4, (hx('#ff8a70'), TOMATO, hx('#b02020'), hx('#781414')), 1.7)   # цял домат
    capsule(cv, (50, 37), (58, 34), 2.2, 1.4, (hx('#ffe080'), PEPPER, hx('#c88010'), hx('#8a5408')), 1.7)   # чушка
    cv.plot(49, 26, GREEN, 2, 972)
    return finish(cv, OUT)


def огнище():
    cv = Canvas(64, 96)
    пр(cv, 4, 30, 60, 94, STONE, 1)                                       # каменната стена
    пр(cv, 0, 24, 64, 34, WOOD, 1.5, extra=0.4)                           # полица (рамка) отгоре
    for y in range(40, 94, 9):                                            # камъни
        for x in range(4, 60):
            cv.plot(x, y, STONE[3], 1.1, 973)
        for x in range(4 + (y // 9 % 2) * 7, 60, 14):
            for yy in range(y - 9, y):
                cv.plot(x, yy, STONE[3], 1.1, 973)
    ellipse(cv, 32, 72, 18, 20, IRON, 1.6, mask=lambda x, y: y <= 92)     # отвор
    пр(cv, 14, 72, 50, 92, IRON, 1.6)
    огън(cv, 32, 88, 12, 16, 1.8)
    for x in (22, 32, 42):
        capsule(cv, (x - 7, 91), (x + 7, 89), 2.2, 2.2, WOOD2, 1.9)
    for (x, c) in ((12, CLAY), (50, JARS[2])):                            # гърненца на полицата
        capsule(cv, (x, 22), (x, 14), 4, 4, c, 2)
    return finish(cv, OUT, inner=False)


def сцена():
    cv = Canvas(128, 64)
    дъски(cv, 2, 20, 126, 50, 1, хоризонтални=True, през=7)               # подиумът
    пр(cv, 2, 50, 126, 60, WOOD2, 1.2)                                    # предният ръб
    for x in range(2, 126, 16):
        for y in range(50, 60):
            cv.plot(x, y, WOOD2[3], 1.3, 974)
    пр(cv, 24, 24, 104, 46, RED, 1.5)                                     # черга
    for x in range(24, 104):                                              # шарки по чергата
        for y in (27, 43):
            cv.plot(x, y, GOLD[1] if (x // 3) % 2 else hx('#202040'), 1.6, 975)
    for cx in range(36, 100, 16):
        for d in range(5):
            for (dx, dy) in ((d, 0), (-d, 0), (0, d), (0, -d)):
                pass
        for (dx, dy) in ((0, -4), (-4, 0), (4, 0), (0, 4), (0, 0), (-2, -2), (2, 2), (2, -2), (-2, 2)):
            cv.plot(cx + dx, 35 + dy, GOLD[1] if (dx + dy) % 4 else hx('#2050a0'), 1.7, 976)
    return finish(cv, OUT)


def табло():
    cv = Canvas(64, 96)
    for (a, b) in (((14, 94), (22, 20)), ((50, 94), (42, 20)), ((32, 92), (32, 30))):   # статив
        capsule(cv, a, b, 2, 2, WOOD2, 0.5)
    пр(cv, 6, 10, 58, 66, WOOD, 1)                                        # рамка
    пр(cv, 10, 14, 54, 62, BOARD, 1.2)                                    # черната дъска
    for y, дълж in ((20, 30), (28, 24), (36, 32), (44, 26), (52, 20)):    # редове с тебешир
        for x in range(14, 14 + дълж):
            if x % 4 != 3:
                cv.plot(x, y, CHALK, 1.3, 977)
        for x in range(46, 51):
            cv.plot(x, y, CHALK, 1.3, 977)
    for x in range(14, 50, 2):
        cv.plot(x, 17, hx('#f0b020'), 1.3, 977)
    return finish(cv, OUT)


def главна():
    pygame.init()
    pygame.display.set_mode((1, 1))
    for име, ф in (("bar", тезгях), ("barrel", бъчва), ("cash", каса), ("chest", сандък), ("shelf", рафт),
                   ("stove", печка), ("cauldron", котел), ("sink", мивка), ("cutting_board", дъска_за_рязане),
                   ("fireplace", огнище), ("stage", сцена), ("menu_board", табло)):
        пиксели = ф()
        s = pygame.Surface((len(пиксели[0]), len(пиксели)), pygame.SRCALPHA)
        for y, ред in enumerate(пиксели):
            for x, ц in enumerate(ред):
                if ц:
                    s.set_at((x, y), към_палитра(ц))
        pygame.image.save(s, os.path.join(обща.ИГРА, "assets", име + ".png"))
        print("assets/%s.png" % име)


if __name__ == "__main__":
    главна()
