# Обща палитра на играта (64 цвята), по правилата на скила pixel-art-sprites:
# "по-малко цветове = по-добри решения", всичко да изглежда като един свят.
# Пускане от папката "Real Life":   python tools/pixelart/palitra.py
# Взима цветовете от картинките, които рисуват програмите в tools/pixelart, и ги свежда до
# 51 цвята (median cut), плюс 13 задължителни (шевици, огън, контур, тъмни сиви). Записва:
#   data/palitra.json     - за pix.py (в новия стил всяка картинка се свежда до тези цветове)
#   art_src/palitra.gpl   - за Piskel / GIMP (Palettes -> Import), за да рисуват учениците със същите цветове
#   art_src/palitra.png   - мостра
# След като я смените, пуснете пак make_*.py, за да се прерисува всичко.
import glob
import json
import os

from PIL import Image

ИГРА = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ЗАДЪЛЖИТЕЛНИ = ["#1e1410", "#16141a", "#28252c", "#3c383e", "#58545c", "#b4e0f4", "#7cb8dc", "#d8322e", "#f08c2a", "#3c9a4a", "#f2c230", "#2e6ad0", "#fff6b0", "#ffffff"]


def главна():
    файлове = [f for f in glob.glob(os.path.join(ИГРА, "assets", "**", "*.png"), recursive=True)
               if "_placeholder" not in f and os.sep + "music" + os.sep not in f and "tilesets" not in f]
    пиксели = []
    for f in файлове:
        im = Image.open(f).convert("RGBA")
        пиксели += [p[:3] for p in (im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()) if p[3] > 200]
    print("картинки:", len(файлове), "пиксела:", len(пиксели))
    # всеки цвят се брои поне 40 пъти: и редките цветове (зелената трева, камъните) да влязат в палитрата
    from collections import Counter
    брой = Counter(пиксели)
    пиксели = [ц for ц, н in брой.items() for _ in range(max(40, min(н, 400)))]
    всички = Image.new("RGB", (len(пиксели), 1))
    всички.putdata(пиксели)
    q = всички.quantize(colors=49, method=Image.Quantize.MEDIANCUT)
    пал = q.getpalette()[:49 * 3]
    цветове = ["#%02x%02x%02x" % tuple(пал[i:i + 3]) for i in range(0, len(пал), 3)]
    for ц in ЗАДЪЛЖИТЕЛНИ:
        if ц not in цветове:
            цветове.append(ц)
    цветове = sorted(set(цветове), key=lambda ц: (sum(int(ц[i:i + 2], 16) for i in (1, 3, 5))))
    with open(os.path.join(ИГРА, "data", "palitra.json"), "w", encoding="utf-8") as f:
        json.dump({"_бележка": "Обща палитра на играта. Прави я tools/pixelart/palitra.py", "цветове": цветове}, f, indent=1)
    with open(os.path.join(ИГРА, "art_src", "palitra.gpl"), "w", encoding="utf-8") as f:
        f.write("GIMP Palette\nName: Real Life\nColumns: 8\n#\n")
        for ц in цветове:
            r, g, b = (int(ц[i:i + 2], 16) for i in (1, 3, 5))
            f.write("%3d %3d %3d\t%s\n" % (r, g, b, ц))
    мостра = Image.new("RGB", (8 * 24, ((len(цветове) + 7) // 8) * 24), (40, 30, 24))
    for и, ц in enumerate(цветове):
        мостра.paste(tuple(int(ц[i:i + 2], 16) for i in (1, 3, 5)), ((и % 8) * 24, (и // 8) * 24, (и % 8) * 24 + 22, (и // 8) * 24 + 22))
    мостра.save(os.path.join(ИГРА, "art_src", "palitra.png"))
    print("цветове:", len(цветове))


if __name__ == "__main__":
    главна()
