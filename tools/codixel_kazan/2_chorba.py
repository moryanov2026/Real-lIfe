# Казанът от снимката (Codixel: без фон -> пиксели -> ивици) + чорбата вътре, 4 кадъра мехурчета
from PIL import Image
import math, random
kazan = Image.open("2_pikseli.png").convert("RGBA")
kp = kazan.load()
лум = lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
for y in range(78, kazan.height):                  # под дъното: оставяме само тъмните крачета (сянката на снимката - не)
    for x in range(kazan.width):
        c = kp[x, y]
        if c[3] and лум(c) > 80:
            kp[x, y] = (0, 0, 0, 0)
# 1 px контур в най-тъмния цвят на чугуна, за да се чете казанът и на тъмен фон
КОНТУР = (14, 14, 20, 255)
маска = [[kp[x, y][3] > 0 for x in range(kazan.width)] for y in range(kazan.height)]
нов = kazan.copy(); np_ = нов.load()
for y in range(kazan.height):
    for x in range(kazan.width):
        if not маска[y][x] and any(0 <= x + dx < kazan.width and 0 <= y + dy < kazan.height and маска[y + dy][x + dx]
                                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            np_[x, y] = КОНТУР
kazan = нов
W, H = 120, 92
SUPA = [(240,180,100), (204,130,54), (154,90,30), (106,58,18)]
БОБ = [(251,232,196), (216,184,136)]
ЗЕЛЕНО = (60,154,74)
cx, cy, rx, ry = 61, 21, 40.5, 6.6           # повърхността на чорбата (малко под ръба)
кадри = []
for к in range(4):
    im = Image.new("RGBA", (W, H), (0,0,0,0))
    im.paste(kazan, (0, 2), kazan)
    px = im.load()
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            d = nx * nx + ny * ny
            if d > 1: continue
            # светлина отгоре вляво; към далечния ръб (горе) чорбата е в сянката на стената
            v = -0.45 * nx - 0.35 * ny + 0.15 - (0.55 if ny < -0.55 else 0) - 0.25 * max(0, d - 0.75) * 4
            i = 0 if v > 0.45 else 1 if v > 0.0 else 2 if v > -0.45 else 3
            # тънка ивица шахматно смесване на границите
            if 0 < i and abs(v - (0.45, 0.0, -0.45)[i - 1]) < 0.06 and (x + y) % 2: i -= 1
            px[x, y] = SUPA[i] + (255,)
    сл = random.Random(7)
    for _ in range(26):                     # бобчета
        x, y = сл.uniform(cx - rx * 0.85, cx + rx * 0.85), сл.uniform(cy - ry * 0.4, cy + ry * 0.8)
        if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 0.8:
            px[int(x), int(y)] = БОБ[0] + (255,); px[int(x) + 1, int(y)] = БОБ[1] + (255,)
    for (x, y) in ((44, 21), (70, 24), (84, 20), (55, 25), (35, 23)):   # джоджен
        px[x, y] = ЗЕЛЕНО + (255,)
    for b, (bx, by) in enumerate(((40, 22), (60, 25), (78, 21), (66, 19), (50, 20))):   # мехурчета
        f = (к + b) % 4
        r = (0, 1, 2, 1)[f]
        if r:
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if dx * dx + dy * dy <= r * r + 0.5:
                        px[bx + dx, by + dy] = (SUPA[0] if dy < 0 else SUPA[1]) + (255,)
            px[bx - r, by - r] = (255, 244, 220, 255)
    кадри.append(im)
лист = Image.new("RGBA", (W * 4, H), (0,0,0,0))
for к, im in enumerate(кадри): лист.paste(im, (W * к, 0))
лист.save("bob_garne.png")
big = лист.resize((W * 4 * 4, H * 4), Image.NEAREST); bg = Image.new("RGBA", big.size, (120, 80, 60, 255)); bg.alpha_composite(big); bg.save("preview.png")
