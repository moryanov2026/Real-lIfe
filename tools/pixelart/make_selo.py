# Рисува селото (Claude): трева, калдъръм, къщи, кръчмата отвън, сергии на пазара, кладенец, дървета, ограда.
# Пускане от папката "Real Life":   python tools/pixelart/make_selo.py
#   assets/grass.png, grass2.png, path.png      64x64 под (трева, калдъръм)
#   assets/house_a.png, house_b.png             къща 4x3 клетки (256x256 с покрива)
#   assets/krachma_out.png                      кръчмата отвън 6x3 клетки (384x256), с табела
#   assets/sergia.png                           сергия на пазара 2x1 (128x128) с навес
#   assets/kladenets.png                        кладенец 1x1 (64x112)
#   assets/darvo.png                            дърво 2x1 (128x160)
#   assets/ograda.png                           дървена ограда 1x1, assets/tsvetya.png цветя
#   assets/niva.png (изорана земя), rasteniya/<култура>_<0-3>.png и _mrtvo.png (растенията на нивата)
#   assets/kokoshkarnik.png 2x2, krava.png 2x1, magazin_out.png 4x3 (магазинът отвън)
#   assets/tsarkva_out.png 5x4 (църквата от бял камък, по снимките на учителя), kambanaria.png 2x1 (камбанарията), ikonostas.png 6x2, svechnik.png, kupel.png, kamak_pod.png
# Светлина горе вляво. Картинката се подравнява по долния ръб на клетките.
import math
import os
import random
import sys

ТУК = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ТУК)
from pix import *
import make_baba as обща
import pygame

M = lambda *a: tuple(hx(c) for c in a)
OUT = hx('#24180f')
GRASS = M('#9ad25a', '#6cae3c', '#4a8a2e', '#2e6224')
STONE = M('#e2dccc', '#bab2a0', '#8e8676', '#5e584c')
PLASTER = M('#fffaf0', '#f2ead8', '#d8ccb2', '#ac9e84')
ROOF = M('#f08a5a', '#cc5a32', '#9c3a20', '#6a2414')
WOOD = M('#e2aa70', '#b8783f', '#8a5228', '#5a321a')
WOOD2 = M('#c99460', '#9a6232', '#70421e', '#482612')
BLUE = M('#9ad0f0', '#4a90c8', '#2e6aa0', '#1c4470')
GLASS = M('#e8f6ff', '#b8dcf0', '#80b4d4', '#507c9c')
LEAF = M('#a8e070', '#6cb444', '#3e8a32', '#235a22')
WATER = M('#bfe6f2', '#7cc0dc', '#4a90b8', '#2c6488')
RED = M('#ff8070', '#e0302a', '#a81e1e', '#701414')
WHITE = hx('#ffffff')


def пр(cv, x0, y0, x1, y1, мат, z, extra=0.0):
    return poly(cv, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], мат, z, extra=extra)


def повърхност(пиксели):
    s = pygame.Surface((len(пиксели[0]), len(пиксели)), pygame.SRCALPHA)
    for y, ред in enumerate(пиксели):
        for x, ц in enumerate(ред):
            if ц:
                s.set_at((x, y), към_палитра(ц))
    return s


def плоско(cv, x0, y0, x1, y1, ц, z, pid=950):
    for y in range(int(y0), int(y1)):
        for x in range(int(x0), int(x1)):
            cv.plot(x, y, ц, z, pid)


# ---------- под ----------
def трева(семе):
    """Трева: равен зелен цвят, стръкчета и малко цветчета. Повтаря се без шев (нищо до ръба)."""
    сл = random.Random(семе)
    s = pygame.Surface((64, 64))
    s.fill(GRASS[1][:3])
    for _ in range(36):                                               # петна по-тъмна трева
        x, y = сл.randrange(64), сл.randrange(64)
        for dx in range(сл.randint(2, 5)):
            s.set_at(((x + dx) % 64, y), GRASS[2][:3])
    for _ in range(26):                                               # стръкчета: светло отгоре, тъмно отдолу
        x, y = сл.randrange(64), сл.randrange(64)
        s.set_at((x, y), GRASS[0][:3])
        s.set_at((x, (y + 1) % 64), GRASS[2][:3])
    if семе % 2:
        for _ in range(3):                                            # цветчета
            x, y = сл.randrange(2, 62), сл.randrange(2, 62)
            ц = сл.choice(((255, 255, 255), (255, 220, 80), (240, 120, 170)))
            for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                s.set_at((x + dx, y + dy), ц)
            s.set_at((x, y), (255, 200, 60))
    return s


def калдъръм():
    """Калдъръм: заоблени камъни с тъмни фуги."""
    сл = random.Random(7)
    cv = Canvas(64, 64)
    плоско(cv, 0, 0, 64, 64, STONE[3], 0)
    for ред in range(5):
        y = ред * 13 + 6
        отм = (ред % 2) * 8
        for к in range(-1, 5):
            x = к * 16 + отм + 8
            ellipse(cv, x % 64, y, 7 + сл.random(), 5.5, STONE, 1 + сл.random() * 0.01)
            if x % 64 > 56:
                ellipse(cv, x % 64 - 64, y, 7, 5.5, STONE, 1)
    s = повърхност([[ц for ц in ред] for ред in cv.col])
    return s


# ---------- сгради ----------
def прозорец(cv, x, y, ш, в, z, капаци=BLUE):
    пр(cv, x - 3, y - 2, x + ш + 3, y + в + 3, WOOD2, z)              # рамка
    пр(cv, x, y, x + ш, y + в, GLASS, z + 0.1)
    for yy in range(y, y + в):                                         # кръстът
        cv.plot(x + ш // 2, yy, WOOD2[2], z + 0.2, 951)
    for xx in range(x, x + ш):
        cv.plot(xx, y + в // 2, WOOD2[2], z + 0.2, 951)
    for k in range(3):                                                 # отблясък
        cv.plot(x + 2 + k, y + 2, WHITE, z + 0.3, 952)
    пр(cv, x - 3 - ш // 2, y - 2, x - 3, y + в + 3, капаци, z + 0.05)  # капаци
    пр(cv, x + ш + 3, y - 2, x + ш + 3 + ш // 2, y + в + 3, капаци, z + 0.05)
    пр(cv, x - 5, y + в + 3, x + ш + 5, y + в + 6, WOOD, z + 0.4)      # перваз


def врата(cv, x, y, ш, в, z):
    poly(cv, [(x, y + 6), (x + ш // 2, y), (x + ш, y + 6), (x + ш, y + в), (x, y + в)], WOOD2, z)
    for xx in range(x + 4, x + ш, 5):                                  # дъски
        for yy in range(y + 5, y + в):
            cv.plot(xx, yy, WOOD2[3], z + 0.1, 953)
    ellipse(cv, x + ш - 5, y + в // 2 + 2, 1.6, 1.6, M('#fff0a0', '#f2cc2e', '#c89a18', '#8a660c'), z + 0.2)   # дръжка
    пр(cv, x - 2, y + в, x + ш + 2, y + в + 4, STONE, z + 0.3)        # праг


def покрив(cv, x0, x1, долу, горе, z, мат=ROOF):
    """Керемиден покрив: трапец с редове керемиди, сянка под стряхата."""
    навес = 10
    poly(cv, [(x0 - навес, долу), (x0 + 22, горе), (x1 - 22, горе), (x1 + навес, долу)], мат, z)
    сл = random.Random(x0 + долу)
    for y in range(горе + 6, долу, 7):                                  # редове керемиди
        к = (y - горе) / max(1, долу - горе)
        л, д = x0 + 22 - (32 * к), x1 - 22 + (32 * к)
        for x in range(int(л), int(д)):
            cv.plot(x, y, мат[3], z + 0.1, 954)
        for x in range(int(л) + (y // 7 % 2) * 4, int(д), 8):
            cv.plot(x, y - 1, мат[3], z + 0.1, 954)
            cv.plot(x, y - 2, мат[2], z + 0.1, 954)
    for x in range(x0 - навес, x1 + навес):                             # ръб на стряхата
        cv.plot(x, долу, мат[3], z + 0.2, 955)
        cv.plot(x, долу + 1, OUT, z + 0.2, 955)


def комин(cv, x, y, z):
    пр(cv, x, y, x + 12, y + 26, M('#f0a070', '#c86a40', '#9a4a2a', '#6a2e18'), z)
    пр(cv, x - 2, y - 3, x + 14, y + 1, STONE, z + 0.1)


def къща(вариант):
    cv = Canvas(256, 256)
    стена = PLASTER if вариант == 0 else M('#fff4d8', '#f6e2b0', '#dcc488', '#b09860')
    капаци = BLUE if вариант == 0 else M('#a8e090', '#5aa848', '#3a7a30', '#22521e')
    пр(cv, 18, 130, 238, 254, стена, 1)                               # стената
    for x in range(18, 238):                                          # сянка отдясно и долу (каменна основа)
        for y in range(240, 254):
            cv.plot(x, y, STONE[2] if (x // 9 + y // 7) % 2 else STONE[1], 1.1, 956)
    for y in range(130, 240):
        for x in range(214, 238):
            cv.plot(x, y, стена[2], 1.05, 957)
    for x in range(18, 238):                                          # сянка под стряхата
        for y in range(130, 136):
            cv.plot(x, y, стена[3], 1.06, 957)
    прозорец(cv, 50, 160, 30, 34, 2, капаци)
    прозорец(cv, 178, 160, 30, 34, 2, капаци)
    врата(cv, 110, 178, 36, 62, 2)
    покрив(cv, 18, 238, 132, 48, 3)
    комин(cv, 176 if вариант == 0 else 60, 30, 2.5)
    for x in range(98, 158, 6):                                       # саксии с мушката отпред
        pass
    ellipse(cv, 58, 236, 8, 5, M('#f0a070', '#c86a40', '#9a4a2a', '#6a2e18'), 3)
    ellipse(cv, 58, 229, 7, 5, RED, 3.1)
    ellipse(cv, 198, 236, 8, 5, M('#f0a070', '#c86a40', '#9a4a2a', '#6a2e18'), 3)
    ellipse(cv, 198, 229, 7, 5, RED, 3.1)
    return повърхност(finish(cv, OUT, inner=False))


def кръчма_отвън():
    cv = Canvas(384, 256)
    for y in range(120, 254):                                          # каменна сграда
        for x in range(14, 370):
            ред = (y - 120) // 12
            отм = (ред % 2) * 14
            шев = (y - 120) % 12 == 0 or (x + отм) % 28 == 0
            к = (x - 14) / 356
            мат = STONE[3] if шев else (STONE[1] if к < 0.75 else STONE[2])
            if not шев and ((x + отм) % 28 < 3 and (y - 120) % 12 < 3):
                мат = STONE[0]
            cv.plot(x, y, мат, 1, 958)
    for x in range(14, 370):
        for y in range(120, 127):
            cv.plot(x, y, STONE[3], 1.05, 958)
    прозорец(cv, 50, 160, 34, 36, 2, M('#f0c878', '#c8963c', '#9a6a24', '#6a4414'))
    прозорец(cv, 300, 160, 34, 36, 2, M('#f0c878', '#c8963c', '#9a6a24', '#6a4414'))
    for (x, y) in ((54, 164), (304, 164)):                             # топла светлина вътре
        for yy in range(y, y + 14):
            for xx in range(x, x + 12):
                cv.plot(xx, yy, hx('#ffe28a'), 2.15, 959)
    врата(cv, 168, 172, 48, 70, 2)                                     # двукрила врата отдолу в средата
    for yy in range(178, 242):
        cv.plot(192, yy, WOOD2[3], 2.15, 953)
    покрив(cv, 14, 370, 122, 40, 3)
    комин(cv, 300, 22, 2.5)
    # табелата „КРЪЧМА“ на конзола над вратата
    пр(cv, 132, 86, 252, 116, WOOD, 4)
    пр(cv, 136, 90, 248, 112, WOOD2, 4.1)
    for x in (140, 244):
        пр(cv, x - 1, 76, x + 1, 88, M('#7a7880', '#4a4850', '#302e36', '#1a1820'), 3.9)
    # фенери от двете страни на вратата
    for x in (150, 234):
        пр(cv, x - 4, 150, x + 4, 162, M('#ffe890', '#ffd040', '#e0a020', '#a06a10'), 4)
        пр(cv, x - 5, 148, x + 5, 150, M('#7a7880', '#4a4850', '#302e36', '#1a1820'), 4.1)
    s = повърхност(finish(cv, OUT, inner=False))
    шрифт = pygame.font.SysFont("dejavusans,arial", 15, bold=True)          # надписът на табелата
    т = шрифт.render("КРЪЧМА", False, (255, 226, 140))
    с = шрифт.render("КРЪЧМА", False, (40, 24, 12))
    s.blit(с, с.get_rect(center=(193, 102)))
    s.blit(т, т.get_rect(center=(192, 101)))
    return s


def сергия():
    cv = Canvas(128, 128)
    for x in (10, 116):                                                 # подпори
        пр(cv, x - 2, 30, x + 2, 120, WOOD2, 1)
    пр(cv, 6, 78, 122, 92, WOOD, 2)                                    # тезгях
    пр(cv, 10, 92, 118, 124, WOOD2, 1.5)
    for xx in range(14, 118, 12):
        for yy in range(94, 124):
            cv.plot(xx, yy, WOOD2[3], 1.6, 960)
    сл = random.Random(3)
    стоки = (M('#ff9a80', '#ea3e30', '#b42222', '#781414'), M('#ffd090', '#f08a2a', '#c85e14', '#8a3a0c'),
             M('#fff0c0', '#f4e0a0', '#d8b870', '#a88840'), M('#c0ec90', '#70bc40', '#40902c', '#265c1c'))
    for к, мат in enumerate(стоки):                                     # щайги със стоки
        x = 16 + к * 26
        пр(cv, x, 66, x + 22, 80, WOOD, 2.5)
        for _ in range(6):
            ellipse(cv, x + сл.uniform(4, 18), сл.uniform(63, 68), 3.4, 3, мат, 2.6 + сл.random() * 0.01)
    for к in range(8):                                                  # раиран навес
        мат = RED if к % 2 == 0 else PLASTER
        poly(cv, [(4 + к * 15, 30), (19 + к * 15, 30), (21 + к * 15, 46), (2 + к * 15, 46)], мат, 3)
    for к in range(8):                                                  # фестон
        ellipse(cv, 11 + к * 15, 46, 7.5, 4, RED if к % 2 == 0 else PLASTER, 3.1)
    return повърхност(finish(cv, OUT, inner=False))


def кладенец():
    cv = Canvas(64, 112)
    for x in (12, 52):
        пр(cv, x - 2, 30, x + 2, 84, WOOD2, 1)
    poly(cv, [(4, 36), (32, 14), (60, 36)], ROOF, 2)                   # покривче
    пр(cv, 12, 46, 52, 49, WOOD, 1.5)                                   # макара
    for y in range(49, 74):
        cv.plot(32, y, hx('#8a6a40'), 1.6, 961)
    пр(cv, 28, 72, 36, 80, WOOD2, 1.7)                                  # кофата
    ellipse(cv, 32, 86, 26, 9, STONE, 2.5)                              # каменният пръстен
    пр(cv, 6, 86, 58, 106, STONE, 2.4)
    ellipse(cv, 32, 106, 26, 6, STONE, 2.3)
    ellipse(cv, 32, 86, 20, 5.5, WATER, 2.6)
    for y in range(90, 108, 6):
        for x in range(8, 58):
            cv.plot(x, y, STONE[3], 2.45, 962)
    return повърхност(finish(cv, OUT, inner=False))


def дърво():
    cv = Canvas(128, 160)
    capsule(cv, (64, 156), (64, 96), 9, 6, WOOD2, 1)                    # стволът
    сл = random.Random(5)
    for (x, y, r) in ((64, 66, 38), (38, 84, 26), (90, 84, 26), (50, 46, 26), (80, 44, 26), (64, 30, 22)):
        ellipse(cv, x, y, r, r * 0.86, LEAF, 2 + сл.random() * 0.1)
    for _ in range(30):                                                 # листа - по-светли петна откъм светлината
        x, y = сл.uniform(24, 100), сл.uniform(18, 100)
        cv.plot(int(x), int(y), LEAF[0], 3, 963)
    for (x, y) in ((50, 70), (80, 60), (66, 88), (42, 52)):             # ябълки
        ellipse(cv, x, y, 2.6, 2.6, RED, 3.1)
    ellipse(cv, 64, 157, 30, 4, M('#4a8a2e', '#3e7426', '#2e5a1e', '#1e4014'), 0.5)   # сянката
    return повърхност(finish(cv, OUT, inner=False))


def ограда():
    cv = Canvas(64, 64)
    for x in (8, 32, 56):
        poly(cv, [(x - 4, 60), (x - 4, 22), (x, 16), (x + 4, 22), (x + 4, 60)], WOOD, 1)
    пр(cv, 0, 28, 64, 34, WOOD2, 1.5)
    пр(cv, 0, 46, 64, 52, WOOD2, 1.5)
    return повърхност(finish(cv, OUT, inner=False))


def цветя():
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    сл = random.Random(9)
    for _ in range(9):
        x, y = сл.randrange(8, 56), сл.randrange(14, 58)
        pygame.draw.line(s, GRASS[3][:3], (x, y), (x, y + 6))
        ц = сл.choice(((255, 255, 255), (255, 210, 60), (240, 110, 160), (230, 60, 50)))
        for dx, dy in ((0, -2), (-2, 0), (2, 0), (0, 2), (-1, -1), (1, 1), (1, -1), (-1, 1)):
            s.set_at((x + dx, y + dy), ц)
        s.set_at((x, y), (255, 210, 60))
    return s


# ---------- фермата и магазинът (28.11.2026) ----------
SOIL = M('#b88a5a', '#8e6438', '#6a4624', '#462c14')
CROP = {"domat": M('#ff9a80', '#ea3e30', '#b42222', '#781414'), "krastavitsa": M('#c0ec90', '#70bc40', '#40902c', '#265c1c'),
        "chushki": M('#ff9a80', '#e0302a', '#a81e1e', '#701414'), "luk": M('#fff4d0', '#f4e0a0', '#d8b870', '#a88840'),
        "morkov": M('#ffc070', '#f08a2a', '#c85e14', '#8a3a0c')}


def нива():
    """Изорана земя на бразди."""
    s = pygame.Surface((64, 64))
    s.fill(SOIL[1][:3])
    for y in range(4, 64, 10):
        pygame.draw.rect(s, SOIL[3][:3], (0, y + 6, 64, 2))
        pygame.draw.rect(s, SOIL[0][:3], (0, y, 64, 1))
    сл = random.Random(11)
    for _ in range(20):
        s.set_at((сл.randrange(64), сл.randrange(64)), SOIL[2][:3])
    return s


def растение(култура, етап, мъртво=False):
    """Растение на нивата: 0 кълн, 1 младо, 2 голямо, 3 узряло (с плодове)."""
    cv = Canvas(64, 64)
    лист = M('#a8a070', '#8a7a48', '#6a5a30', '#4a3c1c') if мъртво else LEAF
    сл = random.Random(hash(култура) % 100 + етап)
    for к in range(3):                                                   # три растения в браздата
        x = 12 + к * 20
        if култура in ("luk", "morkov"):
            височина = (6, 12, 18, 20)[етап]
            for dx in (-3, 0, 3):
                capsule(cv, (x, 52), (x + dx, 52 - височина), 1.3, 0.8, лист, 1 + к * 0.01)
            if етап == 3 and not мъртво:
                ellipse(cv, x, 53, 5, 4, CROP[култура], 1.5)
        else:
            височина = (6, 14, 24, 26)[етап]
            capsule(cv, (x, 54), (x, 54 - височина), 1.5, 1.2, лист, 1)
            for л in range(етап + 1):
                y = 52 - л * 7
                ellipse(cv, x - 4, y, 3.5, 2.2, лист, 1.1 + л * 0.01)
                ellipse(cv, x + 4, y - 3, 3.5, 2.2, лист, 1.1 + л * 0.01)
            if етап == 3 and not мъртво:
                мат = CROP[култура]
                for (dx, dy) in ((-4, -10), (5, -16), (-2, -20)):
                    if култура == "krastavitsa":
                        capsule(cv, (x + dx, 54 + dy - 4), (x + dx + 1, 54 + dy + 3), 2, 2, мат, 2)
                    elif култура == "chushki":
                        capsule(cv, (x + dx, 54 + dy - 3), (x + dx, 54 + dy + 4), 2.6, 1.4, мат, 2)
                    else:
                        ellipse(cv, x + dx, 54 + dy, 3.4, 3.2, мат, 2)
    return повърхност(finish(cv, OUT, inner=False))


def кокошарник():
    cv = Canvas(128, 160)
    пр(cv, 10, 70, 118, 150, WOOD2, 1)                                   # дървена къщичка
    for x in range(14, 118, 8):
        for y in range(72, 150):
            cv.plot(x, y, WOOD2[3], 1.1, 964)
    покрив(cv, 10, 118, 72, 40, 2)
    пр(cv, 52, 112, 76, 150, M('#4a3020', '#3a2418', '#2a1a10', '#1a0e08'), 1.5)   # вратичка
    пр(cv, 60, 150, 90, 154, WOOD, 1.6)                                   # стълбичка
    for (x, y, бяла) in ((24, 150, True), (98, 148, False), (88, 156, True)):   # кокошки
        мат = PLASTER if бяла else M('#f0b070', '#c87a3a', '#9a5226', '#6a3418')
        ellipse(cv, x, y, 7, 5.5, мат, 3)
        ellipse(cv, x + 6, y - 5, 3.4, 3.4, мат, 3.1)
        cv.plot(x + 9, y - 5, hx('#f2cc2e'), 3.2, 965)
        cv.plot(x + 6, y - 9, RED[1], 3.2, 965); cv.plot(x + 7, y - 9, RED[1], 3.2, 965)
        cv.plot(x + 7, y - 6, OUT, 3.2, 965)
    return повърхност(finish(cv, OUT, inner=False))


def крава():
    cv = Canvas(128, 112)
    КОЖА = M('#ffffff', '#f2eee6', '#d4ccbc', '#a8a090')
    ПЕТНО = M('#6a5a50', '#4a3e38', '#342a26', '#201816')
    for x in (34, 46, 84, 96):                                           # краката
        capsule(cv, (x, 80), (x, 106), 4, 3.5, КОЖА, 1)
        пр(cv, x - 4, 104, x + 4, 108, ПЕТНО, 1.2)
    ellipse(cv, 66, 70, 42, 22, КОЖА, 2)                                  # тялото
    for (x, y, r) in ((52, 64, 9), (80, 74, 8), (70, 58, 6)):            # петна
        ellipse(cv, x, y, r, r * 0.8, ПЕТНО, 2.1)
    ellipse(cv, 72, 88, 8, 5, M('#ffd0d8', '#f0a8b4', '#d08494', '#a06070'), 2.2)   # виме
    ellipse(cv, 20, 58, 14, 12, КОЖА, 3)                                  # главата
    ellipse(cv, 14, 64, 8, 6, M('#ffd0d8', '#f0a8b4', '#d08494', '#a06070'), 3.1)   # муцуната
    for x in (12, 28):
        capsule(cv, (x, 48), (x + (-4 if x < 20 else 4), 40), 1.6, 1, M('#fff4d0', '#e8d8a8', '#c8b480', '#988458'), 2.9)
    cv.plot(16, 54, OUT, 3.2, 966); cv.plot(25, 54, OUT, 3.2, 966)
    ellipse(cv, 20, 76, 3, 3, M('#fff0a0', '#f2cc2e', '#c89a18', '#8a660c'), 3.3)   # звънче
    capsule(cv, (106, 64), (114, 86), 1.5, 1, КОЖА, 1.8)                  # опашка
    return повърхност(finish(cv, OUT, inner=False))


def магазин_отвън():
    cv = Canvas(256, 256)
    пр(cv, 14, 120, 242, 254, M('#e8f0f8', '#c8d8e8', '#a0b4c8', '#7088a0'), 1)   # синкава мазилка
    for x in range(14, 242):
        for y in range(240, 254):
            cv.plot(x, y, STONE[2] if (x // 9 + y // 7) % 2 else STONE[1], 1.1, 956)
    прозорец(cv, 30, 150, 50, 56, 2, M('#f0c878', '#c8963c', '#9a6a24', '#6a4414'))   # витрини
    прозорец(cv, 176, 150, 50, 56, 2, M('#f0c878', '#c8963c', '#9a6a24', '#6a4414'))
    for (x, y, мат) in ((36, 186, CROP["domat"]), (48, 188, CROP["morkov"]), (62, 186, CROP["krastavitsa"]),
                        (184, 186, M('#fff8e0', '#f6e6b8', '#dcc48a', '#b09860')), (200, 188, CROP["luk"]), (214, 186, CROP["domat"])):
        ellipse(cv, x, y, 4, 3.4, мат, 2.3)
    врата(cv, 110, 176, 36, 64, 2)
    for к in range(10):                                                   # раиран навес над вратата и витрините
        мат = M('#9ad0f0', '#4a90c8', '#2e6aa0', '#1c4470') if к % 2 == 0 else PLASTER
        poly(cv, [(14 + к * 23, 120), (37 + к * 23, 120), (40 + к * 23, 138), (11 + к * 23, 138)], мат, 3)
    for к in range(10):
        ellipse(cv, 25 + к * 23, 138, 11, 4, M('#9ad0f0', '#4a90c8', '#2e6aa0', '#1c4470') if к % 2 == 0 else PLASTER, 3.1)
    покрив(cv, 14, 242, 122, 52, 2.5, M('#c8d0d8', '#9aa4b0', '#6e7884', '#4a525c'))   # ламаринен покрив
    пр(cv, 70, 82, 186, 108, WOOD, 4)                                    # табела
    пр(cv, 74, 86, 182, 104, M('#9ad0f0', '#4a90c8', '#2e6aa0', '#1c4470'), 4.1)
    s = повърхност(finish(cv, OUT, inner=False))
    шрифт = pygame.font.SysFont("dejavusans,arial", 14, bold=True)
    т = шрифт.render("МАГАЗИН", False, (255, 250, 230))
    s.blit(шрифт.render("МАГАЗИН", False, (20, 30, 60)), т.get_rect(center=(129, 96)))
    s.blit(т, т.get_rect(center=(128, 95)))
    return s


def главна_ферма():
    папка = os.path.join(обща.ИГРА, "assets")
    pygame.image.save(нива(), os.path.join(папка, "niva.png"))
    pygame.image.save(кокошарник(), os.path.join(папка, "kokoshkarnik.png"))
    pygame.image.save(крава(), os.path.join(папка, "krava.png"))
    pygame.image.save(магазин_отвън(), os.path.join(папка, "magazin_out.png"))
    os.makedirs(os.path.join(папка, "rasteniya"), exist_ok=True)
    for култура in CROP:
        for етап in range(4):
            pygame.image.save(растение(култура, етап), os.path.join(папка, "rasteniya", "%s_%d.png" % (култура, етап)))
        pygame.image.save(растение(култура, 2, True), os.path.join(папка, "rasteniya", "%s_mrtvo.png" % култура))
    print("assets/niva.png, kokoshkarnik.png, krava.png, magazin_out.png, rasteniya/*.png")


# ---------- църквата (28.11.2026) ----------
def църква():
    """Църква от бял (варовиков) камък, по снимките на учителя: отпред портик с три стрелковидни арки
    на кръгли колони, над портика три малки оловни купола, отзад голям купол на барабан със златен кръст.
    5x4 клетки (320x352 с куполите)."""
    W, H = 320, 352
    cv = Canvas(W, H)
    КАМЪК = M('#fbf6e8', '#efe6d0', '#d9ccae', '#b3a383')        # бял камък
    ФУГА = hx('#c2b494')
    ОЛОВО = M('#a4a8b0', '#7c8088', '#5a5e66', '#3c3f46')       # оловните куполи
    ЗЛАТО = M('#fff2a8', '#f2cc2e', '#c89a18', '#8a660c')
    ЧЕРВЕНО = M('#c85040', '#9a3226', '#72221a', '#4a140e')      # дограмата и вратата
    СЯНКА = M('#d6ccb4', '#bfb398', '#a39778', '#7e7258')        # вътре в портика (в сянка)
    сл = random.Random(31)

    def стена(x0, y0, x1, y1, z, мат=КАМЪК, светло_от=None):
        """Зидария от дялани блокове: редове с различна дължина на камъните, тънки фуги, лек тон."""
        ред_в = 9
        for y in range(y0, y1):
            ред = (y - y0) // ред_в
            сл2 = random.Random(ред * 7 + x0)
            ръбове, x = [], x0 - сл2.randint(0, 18)
            while x < x1:
                ръбове.append(x)
                x += сл2.randint(16, 30)
            for x in range(x0, x1):
                к = (x - x0) / max(1, x1 - x0)
                тон = мат[0] if к < 0.18 else мат[1] if к < 0.8 else мат[2]
                if (y - y0) % ред_в == 0 or x in ръбове:
                    ц = ФУГА
                elif (x * 7 + ред * 13) % 23 == 0:
                    ц = мат[2]                                          # петънце в камъка
                else:
                    ц = тон
                cv.plot(x, y, ц, z, 980)

    def купол(cx, долу, r, височина, z, кръст=False):
        """Оловен купол (полусфера) с ребра, светъл отляво; на върха - златна топка (и кръст)."""
        for y in range(долу - височина, долу + 1):
            t = (долу - y) / max(1, височина)
            полу = r * math.sqrt(max(0.0, 1 - t * t))
            for x in range(int(cx - полу), int(cx + полу) + 1):
                nx = (x - cx) / max(1, полу)
                b = -0.75 * nx + 0.5 * t - 0.15
                ц = ОЛОВО[0] if b > 0.45 else ОЛОВО[1] if b > 0.0 else ОЛОВО[2] if b > -0.45 else ОЛОВО[3]
                if r > 30 and int((x - cx) / max(1, полу) * 6 + 6) != int((x + 1 - cx) / max(1, полу) * 6 + 6):
                    ц = ОЛОВО[3] if b < 0.3 else ОЛОВО[2]               # ребрата на големия купол
                cv.plot(x, y, ц, z, 981)
        for x in range(int(cx - r - 1), int(cx + r + 2)):                 # корнизът под купола
            cv.plot(x, долу + 1, КАМЪК[2], z + 0.1, 982)
            cv.plot(x, долу + 2, КАМЪК[3], z + 0.1, 982)
        върх = долу - височина
        if кръст:
            ellipse(cv, cx, върх - 3, 3.5, 3.5, ЗЛАТО, z + 0.3)
            ellipse(cv, cx, върх - 9, 2.2, 2.2, ЗЛАТО, z + 0.3)
            for y in range(върх - 34, върх - 9):
                cv.plot(int(cx), y, ЗЛАТО[1], z + 0.4, 983); cv.plot(int(cx) + 1, y, ЗЛАТО[2], z + 0.4, 983)
            for x in range(int(cx) - 8, int(cx) + 10):                     # напречната греда на кръста
                for d in range(3):
                    cv.plot(x, върх - 25 + d, ЗЛАТО[1] if d < 2 else ЗЛАТО[2], z + 0.5, 983)
            for x in range(int(cx) - 5, int(cx) + 7):                      # долната наклонена греда
                cv.plot(x, върх - 16 + (x - int(cx)) // 4, ЗЛАТО[2], z + 0.5, 983)
        else:
            ellipse(cv, cx, върх - 2, 2.4, 2.4, ЗЛАТО, z + 0.3)

    def прозорец_стрела(x, y, ш, в, z):
        """Тесен прозорец със заострен (стрелковиден) връх и червеникава дограма."""
        poly(cv, [(x - 2, y + в), (x - 2, y + ш // 2), (x + ш // 2, y - 4), (x + ш + 2, y + ш // 2), (x + ш + 2, y + в)], КАМЪК, z)
        poly(cv, [(x, y + в), (x, y + ш // 2), (x + ш // 2, y - 1), (x + ш, y + ш // 2), (x + ш, y + в)], ЧЕРВЕНО, z + 0.1)
        poly(cv, [(x + 2, y + в - 2), (x + 2, y + ш // 2 + 1), (x + ш // 2, y + 2), (x + ш - 2, y + ш // 2 + 1), (x + ш - 2, y + в - 2)],
             M('#5a6a82', '#3e4c62', '#2a3446', '#1a202c'), z + 0.2)
        for yy in range(y + 4, y + в - 2):                                  # кръстчето на дограмата
            cv.plot(x + ш // 2, yy, ЧЕРВЕНО[1], z + 0.3, 984)
        for xx in range(x + 2, x + ш - 1):
            cv.plot(xx, y + в // 2 + 3, ЧЕРВЕНО[1], z + 0.3, 984)
        cv.plot(x + 3, y + ш // 2 + 2, hx('#c8d8ec'), z + 0.4, 984)

    # ---------- задната (високата) част: барабан и голям купол ----------
    стена(70, 112, 250, 176, 1)                                            # високият неф зад портика
    for x in range(66, 254):
        cv.plot(x, 112, КАМЪК[3], 1.2, 985); cv.plot(x, 113, КАМЪК[2], 1.2, 985)
    стена(110, 62, 210, 112, 1.5)                                          # барабанът
    for x in range(106, 214):
        cv.plot(x, 62, КАМЪК[3], 1.6, 985)
    ellipse(cv, 160, 88, 7, 7, КАМЪК, 1.7)                                 # кръгъл прозорец (окулус)
    ellipse(cv, 160, 88, 4.5, 4.5, M('#5a6a82', '#3e4c62', '#2a3446', '#1a202c'), 1.8)
    купол(160, 60, 52, 40, 2, кръст=True)
    for cx in (82, 238):                                                   # малки ъглови куполи на нефа
        стена(cx - 12, 98, cx + 12, 112, 1.3)
        купол(cx, 97, 15, 13, 1.4)

    # ---------- предната част: портикът ----------
    стена(10, 176, 310, 352, 3)                                            # фасадата (зад арките)
    for x in range(6, 314):                                                # корнизът над арките
        cv.plot(x, 172, КАМЪК[3], 4.6, 986); cv.plot(x, 173, КАМЪК[2], 4.6, 986)
        cv.plot(x, 174, КАМЪК[1], 4.6, 986); cv.plot(x, 175, КАМЪК[3], 4.6, 986)
    for cx in (60, 160, 260):                                              # три малки купола над портика
        купол(cx, 170, 34, 26, 4.5)
    колони = (12, 108, 212, 302)
    for и in range(3):                                                     # трите стрелковидни арки
        л, д = колони[и] + 10, колони[и + 1]
        ср = (л + д) / 2
        for y in range(186, 350):                                          # вътрешността (в сянка)
            for x in range(л, д):
                if y < 240:                                                # стрелковидният връх
                    t = (240 - y) / 54.0
                    if abs(x - ср) > (д - л) / 2 * math.sqrt(max(0.0, 1 - t * t)) * (1 - 0.25 * t):
                        continue
                тон = СЯНКА[1] if x < ср + 10 else СЯНКА[2]
                if (y - 186) % 9 == 0 or (x + (y // 9) * 11) % 24 == 0:
                    тон = СЯНКА[3]
                cv.plot(x, y, тон, 3.5, 987)
    # вратата (червена, със стрелковиден връх) и прозорците в портика
    poly(cv, [(146, 350), (146, 300), (160, 284), (174, 300), (174, 350)], КАМЪК, 3.6)
    poly(cv, [(149, 350), (149, 302), (160, 289), (171, 302), (171, 350)], ЧЕРВЕНО, 3.7)
    for y in range(300, 350, 10):
        for x in range(150, 171):
            cv.plot(x, y, ЧЕРВЕНО[3], 3.8, 988)
    for y in range(292, 350):
        cv.plot(160, y, ЧЕРВЕНО[3], 3.8, 988)
    прозорец_стрела(48, 262, 18, 42, 3.6)
    прозорец_стрела(254, 262, 18, 42, 3.6)
    прозорец_стрела(152, 222, 16, 40, 3.6)
    for x0 in (34, 220):                                                   # пейките под портика
        пр(cv, x0, 326, x0 + 66, 331, WOOD, 3.9)
        пр(cv, x0, 316, x0 + 66, 320, WOOD2, 3.9)
        for x in (x0 + 4, x0 + 60):
            пр(cv, x, 331, x + 3, 340, M('#4a90c8', '#2e6aa0', '#1c4470', '#102a48'), 3.95)
    # колоните (кръгли, светли отляво) с капители и бази
    for x in колони:
        for y in range(182, 346):
            for dx in range(10):
                nx = (dx - 4.5) / 5.0
                b = -0.8 * nx + 0.1
                cv.plot(x + dx, y, КАМЪК[0] if b > 0.4 else КАМЪК[1] if b > -0.1 else КАМЪК[2] if b > -0.5 else КАМЪК[3], 5, 989)
        пр(cv, x - 3, 176, x + 13, 183, КАМЪК, 5.1)                       # капител
        пр(cv, x - 3, 344, x + 13, 351, КАМЪК, 5.1)                       # база
    for и in range(3):                                                     # ръбът на арките
        л, д = колони[и] + 10, колони[и + 1]
        ср = (л + д) / 2
        for k in range(200):
            t = k / 199.0
            ъгъл = math.pi * t
            x = ср - (д - л) / 2 * math.cos(ъгъл)
            y = 240 - 54 * math.sin(ъгъл) * (1 - 0.1 * abs(math.cos(ъгъл)))
            if y > 240:
                continue
            for d in range(3):
                cv.plot(int(x), int(y) - d, КАМЪК[0] if d < 2 else КАМЪК[3], 5.2, 990)
    for x in (30, 290):                                                    # медните водосточни тръби
        for y in range(176, 350):
            cv.plot(x, y, hx('#c8823c'), 5.3, 991)
    пр(cv, 0, 346, 320, 352, КАМЪК, 5.4)                                   # стъпалото пред портика
    return повърхност(finish(cv, OUT, inner=False))


def камбанария():
    """Камбанарията: дървена кула с три камбани. 2x1 клетки (128x288)."""
    cv = Canvas(128, 288)
    for x in (22, 104):
        пр(cv, x - 6, 90, x + 6, 286, WOOD2, 1)
    for y in (150, 210, 270):
        пр(cv, 16, y, 112, y + 6, WOOD, 1.2)
    for x in range(20, 108):                                               # кръстосани греди
        y = 150 + (x - 20) * 60 // 88
        cv.plot(x, y, WOOD2[2], 1.1, 974); cv.plot(x, y + 1, WOOD2[3], 1.1, 974)
    poly(cv, [(4, 92), (64, 26), (124, 92)], ROOF, 2)                     # покривчето
    for (x, r) in ((40, 11), (64, 15), (88, 9)):                          # камбаните
        poly(cv, [(x - r * 0.5, 100), (x + r * 0.5, 100), (x + r, 100 + r * 1.5), (x - r, 100 + r * 1.5)],
             M('#ffe090', '#e0a83a', '#a8741c', '#6a4810'), 3)
        ellipse(cv, x, 100 + r * 1.5, r, 3, M('#ffe090', '#e0a83a', '#a8741c', '#6a4810'), 3.1)
        ellipse(cv, x, 100 + r * 1.5 + 4, 2.5, 2.5, M('#8a8890', '#58565e', '#38363e', '#1e1c22'), 3.2)
        for y in range(92, 100):
            cv.plot(x, y, OUT, 2.9, 975)
    for y in range(120, 286):                                              # въжето
        cv.plot(64, y, hx('#d8b888'), 3.3, 976)
    for x in range(26, 34):                                                # кръстче на върха
        cv.plot(x + 34, 14, hx('#f2cc2e'), 4, 977)
    for y in range(6, 26):
        cv.plot(64, y, hx('#f2cc2e'), 4, 977)
    return повърхност(finish(cv, OUT, inner=False))


def иконостас():
    """Дървен резбован иконостас с икони: 6x2 клетки (384x192)."""
    cv = Canvas(384, 192)
    пр(cv, 4, 20, 380, 190, M('#e8b870', '#c08a40', '#8e5e24', '#5e3a12'), 1)
    for x in range(4, 380):                                                # позлатен корниз
        for y in range(20, 30):
            cv.plot(x, y, hx('#f2cc2e') if (x // 6) % 2 else hx('#c89a18'), 1.1, 978)
    poly(cv, [(160, 190), (160, 90), (192, 60), (224, 90), (224, 190)], M('#fff0a0', '#f2cc2e', '#c89a18', '#8a660c'), 2)   # царските двери
    for к, x in enumerate((24, 84, 252, 312)):                             # иконите
        пр(cv, x, 50, x + 48, 120, M('#fff0a0', '#f2cc2e', '#c89a18', '#8a660c'), 2)
        пр(cv, x + 4, 54, x + 44, 116, (M('#9ad0f0', '#4a90c8', '#2e6aa0', '#1c4470') if к % 2 else RED), 2.1)
        ellipse(cv, x + 24, 72, 9, 9, M('#fff0a0', '#f2cc2e', '#c89a18', '#8a660c'), 2.2)          # ореол
        ellipse(cv, x + 24, 73, 5, 6, M('#f8d8b8', '#e8b890', '#c89070', '#9a6a50'), 2.3)         # лице
        poly(cv, [(x + 14, 116), (x + 18, 86), (x + 30, 86), (x + 34, 116)], (RED if к % 2 else M('#9ad0f0', '#4a90c8', '#2e6aa0', '#1c4470')), 2.3)
    for x in range(4, 380, 32):                                            # резба отдолу
        ellipse(cv, x + 16, 160, 10, 14, M('#c08a40', '#8e5e24', '#6a4418', '#46280c'), 1.5)
    return повърхност(finish(cv, OUT, inner=False))


def свещник():
    """Свещник с пясък и свещи: 1x1 (64x96)."""
    cv = Canvas(64, 96)
    пр(cv, 28, 50, 36, 92, M('#fff0a0', '#f2cc2e', '#c89a18', '#8a660c'), 1)
    ellipse(cv, 32, 92, 14, 4, M('#fff0a0', '#f2cc2e', '#c89a18', '#8a660c'), 1.1)
    ellipse(cv, 32, 48, 26, 8, M('#fff0a0', '#f2cc2e', '#c89a18', '#8a660c'), 2)
    ellipse(cv, 32, 46, 22, 5, M('#f4e0b0', '#e0c890', '#c8a870', '#a08850'), 2.1)   # пясъкът
    for (x, в) in ((16, 14), (26, 20), (36, 16), (46, 12)):                # свещите
        пр(cv, x - 1, 46 - в, x + 2, 46, M('#fff8e0', '#f6e6b8', '#dcc48a', '#b09860'), 2.2)
        ellipse(cv, x, 46 - в - 3, 1.6, 3, M('#fff6b0', '#ffd048', '#f88a24', '#d43c1a'), 2.3)
    return повърхност(finish(cv, OUT, inner=False))


def купел():
    """Каменен купел за кръщене: 1x1 (64x80)."""
    cv = Canvas(64, 80)
    пр(cv, 24, 50, 40, 76, STONE, 1)
    ellipse(cv, 32, 76, 16, 4, STONE, 1.1)
    ellipse(cv, 32, 44, 28, 14, STONE, 2)
    ellipse(cv, 32, 40, 26, 9, STONE, 2.1)
    ellipse(cv, 32, 40, 21, 6, WATER, 2.2)
    for x in range(10, 54, 6):
        cv.plot(x, 50, STONE[3], 2.15, 979)
    return повърхност(finish(cv, OUT, inner=False))


def каменен_под():
    сл = random.Random(21)
    s = pygame.Surface((64, 64))
    s.fill(STONE[1][:3])
    for y in (0, 32):
        pygame.draw.line(s, STONE[3][:3], (0, y), (63, y))
        отм = 0 if y == 0 else 16
        for x in (отм, отм + 32):
            pygame.draw.line(s, STONE[3][:3], (x % 64, y), (x % 64, y + 31))
    for _ in range(30):
        s.set_at((сл.randrange(64), сл.randrange(64)), STONE[2][:3])
    for _ in range(12):
        s.set_at((сл.randrange(64), сл.randrange(64)), STONE[0][:3])
    return s


def главна_църква():
    папка = os.path.join(обща.ИГРА, "assets")
    for име, ф in (("tsarkva_out", църква), ("kambanaria", камбанария), ("ikonostas", иконостас),
                   ("svechnik", свещник), ("kupel", купел), ("kamak_pod", каменен_под)):
        pygame.image.save(ф(), os.path.join(папка, име + ".png"))
    print("assets/tsarkva_out.png, kambanaria.png, ikonostas.png, svechnik.png, kupel.png, kamak_pod.png")


def главна():
    pygame.init()
    pygame.display.set_mode((1, 1))
    папка = os.path.join(обща.ИГРА, "assets")
    for име, ф in (("grass", lambda: трева(2)), ("grass2", lambda: трева(3)), ("path", калдъръм),
                   ("house_a", lambda: къща(0)), ("house_b", lambda: къща(1)), ("krachma_out", кръчма_отвън),
                   ("sergia", сергия), ("kladenets", кладенец), ("darvo", дърво), ("ograda", ограда),
                   ("tsvetya", цветя)):
        pygame.image.save(ф(), os.path.join(папка, име + ".png"))
        print("assets/%s.png" % име)
    главна_ферма()
    главна_църква()


if __name__ == "__main__":
    главна()
