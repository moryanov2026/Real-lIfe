# Рисува кавала за минииграта "Свирене" (Claude). Пускане от папката "Real Life":
#     python tools/pixelart/make_kaval.py
# Резултат: assets/music/kaval.png (192x432, инструментът отстрани на екрана, платно 960x540)
#           art_src/kaval.piskel и art_src/kaval_preview.png
# Кавалът: три коляна (горно с духалото, средно със 7-те дупки, долно с 4-те "дяволски" дупки),
# костени пръстени на съединенията, резбовани ивици. Светлина горе вляво.
import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

ИГРА = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H = 192, 432


def hx(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


КОНТУР = hx("#1e1410")
ДЪРВО = [hx("#d49a62"), hx("#b07440"), hx("#8a5530"), hx("#62391e"), hx("#46260f")]   # дрян
КОСТ = [hx("#fbf4e2"), hx("#e8dbb9"), hx("#c6b48f"), hx("#968361")]
ДУПКА = [hx("#140c08"), hx("#2c1a10")]

ЦЕНТЪР = 96
ГОРЕ, ДОЛУ = 8, 424


def полуширина(y):
    """Кавалът леко се разширява надолу."""
    return 11 + (y - ГОРЕ) / (ДОЛУ - ГОРЕ) * 2.0


def тон(мат, x, y):
    """Цилиндър: светло вляво, тъмно вдясно."""
    п = полуширина(y)
    t = (x + 0.5 - ЦЕНТЪР) / п           # -1 ляво ... +1 дясно
    if мат is КОСТ:
        return КОСТ[0] if t < -0.45 else КОСТ[1] if t < 0.1 else КОСТ[2] if t < 0.6 else КОСТ[3]
    return (ДЪРВО[0] if t < -0.55 else ДЪРВО[1] if t < -0.05 else ДЪРВО[2] if t < 0.5
            else ДЪРВО[3] if t < 0.85 else ДЪРВО[4])


def рисувай():
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    # пръстени (кост): [от, до]
    пръстени = [(ГОРЕ, ГОРЕ + 7), (118, 130), (292, 304), (ДОЛУ - 8, ДОЛУ)]

    def в_пръстен(y):
        return any(а <= y < б for а, б in пръстени)

    for y in range(ГОРЕ, ДОЛУ):
        п = полуширина(y) + (1 if в_пръстен(y) else 0)        # пръстените са малко по-дебели
        for x in range(int(ЦЕНТЪР - п), int(ЦЕНТЪР + п)):
            s.set_at((x, y), тон(КОСТ if в_пръстен(y) else ДЪРВО, x, y))
    # ръбове на пръстените: тъмна линия отгоре/отдолу + светла черта
    for а, б in пръстени:
        п = int(полуширина(а)) + 1
        for x in range(ЦЕНТЪР - п, ЦЕНТЪР + п):
            s.set_at((x, а), КОСТ[3])
            s.set_at((x, б - 1), КОСТ[3])
        средата = (а + б) // 2
        if б - а > 8:
            for x in range(ЦЕНТЪР - п + 2, ЦЕНТЪР + п - 2):
                if (x + средата) % 3 == 0:
                    s.set_at((x, средата), КОСТ[2])           # гравирани чертички
    # резбовани ивици: наклонени жлебове (спирала)
    for (а, б) in ((24, 58), (136, 150), (268, 288), (312, 336), (394, 414)):
        for y in range(а, б):
            п = int(полуширина(y))
            for x in range(ЦЕНТЪР - п + 1, ЦЕНТЪР + п - 1):
                if (x + y) % 6 == 0:
                    s.set_at((x, y), ДЪРВО[4] if x > ЦЕНТЪР + 2 else ДЪРВО[3])
                elif (x + y) % 6 == 1 and x < ЦЕНТЪР + 4:
                    s.set_at((x, y), ДЪРВО[0])
        for x in range(ЦЕНТЪР - int(полуширина(а)) + 1, ЦЕНТЪР + int(полуширина(а)) - 1):
            s.set_at((x, а - 1), ДЪРВО[4])
            s.set_at((x, б), ДЪРВО[4])
    # инкрустирани точки (седеф) в ромбове на горното коляно
    for cy in (72, 92):
        for (dx, dy) in ((0, -2), (-2, 0), (2, 0), (0, 2), (0, 0)):
            s.set_at((ЦЕНТЪР - 1 + dx, cy + dy), КОСТ[0] if (dx, dy) != (0, 0) else hx("#7fb6c4"))
    # 7 дупки отпред на средното коляно
    for k in range(7):
        cy = 166 + k * 15
        for dy in range(-3, 4):
            for dx in range(-3, 3):
                if (dx + 0.5) ** 2 / 9 + dy ** 2 / 12 <= 1:
                    s.set_at((ЦЕНТЪР - 1 + dx, cy + dy), ДУПКА[0] if dx < 1 else ДУПКА[1])
        s.set_at((ЦЕНТЪР - 1, cy + 4), ДЪРВО[0])                 # светъл ръб под дупката
        s.set_at((ЦЕНТЪР - 2, cy + 4), ДЪРВО[0])
        s.set_at((ЦЕНТЪР + 2, cy - 3), ДЪРВО[3])                 # сянка в горния десен ъгъл
    # 4 "дяволски" дупки на долното коляно (по две отстрани)
    for cy in (356, 376):
        for cx in (ЦЕНТЪР - 7, ЦЕНТЪР + 6):
            for (dx, dy) in ((0, 0), (1, 0), (0, 1), (1, 1), (0, -1), (1, -1)):
                s.set_at((cx + dx, cy + dy), ДУПКА[0])
    # духало: косо срязан ръб горе
    for x in range(ЦЕНТЪР - 12, ЦЕНТЪР + 13):
        for y in range(ГОРЕ, ГОРЕ + 3):
            if y - ГОРЕ < (x - (ЦЕНТЪР - 12)) / 10:
                s.set_at((x, y), (0, 0, 0, 0))
    for x in range(ЦЕНТЪР - 7, ЦЕНТЪР + 7):                         # отворът отгоре
        s.set_at((x, ГОРЕ + 3), ДУПКА[1])
    # тъмен контур отвън
    маска = [[s.get_at((x, y)).a > 0 for x in range(W)] for y in range(H)]
    for y in range(H):
        for x in range(W):
            if not маска[y][x]:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    X, Y = x + dx, y + dy
                    if 0 <= X < W and 0 <= Y < H and маска[Y][X]:
                        s.set_at((x, y), КОНТУР)
                        break
    return s


def довърши(s):
    """Довършване, направено пиксел по пиксел в Piskel (26.11.2026) и пренесено тук:
    отблясък по лакираното дърво, светли ръбчета на дупките, червено-бял пискюл на средния пръстен."""
    ДЪРВЕНИ = {ДЪРВО[0][:3], ДЪРВО[1][:3]}
    боядисани = []

    def сложи(x, y, ц):
        s.set_at((x, y), hx(ц))
        боядисани.append((x, y))

    for y in range(14, 420):                       # 1) прекъснат отблясък отляво
        if y % 23 > 17:
            continue
        if tuple(s.get_at((ЦЕНТЪР - 7, y)))[:3] in ДЪРВЕНИ and s.get_at((ЦЕНТЪР - 7, y)).a:
            сложи(ЦЕНТЪР - 7, y, "#ecc08e")
    for k in range(7):                             # 2) светъл ръб на дупките
        cy = 166 + k * 15
        сложи(ЦЕНТЪР - 5, cy - 1, "#ecc08e")
        сложи(ЦЕНТЪР - 5, cy, "#ecc08e")
        сложи(ЦЕНТЪР - 4, cy + 2, "#d49a62")
    начало = len(боядисани)
    шнур = [(108, 125), (109, 126), (110, 127), (110, 128), (111, 129), (111, 130), (112, 131), (112, 132),
            (113, 133), (113, 134), (113, 135), (114, 136), (114, 137), (114, 138), (114, 139)]
    for i, (x, y) in enumerate(шнур):              # 3) усукан червено-бял шнур
        сложи(x, y, "#f2ece0" if i % 2 else "#c62a2a")
    for x, y in ((112, 140), (113, 140), (114, 140), (115, 140), (116, 140),
                 (112, 141), (113, 141), (115, 141), (116, 141), (114, 141)):
        сложи(x, y, "#9a1c1c")                      # възел
    for y in range(142, 154):                      # пискюлът
        for x in range(111, 118):
            if y > 149 and x in (111, 117):
                continue
            ц = "#7a1414" if x == 111 else ("#d8322e" if x % 2 else "#f6efe2")
            сложи(x, y, "#7a1414" if (y == 153 and x % 2 == 0) else ц)
    пискюл = set(p for p in боядисани[начало:] if p[0] >= 108)
    for (x, y) in list(пискюл):                    # контур
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            X, Y = x + dx, y + dy
            if (X, Y) not in пискюл and s.get_at((X, Y)).a == 0:
                сложи(X, Y, "#1e1410")
    return s


def главна():
    pygame.init()
    pygame.display.set_mode((1, 1))
    s = довърши(рисувай())
    os.makedirs(os.path.join(ИГРА, "assets", "music"), exist_ok=True)
    pygame.image.save(s, os.path.join(ИГРА, "assets", "music", "kaval.png"))
    фон = pygame.Surface((W * 2, H * 2))
    фон.fill((58, 50, 70))
    фон.blit(pygame.transform.scale(s, (W * 2, H * 2)), (0, 0))
    pygame.image.save(фон, os.path.join(ИГРА, "art_src", "kaval_preview.png"))
    print("assets/music/kaval.png")


if __name__ == "__main__":
    главна()
