# Пиксел-арт за мини игрите при готвенето (Claude): кухнята и анимациите.
# Пускане от папката "Real Life":   python tools/pixelart/make_gotvene_art.py
# Сцената е 320x180 пиксела; играта я уголемява x3 (960x540), за да остане пикселна.
#   assets/minigames/kuhnya_fon.png      фон: стена от дъски, прозорец, низ чушки, рафт, плот
#   assets/minigames/rakia_chasha.png    чашата, кадър k = налято k реда (последният = преляла)
#   assets/minigames/rakia_shishe.png    шишето 80x80: 6 кадъра от изправено до наклонено (+ .json: къде е гърлото)
#   assets/minigames/vino_bachva.png     бъчвата на поставка: канелката затворена / отворена
#   assets/minigames/vino_kancha.png     глинената каничка, кадър k = k реда вино
#   assets/minigames/shopska_daska.png   дъската за рязане
#   assets/minigames/shopska_zelenchuci.png  домат, краставица, чушка, лук x (цял, разрязан, на резени)
#   assets/minigames/shopska_noj.png     ножът: 4 кадъра (горе ... долу)
#   assets/minigames/shopska_kupa.png    купата: 0..8 нарязани, последният кадър със сирене отгоре
#   assets/minigames/bob_ognishte.png    каменното огнище
#   assets/minigames/bob_ogan.png        огънят: малък, среден, голям x 6 кадъра
#   assets/minigames/bob_garne.png       гърнето с чорба: 4 кадъра (мехурчета)
#   assets/minigames/bob_lazhica.png     лъжицата: 8 кадъра (обикаля гърнето)
#   assets/minigames/bob_para.png        пара: 4 кадъра
# За всяка анимация има и art_src/<име>.piskel - отваря се в piskelapp.com (Import), за да я прерисувате.
import base64
import json
import math
import os
import sys

ТУК = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ТУК)
from pix import *
import make_baba as обща
import pygame

ИГРА = обща.ИГРА
ПАПКА = os.path.join(ИГРА, "assets", "minigames")
M = lambda *a: tuple(hx(c) for c in a)
OUT = hx('#24170f')
WOOD = M('#e2aa70', '#b8783f', '#8a5228', '#5a321a')
WOOD_D = M('#a8704a', '#80502e', '#5e3820', '#3e2414')
PLANK = M('#9a6a44', '#7e5436', '#64402a', '#46281a')
GLASS = M('#f4fbff', '#dcf0f8', '#b4d8e6', '#86b4c8')
RAKIA = M('#fff4b8', '#f8de7a', '#e6bc4a', '#bc8e28')
WINE = M('#d04a58', '#a2223a', '#741228', '#4c0818')
CLAY = M('#f0a878', '#cc7c4a', '#9e5632', '#6c3620')
IRON = M('#8a8890', '#58565e', '#38363e', '#1e1c22')
STONE = M('#d8d2c4', '#aea696', '#857d6e', '#5a544a')
GOLD = M('#fff0a0', '#f2cc2e', '#c89a18', '#8a660c')
TOMATO = M('#ff9a80', '#ea3e30', '#b42222', '#781414')
CUC = M('#c0ec90', '#70bc40', '#40902c', '#265c1c')
PEPPER = M('#ffe888', '#f4b828', '#c88412', '#8a5608')
ONION = M('#ffffff', '#f4eee2', '#ddd0bc', '#b0a08a')
CARROT = M('#ffc070', '#f08a2a', '#c85e14', '#8a3a0c')
ENAMEL = M('#ffffff', '#f0eee8', '#d4d0c8', '#a8a49c')
ENAMEL_IN = M('#9a9aa6', '#7a7a88', '#5e5e6c', '#42424e')
RED = M('#ff8a70', '#d83a2a', '#a82420', '#701410')
SOUP = M('#f0b464', '#cc8236', '#9a5a1e', '#6a3a12')
BOWL = M('#ffffff', '#efebe2', '#d0c8b8', '#a49a88')
SIRENE = M('#ffffff', '#fbf8ee', '#ebe4d2', '#cfc6b0')
FIRE = (hx('#fff6b0'), hx('#ffd048'), hx('#f88a24'), hx('#d43c1a'))
WHITE = hx('#ffffff'); GREEN = hx('#3c9a4a'); STEAM = (238, 242, 246, 255)


# ---------- помощни ----------
def повърхност(пиксели):
    s = pygame.Surface((len(пиксели[0]), len(пиксели)), pygame.SRCALPHA)
    for y, ред in enumerate(пиксели):
        for x, ц in enumerate(ред):
            if ц:
                s.set_at((x, y), към_палитра(ц))
    return s


def лента(кадри):
    """Кадри един до друг (хоризонтално)."""
    ш, в = кадри[0].get_size()
    s = pygame.Surface((ш * len(кадри), в), pygame.SRCALPHA)
    for и, к in enumerate(кадри):
        s.blit(к, (и * ш, 0))
    return s


def piskel(име, кадри, описание):
    """Записва art_src/<име>.piskel (отваря се в piskelapp.com с Import)."""
    ш, в = кадри[0].get_size()
    временен = os.path.join(ИГРА, "art_src", "_tmp_%s.png" % име)
    pygame.image.save(лента(кадри), временен)
    with open(временен, "rb") as f:
        данни = f.read()
    os.replace(временен, os.path.join(ИГРА, "art_src", име + "_strip.png"))
    слой = {"name": "Layer 1", "opacity": 1, "frameCount": len(кадри),
            "chunks": [{"layout": [[k] for k in range(len(кадри))],
                        "base64PNG": "data:image/png;base64," + base64.b64encode(данни).decode()}]}
    проект = {"modelVersion": 2, "piskel": {"name": име, "description": описание, "fps": 8,
              "height": в, "width": ш, "layers": [json.dumps(слой)], "hiddenFrames": []}}
    with open(os.path.join(ИГРА, "art_src", име + ".piskel"), "w", encoding="utf-8") as f:
        json.dump(проект, f)


def пр(cv, x0, y0, x1, y1, мат, z, extra=0.0):
    return poly(cv, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], мат, z, extra=extra)


def запиши(име, кадри, описание):
    pygame.image.save(лента(кадри), os.path.join(ПАПКА, име + ".png"))
    piskel(име, кадри, описание)
    print("assets/minigames/%s.png  (%d кадъра %dx%d)" % (име, len(кадри), *кадри[0].get_size()))


# ---------- фон: кухнята ----------
def фон():
    cv = Canvas(320, 180)
    for и, x in enumerate(range(0, 320, 20)):                       # стена от дъски
        мат = PLANK if и % 3 else WOOD_D
        пр(cv, x, 0, x + 20, 140, мат, 0, extra=-0.2 + 0.12 * (и % 2))
        for y in range(0, 140):
            cv.plot(x, y, мат[3], 0.1, 950)
        for y in (24, 104):
            cv.plot(x + 4, y, IRON[1], 0.2, 951); cv.plot(x + 15, y, IRON[1], 0.2, 951)
        for k in range(3):                                         # жилки
            yy = (x * 7 + k * 41) % 120 + 8
            for d in range(6):
                cv.plot(x + 8 + k * 3, yy + d, мат[2], 0.15, 952)
    пр(cv, 0, 0, 320, 9, WOOD_D, 1, extra=0.2)                       # греда горе
    пр(cv, 20, 18, 84, 70, WOOD, 1.5)                                # прозорец
    пр(cv, 24, 22, 80, 66, M('#dff4ff', '#b4e0f4', '#8cc4e0', '#6aa4c8'), 1.6, extra=0.4)
    ellipse(cv, 40, 52, 14, 8, M('#b4e48a', '#8cc464', '#6aa044', '#4a7a30'), 1.7)   # хълм зад стъклото
    ellipse(cv, 70, 56, 16, 9, M('#a4d47a', '#7cb454', '#5a9038', '#3e6a26'), 1.65)
    пр(cv, 50, 22, 54, 66, WOOD, 1.8); пр(cv, 24, 42, 80, 45, WOOD, 1.8)
    пр(cv, 16, 68, 88, 74, WOOD, 1.9, extra=0.3)                     # перваз
    capsule(cv, (30, 64), (30, 60), 3, 3, CLAY, 2)                   # саксийка с цвете
    for (x, y) in ((28, 56), (32, 55), (30, 53)):
        cv.plot(x, y, hx('#e83a5a'), 2.5, 953)
    for k in range(9):                                               # низ червени чушки
        y = 14 + k * 8
        capsule(cv, (108, y), (106 + (k % 2) * 4, y + 8), 2.6, 1.0, TOMATO, 2 + k * 0.01)
        cv.plot(108, y - 1, GREEN, 2.5, 954)
    for y in range(9, 84):
        cv.plot(108, y, hx('#c8b080'), 1.9, 955)
    for k in range(6):                                               # плитка чесън
        ellipse(cv, 292 + (k % 2) * 6, 22 + k * 8, 4, 3.6, ONION, 2 + k * 0.01)
    пр(cv, 214, 58, 312, 62, WOOD, 2)                                # рафт с буркани
    for k, (x, мат) in enumerate(((222, CLAY), (238, GLASS), (254, PEPPER), (272, CLAY), (290, GLASS), (304, TOMATO))):
        if мат is GLASS:
            capsule(cv, (x, 56), (x, 46), 5, 5, GLASS, 2.2)
            capsule(cv, (x, 54), (x, 49), 4, 4, (RAKIA, WINE)[k % 2], 2.3)
            capsule(cv, (x, 45), (x, 40), 2, 2, GLASS, 2.2)
        else:
            capsule(cv, (x, 56), (x, 47), 5.5, 5, мат, 2.2)
            ellipse(cv, x, 45, 5, 1.8, (WOOD, TOMATO)[k % 2], 2.3)
    for x, ш in ((150, 30), (186, 26)):                              # закачени тигани / черпаци
        ellipse(cv, x, 40, ш // 2, ш // 2, IRON, 1.8)
        capsule(cv, (x, 40 - ш // 2), (x, 12), 1.5, 1.5, IRON, 1.7)
    for y in range(140, 180):                                        # плотът на масата: дъски по дължината
        ред = (y - 142) % 9
        for x in range(0, 320):
            ц = WOOD[3] if ред == 8 else WOOD[0] if ред == 0 else WOOD[1] if ред < 4 else WOOD[2] if (x * 5 + y * 3) % 97 < 6 else WOOD[1]
            cv.plot(x, y, ц, 3, 956)
        if ред == 4:
            for x in range((y * 37) % 60, 320, 83):                   # шевове между дъските
                for yy in range(y - 4, y + 4):
                    cv.plot(x, yy, WOOD[3], 3.05, 956)
    for x in range(0, 320):
        cv.plot(x, 140, WOOD[0], 3.2, 957); cv.plot(x, 141, WOOD[0], 3.2, 957)
    return повърхност(finish(cv, OUT, inner=False))


# ---------- ракия ----------
ЧАША = (44, 60)
def чаша(налято, преляла=False):
    """Чаша 44x60: стени от стъкло, ракия до 'налято' реда отдолу."""
    cv = Canvas(*ЧАША)
    горе, долу = 6, 52
    def стени(y):                                                    # вътрешна ширина на реда y
        к = (y - горе) / (долу - горе)
        return 6 + 4 * к, 38 - 4 * к
    for y in range(горе, долу + 1):                                  # стъклото (почти прозрачно)
        л, д = стени(y)
        for x in range(int(л) - 2, int(д) + 3):
            if x < л or x > д:
                cv.plot(x, y, GLASS[1], 1, 960)

    for y in range(max(горе, долу - налято + 1), долу + 1):          # ракията
        л, д = стени(y)
        for x in range(int(л), int(д) + 1):
            ц = RAKIA[1] if x < (л + д) / 2 + 4 else RAKIA[2]
            if y == долу - налято + 1:
                ц = RAKIA[0]
            cv.plot(x, y, ц, 1.2, 962)
    пр(cv, 8, 52, 36, 58, GLASS, 1.5, extra=0.3)                      # дебелото дъно
    for y in range(горе + 4, долу - 6):                              # отблясък
        cv.plot(int(стени(y)[0]) + 2, y, WHITE, 2, 963)
    for x in range(4, 41):
        cv.plot(x, горе - 1, GLASS[0], 2, 964)
    if преляла:
        for (x, y) in ((3, 10), (2, 18), (41, 14), (42, 24), (1, 30), (42, 36)):
            capsule(cv, (x, y), (x, y + 5), 1.2, 1.6, RAKIA, 3)
        ellipse(cv, 22, 59, 20, 1.5, RAKIA, 0.2)
    return повърхност(finish(cv, OUT, inner=False))


def шише(ъгъл):
    """Шише 80x80, завъртяно около средата си. Връща (картинка, (x, y) на гърлото)."""
    cv = Canvas(80, 80)
    a = math.radians(ъгъл)
    u = (math.sin(a), -math.cos(a))
    B = (40 - u[0] * 23.5, 40 - u[1] * 23.5)
    т = lambda d: (B[0] + u[0] * d, B[1] + u[1] * d)
    capsule(cv, т(4), т(26), 8, 8, GLASS, 1)                         # тялото
    capsule(cv, т(26), т(32), 8, 3.4, GLASS, 1.1)                   # рамото
    capsule(cv, т(32), т(44), 3.2, 3.2, GLASS, 1.2)                 # гърлото
    capsule(cv, т(44), т(47), 3.8, 3.8, WOOD, 1.4)                  # тапата / капачката
    налято = 22 - min(14, ъгъл / 8)
    capsule(cv, т(5), т(5 + налято), 6.2, 6.2, RAKIA, 1.3)          # ракията вътре
    пр(cv, 0, 0, 0, 0, GLASS, 0)
    лс = т(14)                                                       # етикет
    capsule(cv, т(12), т(20), 7.2, 7.2, M('#fff8e6', '#f2e6c4', '#dccaa0', '#b8a274'), 1.5)
    cv.plot(int(лс[0]), int(лс[1]), hx('#c83a2e'), 2, 965); cv.plot(int(лс[0]) + 1, int(лс[1]), hx('#c83a2e'), 2, 965)
    гърло = т(46)
    return повърхност(finish(cv, OUT, inner=False)), (round(гърло[0], 1), round(гърло[1], 1))


# ---------- вино ----------
def бъчва(отворена):
    cv = Canvas(128, 112)
    for x in (22, 98):                                               # поставка
        poly(cv, [(x - 10, 104), (x + 10, 104), (x + 4, 76), (x - 4, 76)], WOOD_D, 0.5)
    пр(cv, 8, 100, 120, 108, WOOD_D, 0.6)
    capsule(cv, (30, 58), (98, 58), 38, 38, WOOD, 1)                  # тялото (легнала бъчва)
    for x in range(14, 116, 9):                                      # дъските
        for y in range(22, 96):
            cv.plot(x, y, WOOD[3], 1.1, 966)
    for x in (36, 92):                                               # обръчи
        пр(cv, x - 3, 18, x + 3, 98, IRON, 1.3)
        for y in range(20, 97, 12):
            cv.plot(x, y, IRON[0], 1.4, 967)
    ellipse(cv, 64, 58, 24, 30, WOOD_D, 1.6)                          # предното дъно
    for x in range(46, 84, 6):
        for y in range(30, 88):
            if ((x - 64) / 24) ** 2 + ((y - 58) / 30) ** 2 < 1:
                cv.plot(x, y, WOOD_D[3], 1.7, 968)
    ellipse(cv, 64, 58, 24, 30, IRON, 1.55)                           # железен кант
    capsule(cv, (64, 80), (64, 90), 3.4, 3.0, GOLD, 2)                # канелката
    if отворена:
        capsule(cv, (64, 82), (74, 80), 1.6, 1.6, GOLD, 2.3)          # дръжката е завъртяна
    else:
        capsule(cv, (64, 82), (64, 74), 1.6, 1.6, GOLD, 2.3)
    ellipse(cv, 64, 92, 2.6, 1.6, (WINE if отворена else GOLD), 2.4)
    пр(cv, 50, 40, 78, 50, M('#fff4dc', '#ecdcb4', '#d2bc8c', '#a88e5c'), 1.8)   # табелка
    for x in range(54, 75, 3):
        cv.plot(x, 45, WINE[2], 1.9, 969)
    return повърхност(finish(cv, OUT, inner=False))


КАНЧЕ_ВИС = 22
def кана(редове):
    cv = Canvas(44, 46)
    ellipse(cv, 22, 30, 16, 15, CLAY, 1)                             # тялото
    capsule(cv, (22, 14), (22, 8), 8, 9, CLAY, 1.1)                  # шията
    ellipse(cv, 22, 7, 10, 3.2, CLAY, 1.2, extra=0.4)
    ellipse(cv, 22, 7.4, 8, 2.2, CLAY[3:] * 4, 1.25)                 # отворът (тъмно)
    capsule(cv, (36, 16), (38, 32), 1.8, 1.8, CLAY, 0.8)            # дръжката
    for x in range(8, 37, 3):                                        # бяла шарка
        cv.plot(x, 26, hx('#fff2d2'), 1.5, 970); cv.plot(x + 1, 27, hx('#fff2d2'), 1.5, 970)
    if редове:                                                        # виното се вижда в отвора и отстрани
        ellipse(cv, 22, 7.4, 8, 2.2, WINE, 1.3)
        ниво = 42 - int(30 * редове / КАНЧЕ_ВИС)
        for y in range(ниво, 42):
            for x in range(40, 43):
                cv.plot(x, y, WINE[1], 1.6, 971)                    # мерителна чертичка отстрани
    return повърхност(finish(cv, OUT, inner=False))


# ---------- шопска ----------
def дъска():
    cv = Canvas(150, 44)
    пр(cv, 4, 6, 146, 34, WOOD, 1)
    for y in (13, 20, 27):
        for x in range(6, 144):
            if (x * 3 + y) % 11:
                cv.plot(x, y, WOOD[2], 1.1, 972)
    пр(cv, 4, 34, 146, 40, WOOD_D, 1.2)
    ellipse(cv, 136, 14, 4, 3, WOOD_D[3:] * 4, 1.3)                  # дупката за закачане
    for (x, y) in ((30, 26), (60, 12), (100, 28), (120, 18)):        # следи от ножа
        for d in range(5):
            cv.plot(x + d, y - d // 2, WOOD[3], 1.2, 973)
    return повърхност(finish(cv, OUT))


def зеленчук(вид, етап):
    """вид 0 домат, 1 краставица, 2 чушка, 3 лук, 4 морков; етап 0 цял, 1 разрязан, 2 на резени."""
    if вид == 4:
        return морков(етап)
    cv = Canvas(32, 32)
    мат = (TOMATO, CUC, PEPPER, ONION)[вид]
    вътре = (M('#ffb8a0', '#f45a48', '#c43a30', '#8a2020'), M('#f0ffd8', '#d4f0a8', '#a8d47c', '#78a854'),
             M('#fff4c0', '#ffe080', '#f0b830', '#b88010'), M('#ffffff', '#f8f4ec', '#e8dcc8', '#c4b49a'))[вид]
    if етап == 0:
        if вид == 0:
            ellipse(cv, 16, 18, 11, 10, мат, 1)
            for (dx, dy) in ((-2, -9), (0, -10), (2, -9), (0, -11)):
                cv.plot(16 + dx, 18 + dy, GREEN, 2, 974)
        elif вид == 1:
            capsule(cv, (5, 22), (27, 12), 6, 6, мат, 1)
            for k in range(6):
                cv.plot(8 + k * 3, 19 - k * 1, hx('#f0ffd8'), 2, 975)
        elif вид == 2:
            capsule(cv, (16, 9), (16, 26), 8, 4, мат, 1)
            capsule(cv, (16, 9), (18, 3), 1.4, 1.4, CUC, 1.5)
        else:
            ellipse(cv, 16, 19, 10, 9, мат, 1)
            capsule(cv, (16, 10), (16, 5), 1.6, 0.8, мат, 1.2)
            for x in (12, 16, 20):
                for y in range(13, 26):
                    cv.plot(x + (y - 19) // 6, y, мат[2], 1.3, 976)
    elif етап == 1:
        for k, dx in enumerate((-6, 6)):
            ellipse(cv, 16 + dx, 18, 7, 9, мат, 1 + k * 0.1)
            ellipse(cv, 16 + dx + (2 if dx < 0 else -2), 18, 5, 7.5, вътре, 1.2 + k * 0.1)
            if вид in (0, 2):
                for (x, y) in ((0, -3), (0, 0), (0, 3)):
                    cv.plot(16 + dx + (2 if dx < 0 else -2) + x, 18 + y, hx('#fff4c0'), 1.5, 977)
    else:
        for k in range(4):
            x = 6 + k * 7; y = 14 + (k % 2) * 6
            ellipse(cv, x, y, 4.2, 4.2, мат, 1 + k * 0.05)
            ellipse(cv, x, y, 3.0, 3.0, вътре, 1.2 + k * 0.05)
            cv.plot(x, y, hx('#fff4c0') if вид != 3 else вътре[2], 1.4, 978)
    return повърхност(finish(cv, OUT, inner=False))


def морков(етап):
    cv = Canvas(32, 32)
    сърце = M('#ffe0a0', '#ffb860', '#f09030', '#c06a18')
    if етап == 0:
        capsule(cv, (9, 10), (26, 26), 5.5, 1.4, CARROT, 1)
        for k in range(4):                                            # бразди
            x, y = 12 + k * 3.6, 14 + k * 3.4
            cv.plot(int(x) + 2, int(y) - 2, CARROT[3], 1.5, 991); cv.plot(int(x) + 3, int(y) - 1, CARROT[3], 1.5, 991)
        for (a, b) in (((7, 7), (3, 2)), ((8, 6), (8, 1)), ((9, 7), (13, 2))):   # листата
            capsule(cv, a, b, 1.2, 0.8, CUC, 1.6)
    elif етап == 1:
        capsule(cv, (8, 12), (16, 19), 5, 3.8, CARROT, 1)
        ellipse(cv, 16, 19, 3.2, 3.6, сърце, 1.2)
        capsule(cv, (19, 21), (27, 28), 3.6, 1.3, CARROT, 1.05)
        ellipse(cv, 19, 21, 3, 3.2, сърце, 1.25)
        capsule(cv, (8, 12), (5, 6), 1.2, 0.8, CUC, 1.3)
    else:
        for k in range(4):
            x = 6 + k * 7; y = 14 + (k % 2) * 6
            ellipse(cv, x, y, 4.2, 4.0, CARROT, 1 + k * 0.05)
            ellipse(cv, x, y, 2.6, 2.4, сърце, 1.2 + k * 0.05)
            cv.plot(x, y, сърце[2], 1.4, 978)
    return повърхност(finish(cv, OUT, inner=False))


ТЕНДЖЕРА = {"x": 60, "y": 27, "rx": 42, "ry": 9}                        # отворът (там рисуваме какво има вътре)
ТИГАН = {"x": 58, "y": 24, "rx": 46, "ry": 11}


def тенджера():
    """Емайлирана тенджера като у баба: бяла, с червен ръб и цветя. 120x92 (като гърнето)."""
    cv = Canvas(120, 92)
    ellipse(cv, 60, 78, 46, 9, ENAMEL, 1)                             # дъното
    пр(cv, 14, 27, 106, 78, ENAMEL, 1.05)                              # тялото
    for x in range(14, 107):                                          # светлина отляво, сянка отдясно
        к = (x - 14) / 92
        for y in range(28, 80):
            if к > 0.72:
                cv.plot(x, y, ENAMEL[2] if к < 0.88 else ENAMEL[3], 1.06, 992)
            elif к < 0.12:
                cv.plot(x, y, ENAMEL[0], 1.06, 992)
    for x in range(15, 106):                                          # червени ивици
        cv.plot(x, 34, RED[1], 1.1, 993); cv.plot(x, 72, RED[2], 1.1, 993)
    for k, x in enumerate(range(26, 100, 18)):                        # цветя
        y = 52 + (k % 2) * 4
        for (dx, dy) in ((0, -2), (-2, 0), (2, 0), (0, 2)):
            cv.plot(x + dx, y + dy, RED[1], 1.2, 994)
        cv.plot(x, y, hx('#f2cc2e'), 1.21, 994)
        cv.plot(x - 3, y + 3, CUC[2], 1.2, 994); cv.plot(x + 3, y + 3, CUC[2], 1.2, 994)
    for x in (8, 112):                                                # дръжките
        capsule(cv, (x, 36), (x + (6 if x < 60 else -6), 36), 2.6, 2.6, IRON, 0.9)
    ellipse(cv, 60, 27, 48, 12, RED, 1.3)                             # ръбът
    ellipse(cv, 60, 27, 45, 10, ENAMEL_IN, 1.35)                      # вътре (тук играта рисува съдържанието)
    return повърхност(finish(cv, OUT, inner=False))


def тиган():
    """Чугунен тиган с дървена дръжка, 150x50."""
    cv = Canvas(150, 50)
    ellipse(cv, 58, 26, 54, 16, IRON, 1)
    ellipse(cv, 58, 24, 50, 13, M('#5a5862', '#46444e', '#32303a', '#22202a'), 1.2)
    capsule(cv, (108, 24), (118, 21), 2.2, 2.2, IRON, 0.9)
    capsule(cv, (118, 21), (146, 15), 3.4, 3.8, WOOD_D, 1.1)
    cv.plot(141, 16, OUT, 1.5, 995); cv.plot(142, 16, OUT, 1.5, 995)
    return повърхност(finish(cv, OUT, inner=False))


def нож(кадър):
    cv = Canvas(64, 56)
    y = (6, 14, 30, 36)[кадър]
    наклон = (-10, -6, 0, 2)[кадър]
    poly(cv, [(6, y + 6), (40, y + 2 + наклон * 0.2), (40, y + 12), (8, y + 12)], IRON, 1, extra=0.5)   # острието
    for x in range(8, 40):
        cv.plot(x, int(y + 7), WHITE, 1.5, 979)
    пр(cv, 40, y + 2, 60, y + 11, WOOD_D, 1.2)                        # дръжката
    for x in (45, 54):
        cv.plot(x, y + 6, GOLD[1], 1.5, 980)
    if кадър == 3:                                                    # удар: малки чертички
        for (dx, dy) in ((2, 16), (0, 12), (4, 20)):
            cv.plot(dx, y + dy, WHITE, 2, 981); cv.plot(dx + 1, y + dy, WHITE, 2, 981)
    return повърхност(finish(cv, OUT, inner=False))


def купа(парчета):
    cv = Canvas(84, 50)
    ellipse(cv, 42, 30, 38, 18, BOWL, 1)                              # купата
    ellipse(cv, 42, 22, 36, 9, BOWL, 1.2, extra=0.4)                 # ръбът
    ellipse(cv, 42, 23, 31, 6.5, M('#e8e2d6', '#d6cebe', '#bcb2a0', '#968c7a'), 1.25)   # вътрешността
    for x in range(8, 77, 5):                                         # синя шарка (троянска керамика)
        cv.plot(x, 36, hx('#3a6ac8'), 1.4, 982); cv.plot(x + 1, 37, hx('#3a6ac8'), 1.4, 982)
    import random
    сл = random.Random(5)
    for к in range(min(парчета, 8)):                                  # нарязаните зеленчуци
        мат = (TOMATO, CUC, PEPPER, ONION)[к % 4]
        for _ in range(5):
            x, y = сл.uniform(14, 70), сл.uniform(17, 26)
            ellipse(cv, x, y, 3.2, 2.4, мат, 1.5 + к * 0.01 + сл.random() * 0.005)
    if парчета > 8:                                                   # настърганото сирене и магданоз
        ellipse(cv, 42, 17, 22, 7, SIRENE, 2)
        for _ in range(26):
            cv.plot(int(сл.uniform(24, 60)), int(сл.uniform(12, 21)), WHITE, 2.2, 983)
        for (x, y) in ((40, 11), (42, 10), (44, 11), (41, 12)):
            cv.plot(x, y, GREEN, 2.3, 984)
    return повърхност(finish(cv, OUT, inner=False))


# ---------- хляб: самун и филийки ----------
КОРА = M('#ffc878', '#e8963c', '#c06a24', '#8a4618')       # кората (печена)
СРЕДА = M('#fff4d4', '#ffe0a0', '#f6c070', '#d49650')      # средата на хляба
ХЛЯБ_ОС = (math.cos(math.radians(-15)), math.sin(math.radians(-15)))   # самунът е наклонен нагоре надясно
ХЛЯБ_А0 = (36.0, 62.0)                                     # левият (отрязан) край
ХЛЯБ_ДЪЛЖ = 96.0
ФИЛИЙКА = 9.0                                              # дебелина на филийката
ХЛЯБ_ФИЛИЙКИ = 6


def _наклонена_елипса(cv, c, ос, a, b, мат, z, extra=0.0):
    """Елипса, завъртяна по оста на самуна (a по оста, b напречно)."""
    ux, uy = ос
    for y in range(int(c[1] - b - 2), int(c[1] + b + 3)):
        for x in range(int(c[0] - b - 2), int(c[0] + b + 3)):
            dx, dy = x + 0.5 - c[0], y + 0.5 - c[1]
            p, q = (dx * ux + dy * uy) / a, (-dx * uy + dy * ux) / b
            if p * p + q * q <= 1:
                cv.plot(x, y, tone(мат, bright(-0.3, q * 0.9, extra)), z, 940)


def самун(отрязани):
    """Самун 160x110 като на снимката: дебел, с нарези отгоре и отрязан край, в който се вижда средата."""
    cv = Canvas(160, 110)
    ux, uy = ХЛЯБ_ОС
    нр = (uy, -ux)                                               # напречно, нагоре вляво
    A = (ХЛЯБ_А0[0] + ux * ФИЛИЙКА * отрязани, ХЛЯБ_А0[1] + uy * ФИЛИЙКА * отрязани)
    B = (ХЛЯБ_А0[0] + ux * ХЛЯБ_ДЪЛЖ, ХЛЯБ_А0[1] + uy * ХЛЯБ_ДЪЛЖ)
    capsule(cv, A, B, 27, 25, КОРА, 1)                           # тялото
    for y in range(cv.h):                                        # отрязано: нищо вляво от среза
        for x in range(cv.w):
            if (x + 0.5 - A[0]) * ux + (y + 0.5 - A[1]) * uy < 0:
                cv.col[y][x] = None
                cv.z[y][x] = -1e9
    посока = (0.72, 0.69)                                        # нарезите: наклонени "\\" през горната страна
    for k in range(4):                                           # нарезите отгоре: дебели тъмни ивици
        t = 30 + k * 18
        if t < ФИЛИЙКА * отрязани + 12:
            continue
        ц = (ХЛЯБ_А0[0] + ux * t + нр[0] * 5, ХЛЯБ_А0[1] + uy * t + нр[1] * 5)
        п = (-посока[1], посока[0])                              # напречно на нареза
        ъгли = [(ц[0] + посока[0] * a + п[0] * b, ц[1] + посока[1] * a + п[1] * b)
                for a, b in ((-11, -2.4), (11, -2.4), (11, 2.4), (-11, 2.4))]
        poly(cv, [(x + п[0] * 1.6, y + п[1] * 1.6) for x, y in ъгли], КОРА, 1.9, extra=0.8)   # светъл ръб
        poly(cv, ъгли, M('#b8642a', '#94481a', '#763410', '#56240a'), 2)                 # нарезът
    _наклонена_елипса(cv, A, ХЛЯБ_ОС, 13, 26.5, КОРА, 2.5, extra=0.1)         # отрязаният край: кора
    _наклонена_елипса(cv, (A[0] - ux * 2, A[1] - uy * 2), ХЛЯБ_ОС, 10.5, 23, СРЕДА, 2.6, extra=0.35)  # средата
    return повърхност(finish(cv, OUT, inner=False))


def филийка(наклон):
    """Филийка 36x36, лежи в чинията (наклон 0/1 - леко различни за купчината)."""
    cv = Canvas(36, 36)
    ellipse(cv, 18, 21, 15, 10, КОРА, 1)                         # кората отстрани
    ellipse(cv, 18, 17, 15, 10, КОРА, 1.2, extra=0.4)
    ellipse(cv, 18 + наклон, 17, 12.5, 7.8, СРЕДА, 1.4, extra=0.6)
    for (x, y) in ((13, 15), (21, 18), (17, 20), (24, 15)):     # дупчици в средата
        cv.plot(x, y, СРЕДА[2], 1.5, 943)
    return повърхност(finish(cv, OUT, inner=False))


def чиния():
    cv = Canvas(90, 40)
    ellipse(cv, 45, 24, 42, 14, BOWL, 1)
    ellipse(cv, 45, 21, 36, 10, M('#f4f0e8', '#e2dcd0', '#c8c0b0', '#a09888'), 1.2)
    for x in range(8, 84, 6):
        cv.plot(x, 30, hx('#3a6ac8'), 1.3, 944)
    return повърхност(finish(cv, OUT, inner=False))


# ---------- боб ----------
def огнище():
    cv = Canvas(168, 52)
    пр(cv, 2, 14, 166, 50, STONE, 1)
    for y in (24, 36):
        for x in range(2, 166):
            cv.plot(x, y, STONE[3], 1.1, 985)
    for ред, y0 in enumerate((14, 24, 36)):
        for x in range(6 + ред * 9, 166, 22):
            for y in range(y0, y0 + (10 if ред < 2 else 14)):
                cv.plot(x, y, STONE[3], 1.1, 985)
    ellipse(cv, 84, 18, 56, 10, M('#4a3a32', '#2e2420', '#1e1816', '#100c0a'), 1.4)   # огнището (тъмно)
    for k in range(5):                                                # дърва
        capsule(cv, (48 + k * 18, 22), (60 + k * 18, 16), 3.4, 3.4, WOOD_D, 1.6 + k * 0.01)
        ellipse(cv, 60 + k * 18, 16, 2.6, 2.6, M('#f0c890', '#d8a868', '#b88848', '#8a6030'), 1.7 + k * 0.01)
    return повърхност(finish(cv, OUT, inner=False))


def огън(размер, кадър):
    cv = Canvas(72, 48)
    в = (14, 24, 38)[размер]
    ш = (16, 22, 28)[размер]
    for k in range(5):
        фаза = кадър * (2 * math.pi / 6) + k * 1.3
        x = 36 + (k - 2) * ш * 0.42 + math.sin(фаза) * 2
        височина = в * (0.6 + 0.4 * abs(math.sin(фаза * 0.7 + k)))
        for слой, цв in enumerate(FIRE[::-1]):
            r = (ш * 0.32) * (1 - слой * 0.22)
            capsule(cv, (x, 46 - слой), (x + math.sin(фаза) * 3, 46 - височина * (1 - слой * 0.18)), r, 0.6, (цв,) * 4, 1 + слой * 0.1 + k * 0.001)
    for k in range(размер + 2):                                       # искри
        x = 36 + math.sin(кадър * 2.1 + k * 2.4) * ш
        y = 46 - в - 4 - ((кадър * 4 + k * 7) % 12)
        cv.plot(int(x), int(y), FIRE[1], 3, 986)
    return повърхност(finish(cv, OUT, inner=False))


def гърне(кадър):
    cv = Canvas(120, 92)
    ellipse(cv, 60, 56, 52, 34, CLAY, 1)                              # тялото
    ellipse(cv, 60, 26, 50, 13, CLAY, 1.3, extra=0.5)                 # ръбът
    ellipse(cv, 60, 27, 44, 10, SOUP, 1.4)                            # чорбата
    for x in range(14, 108, 6):                                       # бяла шарка
        cv.plot(x, 62, hx('#fff2d2'), 1.5, 987); cv.plot(x + 2, 64, hx('#fff2d2'), 1.5, 987)
    for x in (10, 110):                                               # дръжки
        ellipse(cv, x, 44, 5, 7, CLAY, 0.9)
    import random
    сл = random.Random(11)
    боб = [(сл.uniform(24, 96), сл.uniform(20, 33)) for _ in range(22)]
    for (x, y) in боб:                                                # бобчета
        if ((x - 60) / 42) ** 2 + ((y - 27) / 9) ** 2 < 1:
            cv.plot(int(x), int(y), hx('#fbe8c4'), 1.6, 988); cv.plot(int(x) + 1, int(y), hx('#d8b888'), 1.6, 988)
    for (x, y) in ((40, 25), (70, 30), (82, 23), (52, 31)):           # джоджен
        cv.plot(x, y, GREEN, 1.7, 989); cv.plot(x + 1, y - 1, GREEN, 1.7, 989)
    for k in range(4):                                                # мехурчета (4 кадъра)
        фаза = (кадър + k) % 4
        bx, by = ((36, 26), (58, 30), (80, 24), (66, 22))[k]
        r = (0, 1.4, 2.4, 1.0)[фаза]
        if r:
            ellipse(cv, bx, by, r + 0.6, r, M('#ffd8a0', '#f0b464', '#cc8236', '#9a5a1e'), 1.8 + k * 0.01)
            cv.plot(int(bx - r / 2), int(by - r / 2), WHITE, 1.9, 990)
    return повърхност(finish(cv, OUT, inner=False))


def лъжица(кадър):
    """Лъжицата обикаля в гърнето (същият размер като гърнето: 120x92)."""
    cv = Canvas(120, 92)
    ъ = кадър / 8 * 2 * math.pi
    x, y = 60 + 32 * math.cos(ъ), 27 + 7 * math.sin(ъ)
    отзад = math.sin(ъ) < 0
    capsule(cv, (x, y - 2), (x + 16, y - 54), 2.2, 2.6, WOOD, 3 if not отзад else 1.2)
    ellipse(cv, x, y, 6, 3, WOOD, 3.1 if not отзад else 1.25, extra=-0.3)
    return повърхност(finish(cv, OUT, inner=False))


def пара(кадър):
    cv = Canvas(72, 52)
    for k in range(3):
        for d in range(6):
            y = 48 - d * 8 - (кадър * 2)
            x = 16 + k * 20 + math.sin(d * 0.9 + кадър * 0.8 + k) * 4
            if 0 < y < 52:
                ellipse(cv, x, y, 3.2 - d * 0.35, 2.6 - d * 0.3, (STEAM,) * 4, 1 + d * 0.01)
    пиксели = finish(cv, (200, 210, 220, 255), inner=False)
    s = повърхност(пиксели)
    s.set_alpha(None)
    return s


def главна():
    pygame.init()
    pygame.display.set_mode((1, 1))
    os.makedirs(ПАПКА, exist_ok=True)
    запиши("kuhnya_fon", [фон()], "Кухнята: фон за мини игрите (320x180, в играта x3)")
    # ракия
    запиши("rakia_chasha", [чаша(к) for к in range(47)] + [чаша(46, True)], "Чашата: кадър k = налято k реда, последният = преляла")
    кадри, гърла = zip(*[шише(а) for а in (0, 28, 56, 84, 104, 118)])
    запиши("rakia_shishe", list(кадри), "Шишето с ракия: от изправено до наклонено")
    with open(os.path.join(ПАПКА, "rakia_shishe.json"), "w", encoding="utf-8") as f:
        json.dump({"гърло": гърла}, f)
    # вино
    запиши("vino_bachva", [бъчва(False), бъчва(True)], "Бъчвата: канелката затворена / отворена")
    запиши("vino_kancha", [кана(к) for к in range(КАНЧЕ_ВИС + 1)], "Каничката: кадър k = k реда вино")
    # шопска
    запиши("shopska_daska", [дъска()], "Дъската за рязане")
    запиши("shopska_zelenchuci", [зеленчук(в, е) for в in range(5) for е in range(3)],
           "Домат, краставица, чушка, лук, морков: цял, разрязан, на резени")
    запиши("shopska_noj", [нож(к) for к in range(4)], "Ножът: от горе до удар")
    запиши("shopska_kupa", [купа(к) for к in range(10)], "Купата: 0-8 нарязани, последният кадър със сирене")
    # хляб
    запиши("hlyab_samun", [самун(к) for к in range(ХЛЯБ_ФИЛИЙКИ + 1)], "Самунът: 0-6 отрязани филийки")
    запиши("hlyab_filiyka", [филийка(0), филийка(1)], "Филийка хляб")
    запиши("hlyab_chiniya", [чиния()], "Чиния за филийките")
    with open(os.path.join(ПАПКА, "hlyab.json"), "w", encoding="utf-8") as f:
        json.dump({"ос": ХЛЯБ_ОС, "начало": ХЛЯБ_А0, "филийка": ФИЛИЙКА}, f)
    # боб
    запиши("bob_ognishte", [огнище()], "Каменното огнище")
    запиши("bob_ogan", [огън(р, к) for р in range(3) for к in range(6)], "Огънят: малък, среден, голям x 6 кадъра")
    запиши("bob_garne", [гърне(к) for к in range(4)], "Гърнето с боб: мехурчета, 4 кадъра")
    запиши("bob_lazhica", [лъжица(к) for к in range(8)], "Лъжицата обикаля гърнето, 8 кадъра")
    запиши("bob_para", [пара(к) for к in range(4)], "Пара, 4 кадъра")
    # рецептите
    запиши("tendzhera", [тенджера()], "Емайлирана тенджера (вътре играта рисува какво сме сложили)")
    запиши("tigan", [тиган()], "Чугунен тиган с дървена дръжка")
    with open(os.path.join(ПАПКА, "sadove.json"), "w", encoding="utf-8") as f:
        json.dump({"tendzhera": ТЕНДЖЕРА, "tigan": ТИГАН}, f, ensure_ascii=False)


if __name__ == "__main__":
    главна()
