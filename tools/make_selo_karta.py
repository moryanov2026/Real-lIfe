# Прави картите на селото и на магазина:
#   data/maps/selo.json     - селото (под и предмети)
#   data/maps/magazin.json  - магазинът отвътре
#   data/selo.json          - къде са вратите, къщите, сергиите, нивите, кладенецът, животните
# Пускане от папката "Real Life":   python tools/make_selo_karta.py
# data/selo.json:
#   врати    - клетките пред вратите на сградите в селото и къде водят (krachma, magazin)
#   входове  - къде излиза човек, който излиза от сградата
#   домове   - клетката пред вратата на всеки жител (там е вкъщи)
#   пазар    - клетките пред сергиите (там се пазарува и продава)
#   ниви     - клетките с нивите на селянина
import json
import os
import random
import sys

ТУК = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ТУК))
import tiles

Ш, В = 48, 24
сл = random.Random(4)
карта = tiles.празна_карта(Ш, В)
карта["name"] = "selo"
карта["floor"] = [[сл.choice(("grass", "grass", "grass2")) for _ in range(Ш)] for _ in range(В)]
обекти = []


def път(x0, y0, x1, y1, под="path"):
    for y in range(min(y0, y1), max(y0, y1) + 1):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            if 0 <= x < Ш and 0 <= y < В:
                карта["floor"][y][x] = под


def сложи(име, x, y):
    обекти.append({"name": име, "x": x, "y": y})


# кръчмата горе в средата, площад пред нея, улиците
сложи("krachma_out", 17, 2)
път(16, 5, 23, 7)
път(19, 5, 20, 22)                    # главната улица надолу
път(0, 11, 47, 12)                    # голямата улица през селото
сложи("kladenets", 23, 9)
# къщите: (кой, картинка, x, y); пред вратата има пътечка до улицата
къщи = [("baba_stana", "house_a", 2, 2), ("dyado_kole", "house_b", 9, 2), ("patnik_niki", "house_b", 28, 2),
        ("lovets_boris", "house_a", 33, 2), ("elena", "house_a", 33, 15), ("selyanin", "house_b", 1, 14)]
домове = {}
for кой, картинка, x, y in къщи:
    сложи(картинка, x, y)
    домове[кой] = [x + 2, y + 3]
    път(x + 2, y + 3, x + 2, 11 if y < 11 else 12)
# магазинът (вратата е отдолу в средата)
сложи("magazin_out", 25, 14)
път(20, 17, 27, 17)
# църквата и камбанарията (вдясно)
сложи("tsarkva_out", 40, 13)
сложи("kambanaria", 46, 16)
път(35, 18, 47, 19)
път(42, 17, 43, 18)
път(39, 12, 39, 18)
# пазарът долу
пазар = []
for x in (22, 25, 28):
    сложи("sergia", x, 19)
    пазар.append([x + 1, 20])
път(21, 20, 31, 21)
# фермата на селянина: ниви, кокошарник, крава
ниви = []
for y in (16, 18):
    for x in range(6, 12):
        път(x, y, x, y, "niva")
        ниви.append([x, y])
път(6, 17, 11, 17)                    # пътечка между нивите
път(5, 15, 5, 21)
сложи("kokoshkarnik", 13, 15)
сложи("krava", 13, 19)
# дървета, ограда, цветя
for (x, y) in ((14, 3), (6, 7), (25, 4), (37, 6), (16, 14), (2, 21), (34, 21), (24, 22), (37, 14), (12, 21), (44, 6), (40, 21)):
    сложи("darvo", x, y)
for x in range(6, 10):              # оградите не пресичат пътечките до къщите
    сложи("ograda", x, 9)
for x in range(31, 35):
    сложи("ograda", x, 9)
for (x, y) in ((1, 6), (8, 6), (27, 6), (34, 6), (17, 9), (22, 4), (30, 14), (45, 20), (39, 20)):
    сложи("tsvetya", x, y)
карта["objects"] = обекти
карта["start"] = [19, 6]
tiles.запиши_карта(карта, os.path.join(tiles.ПАПКА, "data", "maps", "selo.json"))

# ---------- магазинът отвътре ----------
м = tiles.празна_карта(12, 8)
м["name"] = "magazin"
м["floor"] = [["floor"] * 12 for _ in range(8)]
мо = []
for x in range(12):
    мо.append({"name": "window" if x in (3, 8) else "wall", "x": x, "y": 0})
    if x not in (5, 6):
        мо.append({"name": "wall", "x": x, "y": 7})
    else:
        мо.append({"name": "door", "x": x, "y": 7})
for y in range(1, 7):
    мо.append({"name": "wall", "x": 0, "y": y})
    мо.append({"name": "wall", "x": 11, "y": y})
for x in range(1, 11):
    if x not in (5,):
        мо.append({"name": "shelf", "x": x, "y": 1})
for x in range(2, 9):
    мо.append({"name": "bar", "x": x, "y": 3})       # тезгяхът
мо.append({"name": "cash", "x": 9, "y": 3})          # касата
мо.append({"name": "chest", "x": 1, "y": 5})
мо.append({"name": "chest", "x": 10, "y": 5})
м["objects"] = мо
м["start"] = [5, 5]
tiles.запиши_карта(м, os.path.join(tiles.ПАПКА, "data", "maps", "magazin.json"))

# ---------- църквата отвътре ----------
ц = tiles.празна_карта(12, 9)
ц["name"] = "tsarkva"
ц["floor"] = [["kamak_pod"] * 12 for _ in range(9)]
цо = []
for x in range(12):
    цо.append({"name": "window" if x in (2, 9) else "wall", "x": x, "y": 0})
    цо.append({"name": "door" if x in (5, 6) else "wall", "x": x, "y": 8})
for y in range(1, 8):
    цо.append({"name": "wall", "x": 0, "y": y})
    цо.append({"name": "wall", "x": 11, "y": y})
цо.append({"name": "ikonostas", "x": 3, "y": 1})
цо.append({"name": "svechnik", "x": 2, "y": 5})
цо.append({"name": "kupel", "x": 9, "y": 4})
ц["objects"] = цо
ц["start"] = [5, 4]
tiles.запиши_карта(ц, os.path.join(tiles.ПАПКА, "data", "maps", "tsarkva.json"))

инфо = {"_бележка": "Селото: къде са вратите на сградите, къщите на жителите, сергиите и нивите. Прави се с tools/make_selo_karta.py.",
        "врати": [{"x": 19, "y": 5, "към": "krachma"}, {"x": 20, "y": 5, "към": "krachma"},
                  {"x": 26, "y": 17, "към": "magazin"}, {"x": 27, "y": 17, "към": "magazin"},
                  {"x": 42, "y": 17, "към": "tsarkva"}, {"x": 43, "y": 17, "към": "tsarkva"}],
        "входове": {"krachma": [19, 6], "magazin": [26, 18], "tsarkva": [42, 18]},
        "камбанария": [46, 17],
        "домове": домове, "пазар": пазар, "ниви": ниви,
        "кладенец": [23, 10], "кокошарник": [14, 17], "крава": [13, 20]}
with open(os.path.join(tiles.ПАПКА, "data", "selo.json"), "w", encoding="utf-8") as f:
    json.dump(инфо, f, ensure_ascii=False, indent=1)
print("data/maps/selo.json, data/maps/magazin.json, data/maps/tsarkva.json, data/selo.json")
