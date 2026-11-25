# КАРТИНКИ: временни картинки (от Claude) и списък кое е нарисувано от учениците.
#
# Как работи:
#   - data/art_list.json е списъкът с ВСИЧКИ нужни картинки (име, размер, какво е).
#   - Ученикът слага своята картинка в assets/<файл>   (напр. assets/items/bread.png)
#   - Временната картинка е в assets/_placeholder/<файл>. Играта винаги взима първо
#     ученическата, ако я има. Така временните се заместват сами.
#
# Пускане:  python tools/art.py          -> прави липсващите временни картинки и KARTINKI.html
#           python tools/art.py --force  -> прерисува и съществуващите временни
import html
import json
import os
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

ПАПКА = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
СПИСЪК = os.path.join(ПАПКА, "data", "art_list.json")
УЧЕНИЦИ = os.path.join(ПАПКА, "assets")
ВРЕМЕННИ = os.path.join(ПАПКА, "assets", "_placeholder")
КОНТУР = (25, 20, 30)


def по_светъл(ц, с=30):
    return [min(255, x + с) for x in ц]


def по_тъмен(ц, с=35):
    return [max(0, x - с) for x in ц]


def надпис(повърхност, текст, шрифт, rect):
    """Малък надпис, за да се познае какво е, докато няма истинска картинка."""
    думи = текст.split(" ")[0][:9]
    н = шрифт.render(думи, False, (255, 255, 255))
    фон = pygame.Surface((н.get_width() + 2, н.get_height()), pygame.SRCALPHA)
    фон.fill((0, 0, 0, 150))
    x = rect.centerx - фон.get_width() // 2
    y = rect.bottom - фон.get_height() - 2
    повърхност.blit(фон, (x, y))
    повърхност.blit(н, (x + 1, y))


def нарисувай(запис, шрифт):
    w, h = запис["size"]
    ц = запис["color"]
    вид = запис["kind"]
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    if вид == "floor":
        s.fill(ц)
        for y in range(0, h, 16):                  # дъски
            pygame.draw.line(s, по_тъмен(ц, 25), (0, y), (w, y))
            pygame.draw.line(s, по_тъмен(ц, 25), ((y * 3) % w, y), ((y * 3) % w, y + 15))
        return s
    if вид == "tileset":
        for ry in range(h // 64):
            for rx in range(w // 64):
                r = pygame.Rect(rx * 64, ry * 64, 64, 64)
                pygame.draw.rect(s, по_светъл(ц, 25) if ry == 0 else ц, r.inflate(-2, -2))
                pygame.draw.rect(s, КОНТУР, r.inflate(-2, -2), 1)
                надпис(s, "%d_%d" % (ry, rx), шрифт, r)
        return s
    if вид == "person":
        сянка = None
        тяло = pygame.Rect(w // 2 - 14, h - 40, 28, 38)
        глава = pygame.Rect(w // 2 - 11, h - 62, 22, 22)
        pygame.draw.rect(s, ц, тяло)
        pygame.draw.rect(s, КОНТУР, тяло, 1)
        pygame.draw.rect(s, (235, 200, 170), глава)
        pygame.draw.rect(s, КОНТУР, глава, 1)
        return s
    if вид in ("item", "icon", "note"):
        r = s.get_rect().inflate(-max(2, w // 8), -max(2, h // 8))
        pygame.draw.ellipse(s, ц, r) if вид == "item" else pygame.draw.rect(s, ц, r, border_radius=4)
        pygame.draw.ellipse(s, по_светъл(ц, 40), r.inflate(-r.w // 2, -r.h // 2).move(-r.w // 8, -r.h // 8)) \
            if вид == "item" else None
        (pygame.draw.ellipse if вид == "item" else pygame.draw.rect)(s, КОНТУР, r, 1)
        if w >= 64:
            надпис(s, запис["name_bg"].replace("Икона: ", ""), шрифт, s.get_rect())
        return s
    if вид == "bg":
        s.fill(ц)
        return s
    # мебел / висока станция: плот отгоре (по-светъл), предна стена, крачета
    височина_горе = int(h * (0.35 if вид == "tall" else 0.55))
    горе = pygame.Rect(3, 4, w - 6, височина_горе)
    предна = pygame.Rect(3, 4 + височина_горе, w - 6, h - височина_горе - 14)
    pygame.draw.rect(s, по_тъмен(ц), (6, h - 12, 8, 10))
    pygame.draw.rect(s, по_тъмен(ц), (w - 14, h - 12, 8, 10))
    pygame.draw.rect(s, по_светъл(ц), горе)
    pygame.draw.rect(s, ц, предна)
    pygame.draw.rect(s, КОНТУР, горе.union(предна), 1)
    pygame.draw.line(s, КОНТУР, (3, горе.bottom), (w - 4, горе.bottom))
    надпис(s, запис["name_bg"], шрифт, горе.union(предна))
    return s


def главна():
    принудително = "--force" in sys.argv
    pygame.init()
    шрифт = pygame.font.SysFont("arial", 10)
    with open(СПИСЪК, encoding="utf-8") as f:
        списък = json.load(f)
    нови = 0
    редове = []
    готови = 0
    for з in списък:
        у = os.path.join(УЧЕНИЦИ, з["file"])
        в = os.path.join(ВРЕМЕННИ, з["file"])
        if принудително or not os.path.exists(в):
            os.makedirs(os.path.dirname(в), exist_ok=True)
            pygame.image.save(нарисувай(з, шрифт), в)
            нови += 1
        статус, бележка, картинка = "временна", "", в
        if os.path.exists(у):
            картинка = у
            размер = list(pygame.image.load(у).get_size())
            if размер == з["size"]:
                статус = "нарисувана"
                готови += 1
            else:
                статус = "грешен размер"
                бележка = "е %d×%d, трябва %d×%d" % (*размер, *з["size"])
        редове.append((з, статус, бележка, os.path.relpath(картинка, ПАПКА).replace("\\", "/")))
    # HTML страница със статуса
    цветове = {"нарисувана": "#2e7d32", "временна": "#9e7b00", "грешен размер": "#c62828"}
    тр = []
    for з, статус, бележка, картинка in редове:
        мащаб = 2 if з["size"][0] <= 128 else 0.25
        тр.append('<tr><td><img src="%s" width="%d" style="image-rendering:pixelated;background:#8a6a45"></td>'
                  '<td>%s</td><td><code>assets/%s</code></td><td>%d × %d</td><td>%s</td>'
                  '<td style="color:%s;font-weight:bold">%s %s</td></tr>' % (
                      html.escape(картинка), з["size"][0] * мащаб, html.escape(з["name_bg"]), html.escape(з["file"]),
                      з["size"][0], з["size"][1], html.escape(з["where"]), цветове[статус], статус, html.escape(бележка)))
    страница = """<!DOCTYPE html><html lang="bg"><head><meta charset="utf-8"><title>Real Life - картинки</title>
<style>body{font-family:Arial;margin:20px}table{border-collapse:collapse}td,th{border:1px solid #bbb;padding:4px 8px;font-size:14px}
th{background:#eee;position:sticky;top:0}</style></head><body>
<h1>Real Life: картинки (%d от %d нарисувани)</h1>
<p>Ученикът рисува в Piskel в точния размер и слага файла на мястото от колона „Файл“. Играта сама я взима вместо временната.
След като сложите нови картинки, пуснете <b>kartinki.bat</b>, за да се обнови тази страница.</p>
<table><tr><th>Сега</th><th>Какво е</th><th>Файл</th><th>Размер</th><th>Къде е описано</th><th>Статус</th></tr>%s</table></body></html>""" % (
        готови, len(списък), "\n".join(тр))
    with open(os.path.join(ПАПКА, "KARTINKI.html"), "w", encoding="utf-8") as f:
        f.write(страница)
    print("Временни картинки направени сега: %d" % нови)
    print("Нарисувани от учениците: %d от %d" % (готови, len(списък)))
    for з, статус, бележка, _ in редове:
        if статус == "грешен размер":
            print("  ВНИМАНИЕ: assets/%s %s" % (з["file"], бележка))
    print("Списъкът: KARTINKI.html")


if __name__ == "__main__":
    главна()
