# Общ модул за плочките и картите. Ползват го и играта (main.py), и редакторът (editor.py).
# Тук е описано: кои плочки има, как се зареждат картинките им и как се чете/пише карта.
import glob
import json
import os

import pygame

ПАПКА = os.path.dirname(os.path.abspath(__file__))
ПЪТ_ПЛОЧКИ = os.path.join(ПАПКА, "data", "tiles.json")
ПАПКА_КАРТИНКИ = os.path.join(ПАПКА, "assets")
# Тайлсет = една голяма картинка с много квадратчета 64x64 (напр. всички части на стената).
# Слагаш я в assets/tilesets/ и програмата сама я реже: всяко квадратче става отделна плочка
# с име <тайлсет>_<ред>_<колона>, напр. walls_0_2. Празните квадратчета се прескачат.
ПАПКА_ТАЙЛСЕТИ = os.path.join(ПАПКА_КАРТИНКИ, "tilesets")
# Временните картинки от Claude (докато учениците нарисуват своите): същите имена, в assets/_placeholder.
ПАПКА_ВРЕМЕННИ = os.path.join(ПАПКА_КАРТИНКИ, "_placeholder")
ПЪТ_СПИСЪК_КАРТИНКИ = os.path.join(ПАПКА, "data", "art_list.json")


def намери_картинка(относителен):
    """Ученическата картинка има предимство; ако я няма, временната; ако и нея няма, None."""
    for основа in (ПАПКА_КАРТИНКИ, ПАПКА_ВРЕМЕННИ):
        път = os.path.join(основа, относителен)
        if os.path.exists(път):
            return път
    return None


def _данни_от_списъка():
    """Твърдост/слой от data/art_list.json (напр. столът е проходим)."""
    if not os.path.exists(ПЪТ_СПИСЪК_КАРТИНКИ):
        return {}
    with open(ПЪТ_СПИСЪК_КАРТИНКИ, encoding="utf-8") as f:
        return {os.path.splitext(з["file"])[0]: з for з in json.load(f) if "/" not in з["file"]}
ПЛОЧКА = 64                      # мрежа 64x64 (решение от 24.11: героите са 64x64)

# Вградени плочки: играта работи с тях и без нито една картинка (правило 5).
# Ако в assets има картинка със същото име (напр. wall.png), се ползва картинката.
ВГРАДЕНИ = {
    "floor": {"layer": "floor", "w": 1, "h": 1, "solid": False, "color": [150, 110, 70]},
    "wall":  {"layer": "object", "w": 1, "h": 1, "solid": True, "color": [70, 70, 90], "tall": 32},
    "door":  {"layer": "object", "w": 1, "h": 1, "solid": False, "color": [60, 120, 160], "tall": 32},
    "table": {"layer": "object", "w": 1, "h": 1, "solid": True, "color": [110, 70, 40]},
    "bar":   {"layer": "object", "w": 1, "h": 1, "solid": True, "color": [90, 55, 35]},
}
# Картинки с тези начала са под (слой "floor"), всичко друго е предмет
НАЧАЛО_ПОД = ("floor", "tile", "grass", "ground", "road", "path", "water", "sand", "carpet")
# Картинки с тези начала са герои, не плочки: не влизат в редактора
НАЧАЛО_ГЕРОЙ = ("hero", "npc", "char", "person")
ЦВЯТ_КОНТУР = (25, 20, 30)


def зареди_плочки():
    """Връща речник име -> описание. Нови картинки в assets се добавят сами в tiles.json."""
    плочки = {к: dict(в) for к, в in ВГРАДЕНИ.items()}
    if os.path.exists(ПЪТ_ПЛОЧКИ):
        with open(ПЪТ_ПЛОЧКИ, encoding="utf-8") as f:
            for име, описание in json.load(f).items():
                плочки.setdefault(име, {}).update(описание)
    # цвят и височина на вградените идват винаги от кода (не от стар tiles.json)
    for име, в in ВГРАДЕНИ.items():
        for ключ in ("color", "tall"):
            if ключ in в:
                плочки[име][ключ] = в[ключ]
    промяна = False
    # махаме плочки, чиято картинка вече я няма никъде (напр. изтрита)
    for име in [и for и, д in плочки.items() if и not in ВГРАДЕНИ and "sheet" not in д
                and not намери_картинка(и + ".png")]:
        del плочки[име]
        промяна = True
    от_списъка = _данни_от_списъка()
    пътища = sorted(glob.glob(os.path.join(ПАПКА_КАРТИНКИ, "*.png")) + glob.glob(os.path.join(ПАПКА_ВРЕМЕННИ, "*.png")))
    for път in пътища:
        име = os.path.splitext(os.path.basename(път))[0]
        if име in плочки or име.startswith(НАЧАЛО_ГЕРОЙ):
            continue
        w, h = pygame.image.load(път).get_size()
        под = име.startswith(НАЧАЛО_ПОД)
        # Колко клетки заема: по ширина и по височина, кратно на 64 (64x96 заема 1 клетка)
        з = от_списъка.get(име, {})
        if з.get("kind") == "floor":
            под = True
        плочки[име] = {"layer": "floor" if под else "object",
                       "w": max(1, w // ПЛОЧКА), "h": max(1, h // ПЛОЧКА),
                       "solid": з.get("solid", not под)}
        промяна = True
    листове = {}
    for основа in (os.path.join(ПАПКА_ВРЕМЕННИ, "tilesets"), ПАПКА_ТАЙЛСЕТИ):   # ученическият печели
        for път in glob.glob(os.path.join(основа, "*.png")):
            листове[os.path.splitext(os.path.basename(път))[0]] = път
    for лист, път in sorted(листове.items()):
        картинка = pygame.image.load(път)
        под = лист.startswith(НАЧАЛО_ПОД)
        колони = картинка.get_width() // ПЛОЧКА
        редове = картинка.get_height() // ПЛОЧКА
        for р in range(редове):
            for к in range(колони):
                име = "%s_%d_%d" % (лист, р, к)
                if име in плочки:
                    continue
                парче = картинка.subsurface((к * ПЛОЧКА, р * ПЛОЧКА, ПЛОЧКА, ПЛОЧКА))
                if парче.get_bounding_rect(min_alpha=10).width == 0:
                    continue          # празно квадратче
                плочки[име] = {"layer": "floor" if под else "object", "w": 1, "h": 1,
                               "solid": not под, "sheet": лист, "cell": [к, р]}
                промяна = True
    if промяна or not os.path.exists(ПЪТ_ПЛОЧКИ):
        запиши_плочки(плочки)
    return плочки


def запиши_плочки(плочки):
    os.makedirs(os.path.dirname(ПЪТ_ПЛОЧКИ), exist_ok=True)
    # цвета и височината на вградените не ги пишем: те са в кода
    чисти = {и: {к: в for к, в in д.items() if к not in ("color", "tall")} for и, д in плочки.items()}
    with open(ПЪТ_ПЛОЧКИ, "w", encoding="utf-8") as f:
        json.dump(чисти, f, ensure_ascii=False, indent=2)


def _резервна_картинка(описание):
    """Цветен правоъгълник, когато няма картинка."""
    w, h = описание["w"] * ПЛОЧКА, описание["h"] * ПЛОЧКА
    горе = описание.get("tall", 0)
    цвят = описание.get("color", [200, 0, 200])
    s = pygame.Surface((w, h + горе), pygame.SRCALPHA)
    if описание["layer"] == "floor":
        s.fill(цвят)
        pygame.draw.rect(s, [max(0, c - 10) for c in цвят], (0, 0, w, h), 1)
        return s
    if горе:   # стена/врата: горен ръб + лице (GAME_RULES, раздел 6)
        s.fill([min(255, c + 20) for c in цвят], (0, 0, w, горе))
        s.fill(цвят, (0, горе, w, h))
        pygame.draw.rect(s, ЦВЯТ_КОНТУР, s.get_rect(), 1)
    else:
        s.fill(цвят, (1, 1, w - 2, h - 2))
        pygame.draw.rect(s, ЦВЯТ_КОНТУР, (1, 1, w - 2, h - 2), 1)
    return s


def зареди_картинки(плочки):
    """Картинките се зареждат веднъж (правило от раздел 3)."""
    картинки = {}
    има_прозорец = pygame.display.get_surface() is not None
    листове = {}
    for име, описание in плочки.items():
        път = os.path.join(ПАПКА_КАРТИНКИ, име + ".png")
        if "sheet" in описание:
            лист = описание["sheet"]
            if лист not in листове:
                пл = намери_картинка(os.path.join("tilesets", лист + ".png"))
                листове[лист] = pygame.image.load(пл) if пл else None
            if листове[лист] is not None:
                к, р = описание["cell"]
                парче = листове[лист].subsurface((к * ПЛОЧКА, р * ПЛОЧКА, ПЛОЧКА, ПЛОЧКА)).copy()
                картинки[име] = парче.convert_alpha() if има_прозорец else парче
            else:
                картинки[име] = _резервна_картинка(описание)
        elif намери_картинка(име + ".png"):
            к = pygame.image.load(намери_картинка(име + ".png"))
            картинки[име] = к.convert_alpha() if има_прозорец else к
        else:
            картинки[име] = _резервна_картинка(описание)
    return картинки


def нарисувай_плочка(екран, картинка, описание, x, y, кам_x, кам_y):
    """Картинката се подравнява по долния ръб на клетките, които заема."""
    px = x * ПЛОЧКА - кам_x
    py = (y + описание["h"]) * ПЛОЧКА - картинка.get_height() - кам_y
    екран.blit(картинка, (px, py))


# ---------- КАРТИ ----------

def празна_карта(ширина=24, височина=12):
    return {"name": "new_map", "width": ширина, "height": височина,
            "floor": [["floor"] * ширина for _ in range(височина)],
            "objects": [], "start": [1, 1]}


def зареди_карта(път):
    with open(път, encoding="utf-8") as f:
        д = json.load(f)
    if "rows" in д:                      # стар формат (знаци в редове) -> нов
        легенда, редове = д["legend"], д["rows"]
        карта = празна_карта(len(редове[0]), len(редове))
        карта["name"] = д.get("name", "map")
        for y, ред in enumerate(редове):
            for x, знак in enumerate(ред):
                вид = легенда.get(знак, "floor")
                if вид == "start":
                    карта["start"] = [x, y]
                elif вид != "floor":
                    карта["objects"].append({"name": вид, "x": x, "y": y})
        return карта
    return д


def запиши_карта(карта, път):
    os.makedirs(os.path.dirname(път), exist_ok=True)
    # Подът се пише ред по ред, за да се чете лесно и от човек
    редове = ",\n    ".join(json.dumps(р, ensure_ascii=False) for р in карта["floor"])
    обекти = ",\n    ".join(json.dumps(о, ensure_ascii=False) for о in карта["objects"])
    текст = ('{\n  "name": %s,\n  "width": %d,\n  "height": %d,\n  "start": %s,\n'
             '  "floor": [\n    %s\n  ],\n  "objects": [\n    %s\n  ]\n}\n') % (
        json.dumps(карта["name"]), карта["width"], карта["height"], json.dumps(карта["start"]),
        редове, обекти)
    with open(път, "w", encoding="utf-8") as f:
        f.write(текст)
