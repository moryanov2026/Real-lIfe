# Котелът за лютеница: от картинката, направена в Pixel Art Village (64x64, изтеглена "Large"),
# връщаме истинските пиксели, махаме фона и парата, а червената течност става лютеница.
from PIL import Image
import colorsys
im = Image.open("ref.png").convert("RGB")
N = 64; к = im.width / N
мал = Image.new("RGBA", (N, N))
for y in range(N):
    for x in range(N):
        мал.putpixel((x, y), im.getpixel((int((x + 0.5) * к), int((y + 0.5) * к))) + (255,))
мал.save("1_pikseli64.png")
px = мал.load()
def hsv(c):
    return colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)
# ред на ръба: най-горният ред, в който има тъмен чугун широко
ръб = min(y for y in range(N) if sum(1 for x in range(N) if max(px[x, y][:3]) < 70) > 20)
print("ръб", ръб)
ЛЮТ = [(74, 14, 10), (122, 26, 16), (168, 48, 26), (204, 74, 38), (230, 112, 64)]   # от тъмно към светло
for y in range(N):
    for x in range(N):
        r, g, b, a = px[x, y]
        h, s, v = hsv((r, g, b))
        бяло = v > 0.80 and s < 0.18
        розово = s < 0.55 and (h < 0.06 or h > 0.9) and v > 0.75 and y < 14   # парата (светло розово над котела)
        сянка = y > 50 and s < 0.15 and v > 0.40                                     # сянката под котела
        if бяло or розово or сянка:
            px[x, y] = (0, 0, 0, 0)
            continue
        if s > 0.35 and (h < 0.06 or h > 0.92):                 # червената течност -> лютеница
            л = 0.3 * r + 0.59 * g + 0.11 * b
            i = 0 if л < 45 else 1 if л < 75 else 2 if л < 110 else 3 if л < 150 else 4
            px[x, y] = ЛЮТ[i] + (255,)
мал.save("2_lyutenitsa.png")
big = мал.resize((N * 8, N * 8), Image.NEAREST); bg = Image.new("RGBA", big.size, (120, 80, 60, 255)); bg.alpha_composite(big); bg.save("preview.png")

# ---- почистване: гладка лютеница и чугун в ивици, контур ----
import random
W = H = N
непр = [[px[x, y][3] > 0 for x in range(W)] for y in range(H)]
червени = [(x, y) for y in range(H) for x in range(W) if непр[y][x] and px[x, y][:3] in ЛЮТ]
from collections import Counter
поред = Counter(p[1] for p in червени)
червени = [p for p in червени if поред[p[1]] >= 5]                       # без самотни червени точки
xs = [p[0] for p in червени]; ys = [p[1] for p in червени]
cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2 + 0.5
rx, ry = (max(xs) - min(xs)) / 2 - 0.5, (max(ys) - min(ys)) / 2 - 0.5
cy += 0.5
print("лютеница", cx, cy, rx, ry)
течност = set()
for y in range(H):
    for x in range(W):
        nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
        if nx * nx + ny * ny <= 1 and непр[y][x]:
            течност.add((x, y))
сл = random.Random(3)
for (x, y) in течност:
    nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
    v = -0.5 * nx - 0.3 * ny + 0.05 - (0.6 if ny < -0.55 else 0)       # светло отгоре вляво, задният ръб в сянка
    i = 4 if v > 0.55 else 3 if v > 0.15 else 2 if v > -0.25 else 1 if v > -0.6 else 0
    px[x, y] = ЛЮТ[i] + (255,)
for _ in range(14):                                                      # парченца чушка (по-тъмни) и мазнинка (светла)
    x, y = сл.choice(sorted(течност))
    px[x, y] = (ЛЮТ[1] if сл.random() < 0.6 else (250, 160, 100)) + (255,)
# чугун: кръгло тяло, осветено отгоре вляво (по формата, не по шума на снимката)
ЧУГУН = [(14, 14, 20), (30, 32, 40), (48, 52, 62), (70, 78, 88), (102, 114, 122)]
тяло = [(x, y) for y in range(H) for x in range(W) if непр[y][x] and (x, y) not in течност]
редове_тяло = [p for p in тяло if p[1] > cy + ry]
bx0 = min(p[0] for p in редове_тяло if 26 < p[1] < 46); bx1 = max(p[0] for p in редове_тяло if 26 < p[1] < 46)
by0 = cy + ry - 2; by1 = max(p[1] for p in тяло if bx0 + 8 < p[0] < bx1 - 8) + 1
tcx, tcy, trx, try_ = (bx0 + bx1) / 2, (by0 + by1) / 2, (bx1 - bx0) / 2 + 0.5, (by1 - by0) / 2
for (x, y) in тяло:
    nx, ny = (x + 0.5 - tcx) / trx, (y + 0.5 - tcy) / try_
    d = nx * nx + ny * ny
    if d <= 1.05:                                   # тялото: сфера, светлина горе вляво
        v = -0.62 * nx - 0.55 * ny - 0.35 * max(0, d - 0.7)
        i = 4 if v > 0.55 else 3 if v > 0.2 else 2 if v > -0.15 else 1 if v > -0.5 else 0
        if y < tcy - try_ + 3:                      # предният ръб на отвора: тънка светла ивица
            i = min(4, i + 1)
    elif y < cy + ry + 3:                           # ръбът на отвора и дръжките
        i = 3 if x < tcx else 2
    else:                                           # крачетата
        i = 2 if x < tcx else 1
    px[x, y] = ЧУГУН[i] + (255,)
# задният ръб над лютеницата
for (x, y) in тяло:
    if y <= cy and (x, y + 1) in течност:
        px[x, y] = ЧУГУН[3] + (255,)
# самотни пиксели вън
for y in range(H):
    for x in range(W):
        if px[x, y][3] and sum(1 for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)) if 0 <= x+dx < W and 0 <= y+dy < H and px[x+dx, y+dy][3]) == 0:
            px[x, y] = (0, 0, 0, 0)
# дупки вътре (бели отблясъци от снимката): попълваме от съседите
for _ in range(2):
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if not px[x, y][3]:
                съседи = [px[x + dx, y + dy] for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)) if px[x + dx, y + dy][3]]
                if len(съседи) >= 3:
                    px[x, y] = Counter(съседи).most_common(1)[0][0]
# издатини от 1 пиксел и самотни тъмни точки
for _ in range(2):
    for y in range(H):
        for x in range(W):
            if px[x, y][3]:
                съседи = [px[x + dx, y + dy] for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)) if 0 <= x+dx < W and 0 <= y+dy < H and px[x + dx, y + dy][3]]
                if len(съседи) <= 1:
                    px[x, y] = (0, 0, 0, 0)
                elif len(съседи) == 4 and all(с != px[x, y] for с in съседи):
                    px[x, y] = Counter(съседи).most_common(1)[0][0]
# контур
маска = [[px[x, y][3] > 0 for x in range(W)] for y in range(H)]
for y in range(H):
    for x in range(W):
        if not маска[y][x] and any(0 <= x+dx < W and 0 <= y+dy < H and маска[y+dy][x+dx] for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))):
            px[x, y] = (10, 8, 12, 255)
мал.save("3_gotov.png")
big = мал.resize((N * 8, N * 8), Image.NEAREST); bg = Image.new("RGBA", big.size, (120, 80, 60, 255)); bg.alpha_composite(big); bg.save("preview.png")
