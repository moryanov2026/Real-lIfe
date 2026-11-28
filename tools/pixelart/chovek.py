# Общ "човек" за персоните, които още нямат свой художник: Петър, Мария, Тодор, Георги, Ники,
# дядо Коле, Борис. Всеки е описан в ХОРА (дрехи, коса, шапка, мустаци...), а тялото е общо.
# front(х, i) = отпред, front(х, i, True) = отзад, side(х, i) = надясно, dance(х, i) = хоро.
# Учениците могат да сменят цветовете в ХОРА или да ги прерисуват в Piskel (art_src/<id>_walk.piskel).
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pix import *

M = lambda *a: tuple(hx(c) for c in a)
SKIN = M('#f4d2b0', '#e8b78e', '#cc916a', '#9a6448')
SKIN_OLD = M('#eecaa8', '#dcae88', '#bc8a66', '#8a5e44')
OUT = hx('#1e1410'); EYE = hx('#2a1d16'); MOUTH = hx('#8c4a3e'); BLUSH = hx('#eca088')
RED = hx('#d8322e'); ORANGE = hx('#f08c2a'); GREEN = hx('#3c9a4a'); YEL = hx('#f2c230'); WHITE = hx('#fbf8f0')
SHIRT = M('#ffffff', '#f1ede4', '#d8d0c0', '#aaa292')

ХОРА = {
    # кръчмарят: бяла риза, кафяв елек, тъмночервен пояс, кафяви потури, бяла престилка, мустаци
    "krachmar": dict(коса=M('#8a5a34', '#6a4226', '#4c2e1a', '#301c10'), мустаци=True,
                     риза=SHIRT, елек=M('#b07a4a', '#8a5a30', '#663e1e', '#422610'), пояс=M('#c43a34', '#9a2424', '#721818', '#4a0e10'),
                     крачоли=M('#8a6a4e', '#6a4e36', '#4e3826', '#322418'), престилка=M('#ffffff', '#efebe2', '#d4ccbc', '#a8a090'),
                     обувки=M('#4a3a30', '#342822', '#241c18', '#16100c'), шевици=True),
    # готвачката: червен сукман, бяла престилка и забрадка
    "gotvach": dict(жена=True, коса=M('#5a3a2a', '#40281c', '#2c1a12', '#1a0e08'), забрадка=M('#ffffff', '#f2eee6', '#d8d0c0', '#aca492'),
                    риза=SHIRT, рокля=M('#e2564e', '#c03430', '#922224', '#601416'), престилка=M('#ffffff', '#efebe2', '#d4ccbc', '#a8a090'),
                    обувки=M('#3a3236', '#2a2428', '#1c181a', '#100c0e'), шевици=True, бузи=True),
    # чистачът: синя работна риза, кафяви панталони, сива престилка, каскет
    "chistach": dict(коса=M('#6a5a4a', '#4e4034', '#382e24', '#221a14'), шапка="каскет", шапка_цвят=M('#7a7468', '#5a554c', '#403c36', '#2a2724'),
                     риза=M('#8ab0d8', '#5a86b8', '#3e6292', '#28426a'), крачоли=M('#8a6a4e', '#6a4e36', '#4e3826', '#322418'),
                     престилка=M('#b8b4aa', '#98948a', '#78746a', '#56524a'), обувки=M('#4a3a30', '#342822', '#241c18', '#16100c'), мустаци=True),
    # снабдителят: кафява дреха (ямурлук), черен калпак, брада - носи стоката за кръчмата
    "snabditel": dict(коса=M('#4a3424', '#34241a', '#241810', '#140c08'), шапка="калпак", брада=True, мустаци=True,
                      риза=SHIRT, дреха=M('#a07850', '#7e5a38', '#5e4026', '#3e2816'), пояс=M('#c43a34', '#9a2424', '#721818', '#4a0e10'),
                      крачоли=M('#e6dcc6', '#cfc2a6', '#b0a284', '#867a62'), обувки=M('#4a3a30', '#342822', '#241c18', '#16100c'), едър=True),
    # пътникът: млад, тъмнозелена пелерина, шапка с периферия, торба
    "patnik_niki": dict(коса=M('#c89a5a', '#a87a40', '#82582a', '#5a3a18'), шапка="периферия", шапка_цвят=M('#8a6a4a', '#6a4e34', '#4e3824', '#322216'),
                        риза=M('#f0e6c8', '#ddd0aa', '#bcae88', '#928466'), дреха=M('#4e8a5a', '#366e44', '#265232', '#183822'),
                        крачоли=M('#6a6070', '#4e4656', '#38323e', '#242028'), обувки=M('#5a4232', '#3e2c22', '#2a1e16', '#18100c'), торба=True),
    # дядо Коле: бели коси и мустаци, сив елек, черен калпак, бастун, малко прегърбен
    "dyado_kole": dict(коса=M('#f4f2ee', '#dedad2', '#c0bab0', '#948e84'), кожа=SKIN_OLD, шапка="калпак", мустаци=True, стар=True,
                       риза=SHIRT, елек=M('#8a8890', '#6a6870', '#4e4c54', '#34323a'), пояс=M('#3e3a44', '#28252e', '#1c1a22', '#0f0e13'),
                       крачоли=M('#4a4652', '#2e2b34', '#1e1c24', '#121016'), обувки=M('#3a3230', '#262020', '#181414', '#0c0a0a'), бастун=True),
    # ловецът Борис: зелено-кафява дреха, шапка с перо, брада
    "lovets_boris": dict(коса=M('#7a4a2a', '#5a341c', '#402412', '#28160a'), шапка="перо", шапка_цвят=M('#6a7a3a', '#4e5c28', '#38441c', '#242c12'),
                         брада=True, мустаци=True, риза=M('#e6dcc6', '#cfc2a6', '#b0a284', '#867a62'),
                         дреха=M('#7a8a4a', '#5c6c34', '#424e24', '#2a3216'), пояс=M('#6a4a2a', '#4e341c', '#382412', '#24160a'),
                         крачоли=M('#6a5a46', '#4e4232', '#382e22', '#241e16'), обувки=M('#4a3a30', '#342822', '#241c18', '#16100c'), едър=True),
}


def rot(p, ang, L):
    a = math.radians(ang); return (p[0] + L * math.sin(a), p[1] + L * math.cos(a))


def _ширина(х):
    return 1.15 if х.get("едър") else 1.0


def ръка(cv, х, sh, el, hd, z, ex=0.0, шевици=True):
    ръкав = х.get("дреха") or х["риза"]
    capsule(cv, sh, el, 2.6, 2.3, ръкав, z, extra=ex)
    capsule(cv, el, hd, 2.3, 2.0, ръкав, z, extra=ex)
    if шевици and х.get("шевици"):
        mx, my = el[0] + (hd[0] - el[0]) * 0.7, el[1] + (hd[1] - el[1]) * 0.7
        for d, c in ((-1, RED), (0, YEL), (1, RED)):
            cv.plot(int(mx + d), int(my), c, z + 0.6, 978)
    гънка(cv, el, ръкав, z)
    ellipse(cv, hd[0], hd[1] + 1.3, 1.9, 1.9, х.get("кожа", SKIN), z + 0.3, extra=-0.1)
    if х.get("бастун") and sh[0] > 32 and шевици:          # бастунът е в дясната ръка
        capsule(cv, (hd[0] + 1, hd[1]), (hd[0] + 2, 59), 0.9, 0.9, M('#a07850', '#7e5a38', '#5e4026', '#3e2816'), z + 0.4)


def шапка(cv, х, hc, back):
    вид = х.get("шапка")
    if вид == "калпак":
        capsule(cv, (hc[0], hc[1] - 6), (hc[0], hc[1] - 10), 6.6, 6.0, M('#3a3434', '#262222', '#181414', '#0c0a0a'), 7)
    elif вид == "каскет":
        ellipse(cv, hc[0], hc[1] - 5.5, 7.2, 4.4, х["шапка_цвят"], 7)
        if not back:
            ellipse(cv, hc[0], hc[1] - 2.5, 5.0, 1.4, х["шапка_цвят"], 7.1, extra=-0.4)
    elif вид in ("периферия", "перо"):
        ellipse(cv, hc[0], hc[1] - 3.5, 9.5, 2.4, х["шапка_цвят"], 7)
        capsule(cv, (hc[0], hc[1] - 5), (hc[0], hc[1] - 9), 5.6, 5.0, х["шапка_цвят"], 7.1)
        if вид == "перо":
            for k in range(7):
                cv.plot(int(hc[0] + 5 + k * 0.6), int(hc[1] - 8 - k), RED if k < 4 else YEL, 7.3, 979)


def глава_отпред(cv, х, hc, back=False, усмивка=False):
    кожа, коса = х.get("кожа", SKIN), х["коса"]
    ellipse(cv, hc[0], hc[1], 6.6, 7.2, кожа, 6)
    if х.get("забрадка"):
        ellipse(cv, hc[0], hc[1] - 1.5, 7.6, 7.0, х["забрадка"], 6.6,
                mask=(lambda x, y: y < hc[1] + 6) if back else (lambda x, y: (y < hc[1] - 3.5) or ((x < hc[0] - 5 or x > hc[0] + 4.5) and y < hc[1] + 5)))
        if back:
            poly(cv, [(hc[0] - 4, hc[1] + 3), (hc[0] + 4, hc[1] + 3), (hc[0], hc[1] + 10)], х["забрадка"], 6.7)
    else:
        дълга = х.get("жена")
        ellipse(cv, hc[0], hc[1] - 1.5, 7.0, 6.6, коса, 6.5,
                mask=(lambda x, y: y < hc[1] + (6 if дълга else 4)) if back else (lambda x, y: (y < hc[1] - 3.0) or ((x < hc[0] - 5.5 or x > hc[0] + 5) and y < hc[1] + 0.5)))
    if not х.get("забрадка"):
        кичури(cv, hc, коса)
    шапка(cv, х, hc, back)
    if back:
        return
    сянка_брадичка(cv, hc, х.get("дреха") or х["риза"])
    ey = int(hc[1] + 0.5)
    for ex in (29, 34):
        cv.plot(ex, ey, EYE, 9, 997)
        cv.plot(ex + 1, ey, EYE if усмивка else hx('#fbf4e2'), 9, 997)
        cv.plot(ex, ey - 2, коса[2], 9, 993); cv.plot(ex + 1, ey - 2, коса[2], 9, 993)
    cv.plot(31, ey + 1, кожа[2], 9, 996); cv.plot(32, ey + 2, кожа[2], 9, 996)
    сянка_лице(cv, hc, кожа, ey)
    if х.get("брада"):
        ellipse(cv, hc[0], hc[1] + 5, 5.4, 3.4, коса, 6.8, mask=lambda x, y: y > hc[1] + 3)
    if х.get("мустаци"):
        for x in range(29, 35): cv.plot(x, ey + 3, коса[2] if not х.get("стар") else коса[1], 9, 995)
        cv.plot(28, ey + 4, коса[2] if not х.get("стар") else коса[1], 9, 995); cv.plot(35, ey + 4, коса[2] if not х.get("стар") else коса[1], 9, 995)
    if not х.get("брада"):
        if усмивка:
            for x in (30, 31, 32, 33): cv.plot(x, ey + 5, MOUTH, 9, 994)
        else:
            cv.plot(31, ey + 5, MOUTH, 9, 994); cv.plot(32, ey + 5, MOUTH, 9, 994)
    if х.get("бузи"):
        cv.plot(28, ey + 2, BLUSH, 9, 993); cv.plot(36, ey + 2, BLUSH, 9, 993)
    if х.get("стар"):
        cv.plot(28, ey - 1, кожа[2], 9, 992); cv.plot(36, ey - 1, кожа[2], 9, 992)   # бръчки


def торс(cv, х, by, back, side=False):
    ш = _ширина(х)
    cx = 31 if side else 32
    рш = (6.2 if side else 7.4) * ш
    capsule(cv, (cx, 27 + by), (cx, 37 + by), рш, рш - 0.4, х["риза"], 5)
    if х.get("жена"):
        poly(cv, [(cx - 7 * ш, 36 + by), (cx + 7 * ш, 36 + by), (cx + 10, 55), (cx - 10, 55)], х["рокля"], 4)
    if х.get("дреха"):                                      # дълга дреха над коленете
        if back or side:
            poly(cv, [(cx - рш - 0.5, 24 + by), (cx + рш + 0.5, 24 + by), (cx + рш + 2, 47 + by), (cx - рш - 2, 47 + by)], х["дреха"], 5.5)
        else:
            poly(cv, [(cx - рш - 0.5, 24 + by), (cx - 1.5, 24 + by), (cx - 2, 47 + by), (cx - рш - 2, 47 + by)], х["дреха"], 5.5, extra=0.05)
            poly(cv, [(cx + 1.5, 24 + by), (cx + рш + 0.5, 24 + by), (cx + рш + 2, 47 + by), (cx + 2, 47 + by)], х["дреха"], 5.5, extra=-0.05)
    elif х.get("елек"):
        if back or side:
            poly(cv, [(cx - рш, 24 + by), (cx + рш, 24 + by), (cx + рш, 39 + by), (cx - рш, 39 + by)], х["елек"], 5.5)
        else:
            poly(cv, [(cx - рш, 24 + by), (cx - 1.8, 24 + by), (cx - 1.5, 39 + by), (cx - рш, 39 + by)], х["елек"], 5.5, extra=0.05)
            poly(cv, [(cx + 1.8, 24 + by), (cx + рш, 24 + by), (cx + рш, 39 + by), (cx + 1.5, 39 + by)], х["елек"], 5.5, extra=-0.05)
    if х.get("пояс") and not х.get("жена"):
        poly(cv, [(cx - рш - 0.5, 38 + by), (cx + рш + 0.5, 38 + by), (cx + рш + 0.5, 43 + by), (cx - рш - 0.5, 43 + by)], х["пояс"], 6)
    if х.get("престилка") and not back:
        if side:
            poly(cv, [(cx + 2, 38 + by), (cx + рш + 1, 38 + by), (cx + рш + 2.5, 53), (cx + 3, 53)], х["престилка"], 6.5)
        else:
            poly(cv, [(cx - 6, 30 + by if х.get("жена") else 39 + by), (cx + 6, 30 + by if х.get("жена") else 39 + by),
                      (cx + 7.5, 53), (cx - 7.5, 53)], х["престилка"], 6.5)
            if х.get("жена"):
                for x in range(int(cx - 6), int(cx + 7)):
                    cv.plot(x, int(30 + by), RED if x % 2 else GREEN, 9, 980)
    if х.get("торба"):
        if back:
            capsule(cv, (cx, 28 + by), (cx, 38 + by), 5.5, 5.5, M('#b08a5a', '#8a6a40', '#6a4c2a', '#46301a'), 6.2)
        elif not side:
            for k in range(14):
                cv.plot(int(cx - 6 + k * 0.85), int(24 + by + k * 1.1), M('#b08a5a', '#8a6a40', '#6a4c2a', '#46301a')[2], 9, 981)


def крака(cv, х, by, лифт, навън=(0, 0)):
    if х.get("жена"):                                     # под роклята се виждат само глезените
        for k, x in enumerate((29, 35)):
            ay = 58.5 - лифт[k] * 0.6
            capsule(cv, (x + навън[k], 53), (x + навън[k], ay - 1), 2.0, 1.8, M('#f6f0e6', '#e2dace', '#c4bcae', '#968e80'), 2)
            ellipse(cv, x + навън[k], ay + 1.0, 2.6, 1.7, х["обувки"], 2.2)
        return
    ellipse(cv, 32, 45.5 + by, 7.4 * _ширина(х), 3.4, х["крачоли"], 2.4)
    for k, x in enumerate((29, 35)):
        ay = 58.5 - лифт[k]; nx = x + навън[k]
        capsule(cv, (x, 44 + by), (nx, ay - 1), 3.2, 2.5, х["крачоли"], 2, extra=(-0.12 if k else 0))
        гънка(cv, ((x + nx) / 2, (44 + by + ay) / 2), х["крачоли"], 2)
        ellipse(cv, nx + (-0.3 if k == 0 else 0.3), ay + 1.1, 2.8, 1.8, х["обувки"], 2.2)


def front(х, i, back=False):
    t = 2 * math.pi * i / 8
    cv = Canvas()
    by = round(0.5 * (1 + math.cos(2 * t))) + (1 if х.get("стар") else 0)
    крака(cv, х, by, [max(0, math.sin(t)) * 2.5, max(0, math.sin(t + math.pi)) * 2.5])
    торс(cv, х, by, back)
    ш = _ширина(х)
    for s in (-1, 1):
        sway = 1.3 * math.sin(t + (0 if s > 0 else math.pi))
        if х.get("бастун") and s > 0:
            sway = 0
        sh = (32 + s * 7.6 * ш, 27 + by); el = (32 + s * 9.4 * ш, 33 + by); hd = (32 + s * 9.6 * ш, 39.5 + by + sway)
        ръка(cv, х, sh, el, hd, 6.5, шевици=not back)
    глава_отпред(cv, х, (32, 15.5 + by + (1 if х.get("стар") else 0)), back)
    return finish(cv, OUT)


def dance(х, i):
    t = 2 * math.pi * i / 8
    cv = Canvas()
    вдигане = [0, 3, 6, 3, 0, 0, 0, 0] if not х.get("стар") else [0, 1, 2, 1, 0, 0, 0, 0]
    by = [1, 0, 0, 0, 1, 0, 0, 0][i]
    л = [вдигане[i], вдигане[(i + 4) % 8]]
    крака(cv, х, by, л, навън=(-л[0] * 0.35, л[1] * 0.35))
    торс(cv, х, by, False)
    стар = dict(х, бастун=False)
    for s in (-1, 1):
        вълна = 0.8 * math.sin(t + (0 if s > 0 else math.pi))
        sh = (32 + s * 7.6, 27 + by); el = (32 + s * 12, 29.5 + by); hd = (32 + s * 16.5, 30.5 + by + вълна)
        ръка(cv, стар, sh, el, hd, 6.5)
    глава_отпред(cv, х, (32, 15.5 + by), усмивка=True)
    return finish(cv, OUT)


def side(х, i):
    t = 2 * math.pi * i / 8
    cv = Canvas()
    TH, SH = 9.5, 9.5
    кожа, коса = х.get("кожа", SKIN), х["коса"]
    крачка = 14 if х.get("стар") else 22
    def leg(ph):
        th = крачка * math.sin(ph); knee = max(0, 40 * math.sin(ph - 1.3)); return th, th - knee
    legs = [leg(t + math.pi), leg(t)]
    ank = [TH * math.cos(math.radians(a)) + SH * math.cos(math.radians(b)) for a, b in legs]
    hipY = 59.0 - max(ank); by = hipY - 41.5; hip = (31.5, hipY)
    def arm(sh, z, ex, sgn):
        fa = -18 * math.sin(t) * sgn
        el = rot(sh, fa, 6.5); hd = rot(el, fa + 15, 6.2)
        ръка(cv, dict(х, бастун=False), sh, el, hd, z, ex, шевици=z > 5)
        if х.get("бастун") and z > 5:
            capsule(cv, (hd[0] + 1, hd[1]), (hd[0] + 4, 59), 0.9, 0.9, M('#a07850', '#7e5a38', '#5e4026', '#3e2816'), z + 0.4)
    arm((31, 27 + by), 1, -0.35, 1)
    if х.get("жена"):
        for k, (a, b) in enumerate(legs):
            knee = rot(hip, a * 0.5, TH); ankle = rot(knee, b * 0.4, SH)
            ellipse(cv, ankle[0] + 2, ankle[1] + 1, 3.2, 1.7, х["обувки"], 2 + k)
    else:
        for k, (a, b) in enumerate(legs):
            z = 2 if k == 0 else 3; ex = -0.35 if k == 0 else 0
            knee = rot(hip, a, TH); ankle = rot(knee, b, SH)
            capsule(cv, hip, knee, 3.2, 2.7, х["крачоли"], z, extra=ex)
            capsule(cv, knee, ankle, 2.7, 2.1, х["крачоли"], z, extra=ex)
            ellipse(cv, ankle[0] + 2.2, ankle[1] + 1.0, 3.4, 1.7, х["обувки"], z + 0.2, extra=ex - 0.1)
    торс(cv, х, by, False, side=True)
    hc = (34, 15.5 + by + (1 if х.get("стар") else 0))
    capsule(cv, (32, 23 + by), (33, 21 + by), 2.2, 2.2, кожа, 5.6, extra=0.1)
    ellipse(cv, hc[0], hc[1], 6.4, 7.0, кожа, 6, extra=0.3)
    if х.get("забрадка"):
        ellipse(cv, hc[0] - 1.2, hc[1] - 1.6, 7.2, 6.6, х["забрадка"], 6.5, mask=lambda x, y: (y < hc[1] - 3.0) or (x < hc[0] - 1 and y < hc[1] + 6))
    else:
        ellipse(cv, hc[0] - 1.2, hc[1] - 1.8, 6.8, 6.2, коса, 6.5, mask=lambda x, y: (y < hc[1] - 3.0) or (x < hc[0] - 2 and y < hc[1] + (6 if х.get("жена") else 3)))
    шапка(cv, х, (hc[0] - 1, hc[1]), False)
    ey = int(hc[1] + 0.5); ex = int(hc[0] + 3)
    cv.plot(ex, ey, EYE, 9, 997); cv.plot(ex, ey - 2, коса[2], 9, 993); cv.plot(ex + 1, ey - 2, коса[2], 9, 993)
    cv.plot(int(hc[0] + 6.5), ey + 1, кожа[2], 9, 996)
    if х.get("брада"):
        ellipse(cv, hc[0] + 2, hc[1] + 5, 4.0, 3.0, коса, 6.8, mask=lambda x, y: y > hc[1] + 3)
    if х.get("мустаци"):
        for x in range(ex, ex + 3): cv.plot(x, ey + 3, коса[1] if х.get("стар") else коса[2], 9, 995)
    if not х.get("брада"):
        cv.plot(ex + 1, ey + 5, MOUTH, 9, 994)
    arm((32, 27 + by), 7, 0, -1)
    return finish(cv, OUT)
