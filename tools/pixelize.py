# Превръща "сурова" картинка (AI или снимка) в готов за играта пиксел-арт файл.
# Какво прави: маха фона -> реже по съдържанието -> смалява до размера от GAME_RULES
#              -> сваля цветовете до малка палитра -> по желание добавя тъмен контур 1 px.
# Ползва само Pygame (правило: без нови библиотеки).
#
# Пускане (от папката "Real Life"):
#   python tools/pixelize.py raw_art --preset hero --colors 10
#   python tools/pixelize.py raw_art/dyrvo.png --preset icon --colors 8 --out assets
import argparse
import os
import re
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")   # не ни трябва прозорец
import pygame

# Размери от GAME_RULES.md, раздел 6 (ширина, височина)
ПРЕСЕТИ = {
    "hero": (64, 64), "wall": (64, 96), "door": (64, 96), "window": (64, 96),
    "tile": (64, 64), "floor": (64, 64), "object": (64, 64), "icon": (64, 64),
    "table_big": (128, 64), "bed": (64, 128), "item": (32, 32),
    "building_s": (192, 192), "building_m": (256, 256), "building_l": (320, 256),
    "tileset": None,   # не смалява: само маха фона и сваля цветовете (за листове с квадратчета)
}
ЦВЯТ_КОНТУР = (25, 20, 30)          # същият тъмен контур като в играта
ДОПУСК_ФОН = 40                     # колко различен цвят още се брои за фон


def безопасно_име(име):
    """Правило 6: само латиница, малки букви, без интервали."""
    име = os.path.splitext(име)[0].lower().replace(" ", "_").replace("-", "_")
    име = re.sub(r"[^a-z0-9_]", "", име)
    return име or "img"


def разлика(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def махни_фона(повърхност):
    """Ако картинката вече е прозрачна, не пипаме. Иначе фонът е цветът на ъглите."""
    w, h = повърхност.get_size()
    ъгли = [повърхност.get_at(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
    if any(ц.a < 250 for ц in ъгли):
        return повърхност
    фон = ъгли[0]
    if any(разлика(ц, фон) > ДОПУСК_ФОН for ц in ъгли):
        return повърхност          # ъглите са различни: не гадаем, оставяме както е
    # Само връзката с краищата се изтрива (flood fill), за да не изяде цветове вътре в героя
    резултат = повърхност.convert_alpha()
    видяни = set()
    стек = [(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)] + \
           [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]
    while стек:
        x, y = стек.pop()
        if (x, y) in видяни or not (0 <= x < w and 0 <= y < h):
            continue
        ц = резултат.get_at((x, y))
        if разлика(ц, фон) > ДОПУСК_ФОН:
            continue
        видяни.add((x, y))
        резултат.set_at((x, y), (ц.r, ц.g, ц.b, 0))
        стек.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return резултат


def реж_по_съдържание(повърхност):
    рамка = повърхност.get_bounding_rect(min_alpha=10)
    if рамка.width == 0 or рамка.height == 0:
        return повърхност
    return повърхност.subsurface(рамка).copy()


def смали_във(повърхност, ширина, височина, вътрешен_ръб):
    """Вписва картинката в (ширина x височина), подравнена по долния ръб, по средата."""
    мак_w, мак_h = ширина - 2 * вътрешен_ръб, височина - вътрешен_ръб
    w, h = повърхност.get_size()
    мащаб = min(мак_w / w, мак_h / h)
    нов = (max(1, round(w * мащаб)), max(1, round(h * мащаб)))
    # За смаляване от голяма картинка усредняването дава по-чисти цветове от "най-близък съсед"
    малка = pygame.transform.smoothscale(повърхност.convert_alpha(), нов)
    платно = pygame.Surface((ширина, височина), pygame.SRCALPHA)
    платно.blit(малка, ((ширина - нов[0]) // 2, височина - вътрешен_ръб - нов[1]))
    return платно


def намали_цветовете(повърхност, брой):
    """Взима най-честите цветове и всичко друго го заменя с най-близкия от тях.
    Полупрозрачните пиксели стават или напълно прозрачни, или плътни (няма преливания)."""
    w, h = повърхност.get_size()
    пиксели = {}
    for y in range(h):
        for x in range(w):
            ц = повърхност.get_at((x, y))
            if ц.a < 128:
                continue
            # групираме близки цветове по 16 нива, за да се броят заедно
            ключ = (ц.r // 16 * 16 + 8, ц.g // 16 * 16 + 8, ц.b // 16 * 16 + 8)
            пиксели[ключ] = пиксели.get(ключ, 0) + 1
    палитра = [ц for ц, _ in sorted(пиксели.items(), key=lambda е: -е[1])[:брой]]
    изход = pygame.Surface((w, h), pygame.SRCALPHA)
    if not палитра:
        return изход
    for y in range(h):
        for x in range(w):
            ц = повърхност.get_at((x, y))
            if ц.a < 128:
                continue
            най = min(палитра, key=lambda п: разлика(п, (ц.r, ц.g, ц.b)))
            изход.set_at((x, y), (*най, 255))
    return изход


def добави_контур(повърхност):
    w, h = повърхност.get_size()
    изход = повърхност.copy()
    for y in range(h):
        for x in range(w):
            if повърхност.get_at((x, y)).a >= 128:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and повърхност.get_at((nx, ny)).a >= 128:
                    изход.set_at((x, y), (*ЦВЯТ_КОНТУР, 255))
                    break
    return изход


def обработи(път_вход, път_изход, размер, цветове, контур):
    картинка = pygame.image.load(път_вход)
    картинка = махни_фона(картинка)
    if размер is None:                 # тайлсет: размерът остава, кратен на 64
        w, h = картинка.get_size()
        картинка = намали_цветовете(картинка.subsurface((0, 0, w - w % 64, h - h % 64)).copy(), цветове)
        pygame.image.save(картинка, път_изход)
        return цветове
    картинка = реж_по_съдържание(картинка)
    ръб = 1 if контур else 0          # оставяме място за контура
    картинка = смали_във(картинка, размер[0], размер[1], ръб + 1)
    картинка = намали_цветовете(картинка, цветове)
    if контур:
        картинка = добави_контур(картинка)
    pygame.image.save(картинка, път_изход)
    used = len({tuple(картинка.get_at((x, y)))[:3] for x in range(размер[0]) for y in range(размер[1])
                if картинка.get_at((x, y)).a > 0})
    return used


def главна():
    п = argparse.ArgumentParser(description="Суров образ -> пиксел-арт за играта Real Life")
    п.add_argument("вход", help="картинка или папка с картинки")
    п.add_argument("--preset", choices=sorted(ПРЕСЕТИ), default="hero")
    п.add_argument("--colors", type=int, default=10, help="най-много цветове (8-12)")
    п.add_argument("--no-outline", action="store_true", help="без тъмен контур")
    п.add_argument("--out", default="assets", help="папка за резултата")
    а = п.parse_args()

    pygame.init()
    pygame.display.set_mode((1, 1))
    os.makedirs(а.out, exist_ok=True)
    if os.path.isdir(а.вход):
        файлове = [os.path.join(а.вход, f) for f in sorted(os.listdir(а.вход))
                   if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp"))]
    else:
        файлове = [а.вход]
    if not файлове:
        print("Няма картинки във входа.")
        return 1
    for ф in файлове:
        име = безопасно_име(os.path.basename(ф)) + ".png"
        папка = os.path.join(а.out, "tilesets") if а.preset == "tileset" else а.out
        os.makedirs(папка, exist_ok=True)
        изход = os.path.join(папка, име)
        try:
            брой = обработи(ф, изход, ПРЕСЕТИ[а.preset], а.colors, not а.no_outline)
            print("OK  %s -> %s  (%s, %d цвята)" % (os.path.basename(ф), изход,
                                                    ПРЕСЕТИ[а.preset] or "тайлсет", брой))
        except Exception as грешка:      # една лоша картинка да не спира останалите
            print("ГРЕШКА при %s: %s" % (ф, грешка))
    return 0


if __name__ == "__main__":
    sys.exit(главна())
