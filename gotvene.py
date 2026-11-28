# Мини игри при готвенето (решение от 28.11.2026). Когато ученик приготвя нещо с E,
# вместо да чака лентата, играе кратка игра. Колкото по-добре, толкова по-хубаво е ястието
# и толкова по-голям бакшиш дава гостът. NPC готвят без игра.
#   ракия  - Наливане: задръж S и пусни точно на чертата (не прелей!)
#   вино   - Канелка: S, когато стрелката е в зеленото (3 пъти)
#   шопска - Рязане: натисни буквата (A S D), когато кръгът стигне ножа (8 реза)
#   боб    - Бъркане: S = дърва в огъня (температурата в зеленото), A и D редом = бъркаш
# Платно 960x540, като минииграта с кавала. Esc = отказ (нищо не се приготвя).
import json
import math
import os
import random
import time

import pygame

import tiles

ШИР, ВИС = 960, 540
ЗЛАТНО, СВЕТЛО, БЯЛО = (255, 230, 150), (230, 220, 200), (255, 252, 240)
УМОРА = 0.0                     # 0-1: колко е уморен готвачът (играта го слага преди мини играта)
КЛАВИШИ_РЯЗАНЕ = (pygame.K_a, pygame.K_s, pygame.K_d)       # всички мини игри: A S D
ИМЕНА_РЯЗАНЕ = ("A", "S", "D")
ДЕЙСТВИЕ = (pygame.K_s, pygame.K_SPACE)                       # едно копче: S (и интервалът)


# Пиксел-арт (tools/pixelart/make_gotvene_art.py): сцена 320x180, уголемена x3.
ПИКСЕЛ = 3
ЛИСТОВЕ = {"kuhnya_fon": (320, 180), "rakia_chasha": (44, 60), "rakia_shishe": (80, 80), "vino_bachva": (128, 112),
           "vino_kancha": (44, 46), "shopska_daska": (150, 44), "shopska_zelenchuci": (32, 32), "shopska_noj": (64, 56),
           "shopska_kupa": (84, 50), "bob_ognishte": (168, 52), "bob_ogan": (72, 48), "bob_garne": (120, 92),
           "bob_lazhica": (120, 92), "bob_para": (72, 52),
           "hlyab_samun": (160, 110), "hlyab_filiyka": (36, 36), "hlyab_chiniya": (90, 40),
           "tendzhera": (120, 92), "tigan": (150, 50)}
_АРТ = {}


def зареди_арт():
    """{име: [кадри]} от assets/minigames. None, ако нещо липсва (тогава рисуваме с прости форми)."""
    if not _АРТ:
        for име, (ш, в) in ЛИСТОВЕ.items():
            път = tiles.намери_картинка(os.path.join("minigames", име + ".png"))
            if not път:
                return None
            лист = pygame.image.load(път)
            if pygame.display.get_surface():
                лист = лист.convert_alpha()
            _АРТ[име] = [лист.subsurface((к * ш, 0, ш, в)) for к in range(лист.get_width() // ш)]
        път = tiles.намери_картинка(os.path.join("minigames", "rakia_shishe.json"))
        _АРТ["гърла"] = json.load(open(път, encoding="utf-8"))["гърло"] if път else [(36, 10)] * 6
        път = tiles.намери_картинка(os.path.join("minigames", "bob_kazan.png"))   # казанът от снимката (Codixel)
        if път:
            лист = pygame.image.load(път)
            лист = лист.convert_alpha() if pygame.display.get_surface() else лист
            _АРТ["bob_kazan"] = [лист.subsurface((к * 120, 0, 120, 92)) for к in range(лист.get_width() // 120)]
        път = tiles.намери_картинка(os.path.join("minigames", "lyut_kazan.png"))  # котелът от Pixel Art Village
        if път:
            лист = pygame.image.load(път)
            лист = лист.convert_alpha() if pygame.display.get_surface() else лист
            _АРТ["lyut_kazan"] = [лист.subsurface((к * 128, 0, 128, 128)) for к in range(лист.get_width() // 128)]
        път = tiles.намери_картинка(os.path.join("minigames", "sadove.json"))
        _АРТ["съдове"] = json.load(open(път, encoding="utf-8")) if път else {
            "tendzhera": {"x": 60, "y": 27, "rx": 42, "ry": 9}, "tigan": {"x": 58, "y": 24, "rx": 46, "ry": 11}}
        път = tiles.намери_картинка(os.path.join("minigames", "hlyab.json"))
        _АРТ["хляб"] = json.load(open(път, encoding="utf-8")) if път else {"ос": (0.89, -0.45), "начало": (34, 70), "филийка": 9}
    return _АРТ


_ЕФЕКТИ = {}


def ефект(име):
    """Лента с кадри от PixelFX (assets/fx/<име>.png + .json): (кадри, fps, pivot). None, ако я няма."""
    if име not in _ЕФЕКТИ:
        път = tiles.намери_картинка(os.path.join("fx", име + ".png"))
        _ЕФЕКТИ[име] = None
        if път and os.path.exists(път[:-4] + ".json"):
            мета = json.load(open(път[:-4] + ".json", encoding="utf-8"))["meta"]["pixelfx"]
            лист = pygame.image.load(път)
            if pygame.display.get_surface():
                лист = лист.convert_alpha()
            ш, в = мета["frameSize"]
            кадри = [лист.subsurface(((к % мета["columns"]) * ш, (к // мета["columns"]) * в, ш, в))
                     for к in range(мета["frames"])]
            _ЕФЕКТИ[име] = (кадри, мета["fps"], мета["pivot"])
    return _ЕФЕКТИ[име]


def рисувай_ефект(п, име, x, y, време, прозрачност=255):
    """Рисува кадъра за 'време' (секунди) така, че pivot-ът на ефекта да е в (x, y)."""
    е = ефект(име)
    if not е:
        return False
    кадри, fps, pivot = е
    к = кадри[int(време * fps) % len(кадри)]
    if прозрачност < 255:
        к = к.copy()
        к.set_alpha(прозрачност)
    п.blit(к, (int(x - pivot[0]), int(y - pivot[1])))
    return True


def оценка(качество):
    if качество >= 0.85:
        return "Отлично!", 3
    if качество >= 0.55:
        return "Добре", 2
    if качество > 0.2:
        return "Става", 1
    return "Не стана", 0


class Стъпка:
    """Една стъпка от рецептата = една мини игра. Играта я вика: клавиш(събитие), обнови(), нарисувай(екран).
    Когато край е True: резултат = {"item", "quality"} или None (отказ)."""

    def __init__(self, предмет, име="", изглед=None, вид=None, настройки=None, заглавие=None, съдържание=None):
        self.предмет, self.име = предмет, име or предмет
        # какво има в тенджерата и тигана: пази се от стъпка на стъпка (вижда се, че бобът е в тенджерата)
        self.съдържание = съдържание if съдържание is not None else {"тенджера": [], "тиган": [], "печено": 0.0}
        self.изглед = изглед
        self.настр = настройки or {}
        self.вид = вид or {"rakia": "наливане", "vino": "канелка", "shopska": "рязане", "bob": "бъркане",
                    "hlyab": "хляб", "lyutenitsa": "лютеница"}.get(предмет, "канелка")
        self.етап = "обяснение"                     # обяснение -> игра -> резултат
        self.край = False
        self.резултат = None
        self.качество = 0.0
        self.ш = {}
        self.сл = random.Random()
        self.преди = time.perf_counter()
        self.от = self.преди                        # кога е започнал текущият етап
        self.икона = None
        self.арт = зареди_арт()
        self.пиксели = pygame.Surface((ШИР // ПИКСЕЛ, ВИС // ПИКСЕЛ))
        self.кадър_време = 0.0                       # за анимациите (огън, мехурчета)
        път = tiles.намери_картинка(os.path.join("items", предмет + ".png"))
        if път:
            self.икона = pygame.transform.scale(pygame.image.load(път), (128, 128))
        self.умора = УМОРА
        self.по_бавно = 1 + 0.6 * self.умора                # уморен: бъркането спада по-бързо
        getattr(self, "_начало_" + self.вид)()
        if заглавие:
            self.обяснение[0] = заглавие
        if self.умора > 0.2:
            self.обяснение = self.обяснение + ["Уморен си - ще е по-трудно! Почини си (F = седни)."]

    # ---------- общо ----------
    def шрифт(self, размер, удебелен=False):
        if (размер, удебелен) not in self.ш:
            self.ш[(размер, удебелен)] = pygame.font.SysFont("arial", размер, bold=удебелен)
        return self.ш[(размер, удебелен)]

    def _текст(self, екран, текст, размер, цвят, център, удебелен=False):
        п = self.шрифт(размер, удебелен).render(текст, True, цвят)
        с = self.шрифт(размер, удебелен).render(текст, True, (20, 12, 8))
        r = п.get_rect(center=център)
        екран.blit(с, r.move(2, 2))
        екран.blit(п, r)

    def време(self):
        return time.perf_counter() - self.от

    def _готово(self, качество):
        self.качество = max(0.0, min(1.0, качество))
        self.етап, self.от = "резултат", time.perf_counter()

    def клавиш(self, с):
        if с.type == pygame.KEYDOWN and с.key == pygame.K_ESCAPE:
            self.край, self.резултат = True, None
            return
        if self.етап == "обяснение":
            if с.type == pygame.KEYDOWN and с.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e, pygame.K_s):
                self.етап, self.от = "игра", time.perf_counter()
            return
        if self.етап == "игра":
            getattr(self, "_клавиш_" + self.вид)(с)

    def обнови(self):
        сега = time.perf_counter()
        dt, self.преди = min(0.1, сега - self.преди), сега
        self.кадър_време += dt
        if self.етап == "игра":
            getattr(self, "_обнови_" + self.вид)(dt)
        elif self.етап == "резултат" and self.време() > 1.8:
            self.край = True
            self.резултат = {"item": self.предмет, "quality": round(self.качество, 2)}

    def нарисувай(self, екран):
        if self.арт:                                         # пиксел-арт: рисуваме 320x180 и уголемяваме x3
            п = self.пиксели
            п.blit(self.арт["kuhnya_fon"][0], (0, 0))
            getattr(self, "_пиксели_" + self.вид)(п)
            pygame.transform.scale(п, (ШИР, ВИС), екран)
            табела = self.шрифт(34, True).size(self.име)
            r = pygame.Rect(0, 0, табела[0] + 40, табела[1] + 14)
            r.center = (ШИР // 2, 40)
            pygame.draw.rect(екран, (62, 38, 22), r, border_radius=8)          # дървена табела
            pygame.draw.rect(екран, (170, 116, 64), r, 3, border_radius=8)
            self._текст(екран, self.име, 34, ЗЛАТНО, (ШИР // 2, 40), True)
            getattr(self, "_надписи_" + self.вид)(екран)
            self._отгоре(екран)
            return
        for y in range(0, ВИС, 4):                               # топла кухня
            к = y / ВИС
            pygame.draw.rect(екран, (int(58 + 30 * к), int(38 + 18 * к), int(28 + 8 * к)), (0, y, ШИР, 4))
        for x in range(0, ШИР, 120):
            pygame.draw.rect(екран, (40, 26, 18), (x, 0, 12, ВИС))
        pygame.draw.rect(екран, (110, 70, 40), (0, 430, ШИР, 110))   # плотът на масата
        pygame.draw.rect(екран, (80, 50, 28), (0, 430, ШИР, 8))
        self._текст(екран, self.име, 34, ЗЛАТНО, (ШИР // 2, 40), True)
        getattr(self, "_рисувай_" + self.вид)(екран)
        self._отгоре(екран)

    def _отгоре(self, екран):
        if self.етап == "обяснение":
            рамка = pygame.Surface((720, 170), pygame.SRCALPHA)
            рамка.fill((20, 12, 8, 215))
            екран.blit(рамка, (120, 180))
            for и, ред in enumerate(self.обяснение):
                self._текст(екран, ред, 24 if и == 0 else 20, ЗЛАТНО if и == 0 else СВЕТЛО, (ШИР // 2, 215 + и * 36), и == 0)
            self._текст(екран, "S = почни     Esc = отказ", 18, (200, 190, 170), (ШИР // 2, 330))
        elif self.етап == "резултат":
            текст, звезди = оценка(self.качество)
            рамка = pygame.Surface((420, 150), pygame.SRCALPHA)
            рамка.fill((20, 12, 8, 220))
            екран.blit(рамка, (270, 190))
            self._текст(екран, текст, 40, ЗЛАТНО, (ШИР // 2, 230), True)
            self._текст(екран, "★" * звезди + "☆" * (3 - звезди), 44, (255, 210, 60), (ШИР // 2, 295), True)

    # ---------- пиксел-арт за всяка игра ----------
    def _кадър(self, име, к):
        кадри = self.арт[име]
        return кадри[max(0, min(len(кадри) - 1, int(к)))]

    def _лента(self, п, x, y, ш, в, стойност, зона, цвят):
        """Вертикална лента с дървена рамка и зелена зона (в пиксели)."""
        pygame.draw.rect(п, (62, 38, 22), (x - 3, y - 3, ш + 6, в + 6))
        pygame.draw.rect(п, (140, 92, 52), (x - 2, y - 2, ш + 4, в + 4), 1)
        pygame.draw.rect(п, (36, 24, 18), (x, y, ш, в))
        pygame.draw.rect(п, (70, 160, 76), (x, y + int(в * (1 - зона[1])), ш, int(в * (зона[1] - зона[0]))))
        h = int(в * стойност)
        pygame.draw.rect(п, цвят, (x + 2, y + в - h, ш - 4, h))
        pygame.draw.line(п, (255, 255, 255), (x + 2, y + в - h), (x + ш - 3, y + в - h))

    def _пиксели_наливане(self, п):
        к = self.ниво * 46
        чаша = self._кадър("rakia_chasha", 47 if self.ниво > 1 else round(к))
        п.blit(чаша, (138, 82))
        yч = 82 + 52 - round(self.черта * 46) + 1                 # чертата
        pygame.draw.line(п, (230, 50, 40), (128, yч), (192, yч))
        pygame.draw.line(п, (255, 120, 100), (128, yч - 1), (132, yч - 1))
        налива = self.налива or self.докапва > 0
        цел = 5 if налива else 0
        self.наклон = getattr(self, "наклон", 0.0)
        self.наклон += (цел - self.наклон) * 0.35
        к_ш = round(self.наклон)
        гърло5 = self.арт["гърла"][5]
        ox, oy = 168 - гърло5[0], 66 - гърло5[1]                  # гърлото на наклоненото шише е над чашата
        п.blit(self._кадър("rakia_shishe", к_ш), (ox, oy))
        if налива and к_ш >= 4:
            гx, гy = self.арт["гърла"][к_ш]
            гx, гy = ox + гx, oy + гy
            повърхност_y = 82 + 52 - round(к) + 1
            for y in range(int(гy), повърхност_y):
                x = int(гx + (166 - гx) * (y - гy) / max(1, повърхност_y - гy)) + (1 if (y + int(self.кадър_време * 20)) % 5 == 0 else 0)
                п.set_at((x, y), (248, 222, 122)); п.set_at((x + 1, y), (230, 188, 74))

    def _надписи_наливане(self, екран):
        yч = (82 + 52 - round(self.черта * 46) + 1) * ПИКСЕЛ
        self._текст(екран, "черта", 18, (255, 160, 140), (620, yч))

    def _пиксели_канелка(self, п):
        отворена = self.пауза > 0 and self.кръг > 0
        п.blit(self._кадър("vino_bachva", 1 if отворена else 0), (40, 10))
        self.пълно = getattr(self, "пълно", 0.0)
        self.пълно += (len(self.точки) / 3.0 - self.пълно) * 0.12
        if отворена:
            for y in range(104, 112):
                п.set_at((104, y), (162, 34, 58)); п.set_at((105, y), (116, 18, 40))
        п.blit(self._кадър("vino_kancha", round(self.пълно * 22)), (82, 102))
        x0, y0, ш = 170, 62, 130                                  # лентата със стрелката
        pygame.draw.rect(п, (62, 38, 22), (x0 - 4, y0 - 4, ш + 8, 20))
        pygame.draw.rect(п, (140, 92, 52), (x0 - 3, y0 - 3, ш + 6, 18), 1)
        pygame.draw.rect(п, (96, 60, 40), (x0, y0, ш, 12))
        if self.кръг < 3:
            pygame.draw.rect(п, (80, 180, 86), (x0 + int(ш * self.зона[0]), y0, max(2, int(ш * self.зона[1])), 12))
            pygame.draw.line(п, (150, 230, 150), (x0 + int(ш * self.зона[0]), y0), (x0 + int(ш * (self.зона[0] + self.зона[1])), y0))
        sx = x0 + int(ш * (0.5 + 0.5 * math.sin(self.фаза)))
        pygame.draw.polygon(п, (255, 250, 236), [(sx - 4, y0 - 9), (sx + 4, y0 - 9), (sx, y0 - 3)])
        pygame.draw.polygon(п, (40, 24, 16), [(sx - 4, y0 - 9), (sx + 4, y0 - 9), (sx, y0 - 3)], 1)
        pygame.draw.line(п, (255, 250, 236), (sx, y0 - 3), (sx, y0 + 12))
        for и in range(3):
            if и < len(self.точки):
                цвят = (255, 206, 60) if self.точки[и] > 0.6 else (200, 120, 80)
            else:
                цвят = (110, 86, 66)
            pygame.draw.circle(п, (40, 24, 16), (x0 + ш // 2 - 18 + и * 18, y0 + 26), 6)
            pygame.draw.circle(п, цвят, (x0 + ш // 2 - 18 + и * 18, y0 + 26), 5)

    def _надписи_канелка(self, екран):
        if self.етап == "игра" and self.кръг < 3:
            self._текст(екран, "Проба %d от 3" % (self.кръг + 1), 22, СВЕТЛО, (705, 300))

    def _пиксели_рязане(self, п):
        п.blit(self.арт["shopska_daska"][0], (30, 100))
        център = (105, 118)
        сега = self.време()
        if self.следващ < len(self.удари):
            t, буква = self.удари[self.следващ]
            п.blit(self._кадър("shopska_zelenchuci", self.зел_ред[self.следващ] * 3), (център[0] - 16, център[1] - 16))
            остава = t - сега
            if остава > -0.4 and self.етап == "игра":
                pygame.draw.circle(п, (255, 250, 236), център, int(13 + max(0.0, остава) * 36), 1)
            pygame.draw.circle(п, (255, 214, 90), център, 13, 1)
        if self.следващ:                                          # току-що нарязаното
            преди = self.удари[self.следващ - 1][0]
            if сега - преди < 0.35 and self.точки and self.точки[-1] > 0:
                етап = 1 if сега - преди < 0.15 else 2
                п.blit(self._кадър("shopska_zelenchuci", self.зел_ред[self.следващ - 1] * 3 + етап), (център[0] - 16, център[1] - 16))
        удар = self.следващ and сега - self.удари[self.следващ - 1][0] < 0.18
        к_нож = (3 if сега - self.удари[self.следващ - 1][0] < 0.08 else 2) if удар else 0
        п.blit(self._кадър("shopska_noj", к_нож), (център[0] - 8, център[1] - 50))
        нарязани = sum(1 for т in self.точки if т > 0)
        п.blit(self._кадър("shopska_kupa", min(8, нарязани * 8 // max(1, len(self.удари)))), (214, 100))
        for и, т in enumerate(self.точки):
            цвят = (255, 206, 60) if т >= 0.6 else (200, 120, 80) if т else (90, 60, 40)
            pygame.draw.circle(п, (40, 24, 16), (60 + и * 12, 160), 4)
            pygame.draw.circle(п, цвят, (60 + и * 12, 160), 3)

    def _надписи_рязане(self, екран):
        if self.етап == "игра" and self.следващ < len(self.удари):
            буква = self.удари[self.следващ][1]
            r = pygame.Rect(0, 0, 64, 64)
            r.center = (105 * ПИКСЕЛ, 50 * ПИКСЕЛ + 30)
            pygame.draw.rect(екран, (60, 40, 28), r.move(0, 6), border_radius=10)     # клавиш
            pygame.draw.rect(екран, (250, 236, 200), r, border_radius=10)
            pygame.draw.rect(екран, (60, 40, 28), r, 3, border_radius=10)
            self._текст(екран, ИМЕНА_РЯЗАНЕ[буква], 40, (80, 40, 20), r.center, True)

    def _пиксели_бъркане(self, п):
        п.blit(self.арт["bob_ognishte"][0], (76, 126))
        размер = 0 if self.темп < 0.35 else 1 if self.темп < 0.65 else 2
        # огънят е от PixelFX (fire/campfire в 3 размера); ако го няма - нашият, по-простият
        if not рисувай_ефект(п, ("ogan_malak", "ogan_sreden", "ogan_golyam")[размер], 160, 146, self.кадър_време):
            к = int(self.кадър_време * 9) % 6
            п.blit(self._кадър("bob_ogan", размер * 6 + к), (124, 96))
        мехури = int(self.кадър_време * (4 + 8 * self.темп)) % 4 if self.темп > 0.3 else 0
        лъжица = self._кадър("bob_lazhica", int(self.ъгъл / (2 * math.pi) * 8) % 8)
        if self.настр.get("съд") == "тенджера" and "tendzhera" in self.арт:
            п.blit(self.арт["tendzhera"][0], (100, 46))
            self._в_съда(п, "тенджера", 100, 46, топлина=self.темп)
            п.blit(лъжица, (100, 46))
        elif "bob_kazan" in self.арт:                          # чугунен казан на крачета (от снимката на учителя)
            п.blit(self.арт["bob_kazan"][мехури], (100, 46))
            п.blit(лъжица, (101, 40))
        else:
            п.blit(self._кадър("bob_garne", мехури), (100, 28))
            п.blit(лъжица, (100, 28))
        if self.темп > 0.3:
            сила = int(90 + 165 * min(1.0, (self.темп - 0.3) / 0.45))      # колкото по-горещо, толкова повече пара
            if not рисувай_ефект(п, "para", 160, 65 if "bob_kazan" in self.арт else 52, self.кадър_време, сила):
                пара = self._кадър("bob_para", int(self.кадър_време * 6) % 4).copy()
                пара.set_alpha(сила)
                п.blit(пара, (124, 2))
        self._лента(п, 34, 34, 14, 96, self.темп, (0.45, 0.72), (240, 120, 40))
        self._лента(п, 272, 34, 14, 96, self.бъркане, (0.35, 1.0), (236, 226, 204))

    def _надписи_бъркане(self, екран):
        self._текст(екран, "огън", 20, СВЕТЛО, (41 * ПИКСЕЛ, 140 * ПИКСЕЛ))
        self._текст(екран, "S", 26, ЗЛАТНО, (41 * ПИКСЕЛ, 22 * ПИКСЕЛ), True)
        self._текст(екран, "бъркане", 20, СВЕТЛО, (279 * ПИКСЕЛ, 140 * ПИКСЕЛ))
        self._текст(екран, "A  D", 26, ЗЛАТНО, (279 * ПИКСЕЛ, 22 * ПИКСЕЛ), True)
        if self.етап == "игра":
            self._текст(екран, "%d с" % max(0, math.ceil(self.варене - self.общо)), 26, ЗЛАТНО, (ШИР // 2 + 200, 84), True)

    # ---------- хляб: рязане на филийки ----------
    ХЛЯБ_X, ХЛЯБ_Y = 6, 50                                    # къде стои самунът (пиксели)

    def _начало_хляб(self):
        self.обяснение = ["Хляб", "Режи филийки: натисни буквата, когато кръгът стигне ножа.",
                          "A  S  D - 6 филийки. Колкото по-точно, толкова по-равни."]
        self.удари = [(1.4 + и * 1.2, self.сл.randrange(3)) for и in range(6)]
        self.точки, self.следващ, self.резени = [], 0, []
        self.зеленчуци = [((255, 216, 144), 20)] * 4

    def _клавиш_хляб(self, с):
        self._клавиш_рязане(с)

    def _обнови_хляб(self, dt):
        self._обнови_рязане(dt)

    def _рисувай_хляб(self, екран):
        self._рисувай_рязане(екран)

    def _точка_рез(self, к):
        х = self.арт["хляб"]
        return (self.ХЛЯБ_X + х["начало"][0] + х["ос"][0] * х["филийка"] * к,
                self.ХЛЯБ_Y + х["начало"][1] + х["ос"][1] * х["филийка"] * к)

    def _пиксели_хляб(self, п):
        п.blit(self.арт["shopska_daska"][0], (10, 104))
        п.blit(self.арт["hlyab_chiniya"][0], (208, 112))
        сега = self.време()
        отрязани = self.следващ
        п.blit(self._кадър("hlyab_samun", отрязани), (self.ХЛЯБ_X, self.ХЛЯБ_Y))
        for и in range(отрязани):                              # филийките в чинията
            if и == отрязани - 1 and сега - self.удари[и][0] < 0.25:
                # току-що отрязаната: пада от самуна към чинията
                к = max(0.0, (сега - self.удари[и][0]) / 0.25)
                x0, y0 = self._точка_рез(и)
                x = x0 + (238 + и * 6 - x0) * к - 18
                y = y0 + (128 - и * 3 - y0) * к - 18 - math.sin(к * math.pi) * 20
                п.blit(self._кадър("hlyab_filiyka", и % 2), (int(x), int(y)))
            else:
                п.blit(self._кадър("hlyab_filiyka", и % 2), (238 + и * 6 - 18, 128 - и * 3 - 18))
        if self.следващ < len(self.удари):
            t, _ = self.удари[self.следващ]
            център = tuple(int(в) for в in self._точка_рез(self.следващ + 1))
            остава = t - сега
            if остава > -0.4 and self.етап == "игра":
                pygame.draw.circle(п, (255, 250, 236), център, int(10 + max(0.0, остава) * 36), 1)
            pygame.draw.circle(п, (255, 214, 90), център, 10, 1)
            self._място_буква = център
        удар = self.следващ and сега - self.удари[self.следващ - 1][0] < 0.18
        нож_при = self._точка_рез(min(self.следващ, len(self.удари) - 1) + (0 if удар else 1))
        нож = pygame.transform.rotate(self._кадър("shopska_noj", 0), 90)       # ножът е изправен, острието надолу
        надолу = 26 if удар else 0                               # при удар слиза през самуна
        п.blit(нож, (int(нож_при[0]) - нож.get_width() // 2 + 2, int(нож_при[1]) - 66 + надолу))
        for и, т in enumerate(self.точки):
            цвят = (255, 206, 60) if т >= 0.6 else (200, 120, 80) if т else (90, 60, 40)
            pygame.draw.circle(п, (40, 24, 16), (60 + и * 12, 166), 4)
            pygame.draw.circle(п, цвят, (60 + и * 12, 166), 3)

    def _надписи_хляб(self, екран):
        if self.етап == "игра" and self.следващ < len(self.удари):
            буква = self.удари[self.следващ][1]
            x, y = getattr(self, "_място_буква", (100, 80))
            r = pygame.Rect(0, 0, 60, 60)
            r.center = (x * ПИКСЕЛ + 120, y * ПИКСЕЛ - 150)
            pygame.draw.rect(екран, (60, 40, 28), r.move(0, 6), border_radius=10)
            pygame.draw.rect(екран, (250, 236, 200), r, border_radius=10)
            pygame.draw.rect(екран, (60, 40, 28), r, 3, border_radius=10)
            self._текст(екран, ИМЕНА_РЯЗАНЕ[буква], 38, (80, 40, 20), r.center, True)

    # ---------- ракия: наливане ----------
    def _начало_наливане(self):
        self.обяснение = ["Наливане на ракия", "Задръж S, за да наливаш.",
                          "Пусни точно на чертата - и внимавай да не прелееш!"]
        self.ниво, self.черта, self.налива, self.докапва, self.почнал = 0.0, self.сл.uniform(0.55, 0.85), False, 0.0, False

    def _клавиш_наливане(self, с):
        if с.key not in ДЕЙСТВИЕ:
            return
        if с.type == pygame.KEYDOWN:
            self.налива = self.почнал = True
        elif с.type == pygame.KEYUP and self.налива:
            self.налива, self.докапва = False, 0.15         # още малко докапва

    def _обнови_наливане(self, dt):
        if self.налива or self.докапва > 0:
            self.ниво += 0.24 * dt
            if not self.налива:
                self.докапва -= dt
                if self.докапва <= 0:
                    self._готово(0 if self.ниво > 1 else 1 - abs(self.ниво - self.черта) / 0.2)
        if self.ниво > 1.0:
            self.ниво = 1.02
            self._готово(0)                                  # преля
        if self.време() > 12 and not self.почнал:
            self._готово(0)

    def _рисувай_наливане(self, екран):
        x0, x1, y0, y1 = 380, 580, 160, 430                   # чашата: широка горе, тясна долу
        вътре = [(x0 + 8, y0), (x1 - 8, y0), (x1 - 28, y1 - 10), (x0 + 28, y1 - 10)]
        h = (y1 - 10 - y0) * min(1.0, self.ниво)
        if h > 0:
            yt = y1 - 10 - h
            ш = lambda y: 8 + 20 * (y - y0) / (y1 - 10 - y0)
            pygame.draw.polygon(екран, (240, 200, 90), [(x0 + ш(yt), yt), (x1 - ш(yt), yt), (x1 - 28, y1 - 10), (x0 + 28, y1 - 10)])
            pygame.draw.line(екран, (255, 236, 160), (x0 + ш(yt), yt), (x1 - ш(yt), yt), 3)
        pygame.draw.polygon(екран, (220, 240, 250), [(x0, y0), (x1, y0), (x1 - 20, y1), (x0 + 20, y1)], 6)
        pygame.draw.line(екран, (255, 255, 255), (x0 + 14, y0 + 20), (x0 + 30, y1 - 30), 4)
        yч = y1 - 10 - (y1 - 10 - y0) * self.черта                  # чертата
        pygame.draw.line(екран, (230, 60, 50), (x0 - 30, yч), (x1 + 30, yч), 4)
        self._текст(екран, "черта", 18, (255, 160, 140), (x1 + 70, yч))
        # шишето над чашата: наклонено, докато налива
        ъгъл = 110 if (self.налива or self.докапва > 0) else 160
        шише = pygame.Surface((70, 180), pygame.SRCALPHA)
        pygame.draw.rect(шише, (220, 240, 250), (5, 50, 60, 125), border_radius=16)
        pygame.draw.rect(шише, (240, 200, 90), (11, 90, 48, 80), border_radius=10)
        pygame.draw.rect(шише, (220, 240, 250), (24, 5, 22, 55), border_radius=6)
        pygame.draw.rect(шише, (150, 90, 50), (22, 0, 26, 12), border_radius=4)
        з = pygame.transform.rotate(шише, ъгъл)
        екран.blit(з, з.get_rect(center=(560, 120)))
        if self.налива or self.докапва > 0:
            pygame.draw.line(екран, (240, 200, 90), (505, 150), (480, y1 - 10 - h), 5)

    # ---------- вино: канелка ----------
    def _начало_канелка(self):
        self.обяснение = ["Вино от бъчвата", "Натисни S, когато стрелката е в зеленото.",
                          "Три пъти - зеленото става все по-тясно."]
        self.кръг, self.точки, self.фаза = 0, [], 0.0
        self._нов_кръг()

    def _нов_кръг(self):
        ш = (0.24, 0.17, 0.11)[self.кръг]
        self.зона = (self.сл.uniform(0.1, 0.9 - ш), ш)
        self.скорост = 1.3 + self.кръг * 0.5
        self.пауза = 0.0

    def _клавиш_канелка(self, с):
        if с.type != pygame.KEYDOWN or с.key not in ДЕЙСТВИЕ or self.пауза > 0:
            return
        п = 0.5 + 0.5 * math.sin(self.фаза)
        център = self.зона[0] + self.зона[1] / 2
        self.точки.append(max(0.0, 1 - abs(п - център) / self.зона[1]))
        self.кръг += 1
        self.пауза = 0.6
        if self.кръг < 3:
            self._нов_кръг()
            self.пауза = 0.6

    def _обнови_канелка(self, dt):
        if self.пауза > 0:
            self.пауза -= dt
            if self.пауза <= 0 and self.кръг >= 3:
                self._готово(sum(self.точки) / 3)
            return
        self.фаза += self.скорост * dt * math.pi

    def _рисувай_канелка(self, екран):
        pygame.draw.ellipse(екран, (120, 70, 36), (90, 110, 260, 320))     # бъчвата
        for y in (170, 370):
            pygame.draw.ellipse(екран, (50, 48, 56), (92, y - 12, 256, 24), 6)
        pygame.draw.rect(екран, (220, 180, 60), (330, 300, 50, 16))       # канелката
        pygame.draw.rect(екран, (220, 180, 60), (366, 292, 14, 10))
        if self.пауза > 0:
            pygame.draw.line(екран, (150, 30, 40), (372, 316), (372, 390), 6)
        # каната се пълни
        ниво = len(self.точки) / 3.0
        pygame.draw.rect(екран, (190, 110, 70), (322, 380, 100, 50), border_radius=14)
        if ниво:
            pygame.draw.rect(екран, (140, 20, 40), (330, 422 - int(36 * ниво), 84, int(36 * ниво)), border_radius=8)
        # лентата със стрелката
        x0, ш = 440, 440
        pygame.draw.rect(екран, (40, 26, 18), (x0 - 6, 236, ш + 12, 48), border_radius=8)
        pygame.draw.rect(екран, (90, 60, 40), (x0, 242, ш, 36), border_radius=6)
        if self.кръг < 3:
            pygame.draw.rect(екран, (80, 190, 90), (x0 + int(ш * self.зона[0]), 242, int(ш * self.зона[1]), 36))
        п = 0.5 + 0.5 * math.sin(self.фаза)
        sx = x0 + int(ш * п)
        pygame.draw.polygon(екран, БЯЛО, [(sx - 10, 222), (sx + 10, 222), (sx, 240)])
        pygame.draw.line(екран, БЯЛО, (sx, 240), (sx, 280), 3)
        for и in range(3):
            цвят = (255, 210, 60) if и < len(self.точки) and self.точки[и] > 0.6 else (120, 100, 80) if и >= len(self.точки) else (200, 120, 80)
            pygame.draw.circle(екран, цвят, (x0 + ш // 2 - 50 + и * 50, 320), 14)

    # ---------- шопска: рязане ----------
    def _начало_рязане(self):
        self.зел = self.настр.get("зеленчуци", [0, 1, 2, 3])          # 0 домат, 1 краставица, 2 чушка, 3 лук
        брой = self.настр.get("брой", 2)                              # реза от всеки зеленчук
        self.зел_ред = [з for з in self.зел for _ in range(брой)]
        self.обяснение = ["Шопска салата", "Натисни буквата, когато кръгът стигне ножа.",
                          "A  S  D. %d реза." % len(self.зел_ред)]
        интервал = self.настр.get("интервал", 1.05 if self.настр.get("ситно") else 1.4)   # секунди между резовете
        self.удари = [(1.8 + и * интервал, self.сл.randrange(3)) for и in range(len(self.зел_ред))]
        self.точки, self.следващ, self.резени = [], 0, []
        self.зеленчуци = [((230, 58, 46), 26), ((108, 184, 62), 20), ((240, 176, 32), 22), ((245, 240, 230), 22), ((240, 138, 42), 18)]

    def _клавиш_рязане(self, с):
        if с.type != pygame.KEYDOWN or с.key not in КЛАВИШИ_РЯЗАНЕ or self.следващ >= len(self.удари):
            return
        t, буква = self.удари[self.следващ]
        разлика = abs(self.време() - t)
        if разлика > 0.4:
            return                                           # твърде рано: не се брои
        точки = 0.0
        if КЛАВИШИ_РЯЗАНЕ.index(с.key) == буква:
            к = 1 - 0.4 * self.умора                         # уморен: трябва да си по-точен
            точки = 1.0 if разлика <= 0.13 * к else 0.6 if разлика <= 0.26 * к else 0.25
        self.точки.append(точки)
        if точки:
            self.резени.append((self.зеленчуци[self.зел_ред[self.следващ]][0], self.сл.uniform(-30, 30)))
        self.следващ += 1

    def _обнови_рязане(self, dt):
        while self.следващ < len(self.удари) and self.време() > self.удари[self.следващ][0] + 0.4:
            self.точки.append(0.0)                           # пропуснат рез
            self.следващ += 1
        if self.следващ >= len(self.удари) and self.време() > self.удари[-1][0] + 0.5:
            self._готово(sum(self.точки) / len(self.удари))

    def _рисувай_рязане(self, екран):
        pygame.draw.rect(екран, (200, 150, 90), (200, 300, 420, 140), border_radius=12)   # дъската
        pygame.draw.rect(екран, (150, 100, 56), (200, 300, 420, 140), 4, border_radius=12)
        цел = (410, 360)
        if self.следващ < len(self.удари):
            t, буква = self.удари[self.следващ]
            цвят, r = self.зеленчуци[self.зел_ред[self.следващ]]
            pygame.draw.circle(екран, цвят, цел, r + 18)
            pygame.draw.circle(екран, (40, 26, 18), цел, r + 18, 3)
            остава = t - self.време()
            радиус = int(40 + max(0.0, остава) * 150)
            if остава > -0.4:
                pygame.draw.circle(екран, БЯЛО, цел, радиус, 4)
            pygame.draw.circle(екран, ЗЛАТНО, цел, 40, 2)
            self._текст(екран, ИМЕНА_РЯЗАНЕ[буква], 48, ЗЛАТНО, (цел[0], 200), True)
        нож_y = 300 if self.следващ and self.време() - self.удари[self.следващ - 1][0] < 0.15 else 250
        pygame.draw.polygon(екран, (220, 225, 235), [(цел[0] - 6, нож_y), (цел[0] + 70, нож_y - 10), (цел[0] + 70, нож_y + 8), (цел[0] - 6, нож_y + 18)])
        pygame.draw.rect(екран, (110, 70, 40), (цел[0] + 70, нож_y - 12, 50, 22), border_radius=6)
        pygame.draw.ellipse(екран, (245, 245, 238), (660, 330, 220, 100))     # купата
        pygame.draw.ellipse(екран, (200, 196, 186), (660, 330, 220, 100), 4)
        for и, (цвят, dx) in enumerate(self.резени):
            pygame.draw.circle(екран, цвят, (770 + int(dx), 360 + (и % 3) * 8), 12)
        for и, т in enumerate(self.точки):
            pygame.draw.circle(екран, (255, 210, 60) if т >= 0.6 else (200, 120, 80) if т else (90, 60, 40), (300 + и * 30, 470), 10)

    # ---------- какво има в съда (тенджера, тиган) ----------
    ТЕГЛО = {"течност": 0.4, "прах": 0.25, "запръжка": 0.5, "парчета": 0.06}

    def _цвят_вътре(self, неща, печено=0.0):
        течни = [н for н in неща if н.get("вид") == "течност"]
        if not течни:
            return None
        цвят = list(pygame.Color(течни[0]["цвят"]))[:3]
        for н in неща:
            if н is течни[0]:
                continue
            т = self.ТЕГЛО.get(н.get("вид", "парчета"), 0.06)
            друг = pygame.Color(н["цвят"])
            цвят = [int(a + (b - a) * т) for a, b in zip(цвят, друг[:3])]
        if печено:
            цвят = [int(a + (b - a) * min(1.0, печено) * 0.75) for a, b in zip(цвят, (150, 84, 30))]
        return tuple(цвят)

    def _в_съда(self, п, съд, x0, y0, топлина=0.0, пяна=0.0):
        """Рисува съдържанието в отвора на тенджерата/тигана: течността (смесен цвят), парчетата, мехурчета."""
        г = self.арт["съдове"]["tendzhera" if съд == "тенджера" else "tigan"] if self.арт else {"x": 60, "y": 27, "rx": 42, "ry": 9}
        cx, cy, rx, ry = x0 + г["x"], y0 + г["y"], г["rx"], г["ry"]
        неща = self.съдържание.get(съд, [])
        печено = self.съдържание.get("печено", 0.0) if съд == "тиган" else 0.0
        цвят = self._цвят_вътре(неща, печено)
        if цвят:
            pygame.draw.ellipse(п, цвят, (cx - rx, cy - ry, 2 * rx, 2 * ry))
            тъмно = tuple(int(c * 0.78) for c in цвят)
            pygame.draw.arc(п, тъмно, (cx - rx, cy - ry, 2 * rx, 2 * ry), 0.3, math.pi - 0.3, 2)   # задният ръб в сянка
            pygame.draw.line(п, tuple(min(255, c + 40) for c in цвят), (cx - rx // 2, cy + ry // 2), (cx - rx // 5, cy + ry // 2 + 1))
        for и, н in enumerate(неща):
            вид = н.get("вид", "парчета")
            if вид == "течност":
                continue
            сл = random.Random(и * 31 + 7)
            ц = pygame.Color(н["цвят"])[:3]
            if печено and вид != "течност":
                ц = tuple(int(a + (b - a) * min(1.0, печено) * 0.6) for a, b in zip(ц, (140, 76, 24)))
            тъмно = tuple(int(c * 0.6) for c in ц)
            брой = 12 if вид == "парчета" else 10
            for к in range(брой):
                a, r = сл.uniform(0, 2 * math.pi), math.sqrt(сл.random()) * 0.82
                x = cx + r * rx * math.cos(a) + math.sin(self.кадър_време * 5 + к) * топлина * 1.5
                y = cy + r * ry * math.sin(a)
                if вид == "парчета":
                    pygame.draw.rect(п, тъмно, (int(x) - 1, int(y), 3, 2))
                    pygame.draw.rect(п, ц, (int(x) - 1, int(y), 2, 1))
                else:
                    п.set_at((int(x), int(y)), ц)
        if цвят and топлина > 0.45:                                     # мехурчета: колкото по-горещо, толкова повече
            сл = random.Random(int(self.кадър_време * 5))
            светло = tuple(min(255, c + 60) for c in цвят)
            for _ in range(int((топлина - 0.45) * 14)):
                a, r = сл.uniform(0, 2 * math.pi), math.sqrt(сл.random()) * 0.8
                pygame.draw.circle(п, светло, (int(cx + r * rx * math.cos(a)), int(cy + r * ry * math.sin(a))), сл.choice((1, 1, 2)), 1)
        if пяна > 0:                                                    # прелива: бяла пяна по ръба
            сл = random.Random(int(self.кадър_време * 3))
            for _ in range(int(пяна * 30)):
                a = сл.uniform(math.pi * 0.05, math.pi * 0.95)
                x, y = cx + (rx + 2) * math.cos(a), cy + (ry + 2) * math.sin(a) + сл.randint(0, 6)
                pygame.draw.circle(п, (250, 246, 236), (int(x), int(y)), сл.choice((1, 2, 2)))

    # ---------- кипване: доведи до кипене, без да прелее ----------
    def _начало_кипване(self):
        self.обяснение = ["", "S = дърва в огъня. Доведи водата до кипене.",
                          "Като заври, дръж огъня в зеленото - ако е силен, прелива!"]
        self.темп, self.кипи, self.прелива, self.общо = 0.15, 0.0, 0.0, 0.0
        self.нужно = self.настр.get("време", 3)

    def _клавиш_кипване(self, с):
        pass

    def _обнови_кипване(self, dt):
        к = pygame.key.get_pressed()
        if к[pygame.K_s] or к[pygame.K_w] or к[pygame.K_UP]:
            self.темп += 0.25 * dt
        self.темп = max(0.0, min(1.0, self.темп - 0.06 * dt))
        self.общо += dt
        if 0.78 <= self.темп <= 0.93:
            self.кипи += dt
        elif self.темп > 0.93:
            self.прелива += dt
        if self.кипи >= self.нужно or self.общо > 20:
            бързо = 1.0 if self.общо < 12 else 0.7
            self._готово(min(1.0, self.кипи / self.нужно) * (0.75 * бързо + 0.25) * (1 - min(0.8, self.прелива / 2)))

    def _пиксели_кипване(self, п):
        if self.арт:
            п.blit(self.арт["bob_ognishte"][0], (76, 126))
        огън = "ogan_malak" if self.темп < 0.4 else "ogan_sreden" if self.темп < 0.75 else "ogan_golyam"
        рисувай_ефект(п, огън, 160, 146, self.кадър_време)
        if self.арт and "tendzhera" in self.арт:
            п.blit(self.арт["tendzhera"][0], (100, 46))
        self._в_съда(п, "тенджера", 100, 46, топлина=self.темп, пяна=max(0.0, (self.темп - 0.93) * 12))
        if self.темп > 0.6:
            рисувай_ефект(п, "para", 160, 65, self.кадър_време, int(80 + 175 * min(1.0, (self.темп - 0.6) / 0.35)))
        self._лента(п, 34, 34, 14, 96, self.темп, (0.78, 0.93), (240, 120, 40))
        pygame.draw.rect(п, (40, 24, 16), (262, 128, 34, 6))                   # колко е врял
        pygame.draw.rect(п, (120, 190, 240), (263, 129, int(32 * min(1.0, self.кипи / self.нужно)), 4))

    def _надписи_кипване(self, екран):
        self._текст(екран, "огън", 20, СВЕТЛО, (41 * ПИКСЕЛ, 140 * ПИКСЕЛ))
        self._текст(екран, "S", 26, ЗЛАТНО, (41 * ПИКСЕЛ, 22 * ПИКСЕЛ), True)
        self._текст(екран, "кипи", 20, СВЕТЛО, (279 * ПИКСЕЛ, 140 * ПИКСЕЛ))
        if self.етап == "игра":
            if self.темп > 0.93:
                self._текст(екран, "Прелива! По-слаб огън!", 30, (255, 120, 80), (ШИР // 2, 110), True)
            elif self.темп >= 0.78:
                self._текст(екран, "Ври!", 30, (140, 210, 255), (ШИР // 2, 110), True)

    def _рисувай_кипване(self, екран):
        self._прости_пиксели(екран, self._пиксели_кипване, self._надписи_кипване)

    # ---------- запържване: брашното в олиото, бъркаш, докато стане златисто ----------
    def _начало_запържване(self):
        if not self.съдържание["тиган"]:
            self.съдържание["тиган"] = [dict(п) for п in self.настр.get("продукти", [])]
        self.съдържание["печено"] = 0.0
        self.бъркане, self.последен, self.ъгъл, self.загоряло, self.общо = 0.6, None, 0.0, 0.0, 0.0
        self.обяснение = ["", "A и D един след друг = бъркаш, за да не загори.",
                          "Когато стане златисто (зеленото), S = свали от огъня."]

    def _клавиш_запържване(self, с):
        if с.type == pygame.KEYDOWN and с.key in ДЕЙСТВИЕ:
            ц = self.съдържание["печено"]
            точно = 1.0 if 0.6 <= ц <= 0.82 else 0.6 if 0.48 <= ц <= 0.92 else 0.2
            self._готово(точно * (1 - min(0.7, self.загоряло / 3)))
            return
        self._клавиш_бъркане(с)

    def _обнови_запържване(self, dt):
        self.бъркане = max(0.0, self.бъркане - 0.3 * self.по_бавно * dt)
        self.общо += dt
        скорост = 0.07 if self.бъркане >= 0.3 else 0.13                 # без бъркане става по-бързо и на петна
        self.съдържание["печено"] += скорост * dt
        if self.бъркане < 0.3:
            self.загоряло += dt
        if self.съдържание["печено"] >= 1.15:
            self._готово(0.05)                                          # изгоря

    def _пиксели_запържване(self, п):
        if self.арт:
            п.blit(self.арт["bob_ognishte"][0], (76, 126))
        рисувай_ефект(п, "ogan_sreden", 150, 146, self.кадър_време)
        if self.арт and "tigan" in self.арт:
            п.blit(self.арт["tigan"][0], (92, 90))
        self._в_съда(п, "тиган", 92, 90, топлина=0.5)
        cx, cy = 92 + 58 + 30 * math.cos(self.ъгъл), 90 + 24 + 6 * math.sin(self.ъгъл)   # дървената шпатула
        pygame.draw.line(п, (40, 22, 12), (cx, cy), (cx - 20, cy - 40), 4)
        pygame.draw.line(п, (186, 132, 76), (cx, cy), (cx - 20, cy - 40), 2)
        pygame.draw.ellipse(п, (40, 22, 12), (cx - 5, cy - 3, 10, 6))
        pygame.draw.ellipse(п, (186, 132, 76), (cx - 4, cy - 2, 8, 4))
        if self.загоряло > 0.5 and self.бъркане < 0.3:
            рисувай_ефект(п, "para", 150, 100, self.кадър_време, 160)
        self._лента(п, 34, 34, 14, 96, min(1.0, self.съдържание["печено"] / 1.15), (0.6 / 1.15, 0.82 / 1.15), (214, 150, 60))
        self._лента(п, 272, 34, 14, 96, self.бъркане, (0.3, 1.0), (236, 226, 204))

    def _надписи_запържване(self, екран):
        self._текст(екран, "цвят", 20, СВЕТЛО, (41 * ПИКСЕЛ, 140 * ПИКСЕЛ))
        self._текст(екран, "S", 26, ЗЛАТНО, (41 * ПИКСЕЛ, 22 * ПИКСЕЛ), True)
        self._текст(екран, "бъркане", 20, СВЕТЛО, (279 * ПИКСЕЛ, 140 * ПИКСЕЛ))
        self._текст(екран, "A  D", 26, ЗЛАТНО, (279 * ПИКСЕЛ, 22 * ПИКСЕЛ), True)
        if self.етап == "игра" and self.бъркане < 0.3:
            self._текст(екран, "Залепва! Бъркай!", 30, (255, 120, 80), (ШИР // 2, 110), True)

    def _рисувай_запържване(self, екран):
        self._прости_пиксели(екран, self._пиксели_запържване, self._надписи_запържване)

    # ---------- сипи: запръжката от тигана в тенджерата ----------
    def _начало_сипи(self):
        self.ъгъл_т, self.остава, self.добре, self.пръснато, self.общо = 0.0, 1.0, 0.0, 0.0, 0.0
        self.капки = []
        self.обяснение = ["", "Задръж S = накланяш тигана над тенджерата.",
                          "Сипвай бавно (струята в зеленото), за да не пръска."]

    def _клавиш_сипи(self, с):
        pass

    def _струя(self):
        return max(0.0, (self.ъгъл_т - 18) / 50)

    def _обнови_сипи(self, dt):
        к = pygame.key.get_pressed()
        self.ъгъл_т += (45 if (к[pygame.K_s] or к[pygame.K_SPACE]) else -60) * dt
        self.ъгъл_т = max(0.0, min(75.0, self.ъгъл_т))
        self.общо += dt
        струя = self._струя()
        if self.остава > 0 and струя > 0:
            self.остава -= струя * 0.22 * dt
            if 0.25 <= струя <= 0.7:
                self.добре += dt
            elif струя > 0.8:
                self.пръснато += dt
                if self.сл.random() < 0.5:
                    self.капки.append([self.сл.uniform(60, 180), 90.0, self.сл.uniform(-40, 40), self.сл.uniform(-60, -20), 0.0])
        for к_ in self.капки:
            к_[0] += к_[2] * dt; к_[1] += к_[3] * dt; к_[3] += 200 * dt; к_[4] += dt
        self.капки = [к_ for к_ in self.капки if к_[4] < 0.6]
        if self.остава <= 0 or self.общо > 18:
            if self.съдържание["тиган"]:
                цвят = self._цвят_вътре(self.съдържание["тиган"], self.съдържание["печено"]) or (200, 120, 60)
                self.съдържание["тенджера"].append({"име": "запръжка", "вид": "запръжка", "цвят": "#%02x%02x%02x" % цвят})
                self.съдържание["тиган"] = []
            сипано = 1 - max(0.0, self.остава)
            време = max(0.5, self.общо - 1)
            self._готово(сипано * (0.35 + 0.65 * min(1.0, self.добре / време * 1.4)) * (1 - min(0.6, self.пръснато / 2)))

    def _пиксели_сипи(self, п):
        if self.арт:
            п.blit(self.арт["bob_ognishte"][0], (36, 126))
        рисувай_ефект(п, "ogan_malak", 120, 146, self.кадър_време)
        if self.арт and "tendzhera" in self.арт:
            п.blit(self.арт["tendzhera"][0], (60, 46))
        self._в_съда(п, "тенджера", 60, 46, топлина=0.6)
        тиган = pygame.Surface((150, 50), pygame.SRCALPHA)               # тиганът с запръжката, после го накланяме
        if self.арт and "tigan" in self.арт:
            тиган.blit(self.арт["tigan"][0], (0, 0))
        if self.остава > 0:
            self._в_съда(тиган, "тиган", 0, 0)
        завъртян = pygame.transform.rotate(тиган, self.ъгъл_т)
        център = (194, 14)
        п.blit(завъртян, завъртян.get_rect(center=център))
        a = math.radians(self.ъгъл_т)
        dx, dy = -63, -1                                                   # левият ръб на тигана спрямо центъра
        устна = (център[0] + dx * math.cos(a) + dy * math.sin(a), център[1] - dx * math.sin(a) + dy * math.cos(a))
        струя = self._струя()
        if струя > 0 and self.остава > 0 and self.съдържание["тиган"]:
            цвят = self._цвят_вътре(self.съдържание["тиган"], self.съдържание["печено"]) or (200, 120, 60)
            pygame.draw.line(п, tuple(int(c * 0.7) for c in цвят), устна, (устна[0] - 2, 76), max(1, int(1 + 3 * струя)) + 1)
            pygame.draw.line(п, цвят, устна, (устна[0] - 2, 76), max(1, int(1 + 3 * струя)))
        for (x, y, _, _, _) in self.капки:
            pygame.draw.rect(п, (190, 80, 40), (int(x), int(y), 2, 2))
        pygame.draw.rect(п, (40, 24, 16), (262, 128, 34, 6))                   # колко остава в тигана
        pygame.draw.rect(п, (214, 120, 60), (263, 129, int(32 * max(0.0, self.остава)), 4))
        self._лента(п, 290, 34, 12, 80, min(1.0, струя), (0.25, 0.7), (214, 120, 60))

    def _надписи_сипи(self, екран):
        self._текст(екран, "струя", 18, СВЕТЛО, (296 * ПИКСЕЛ, 124 * ПИКСЕЛ))
        self._текст(екран, "в тигана", 18, СВЕТЛО, (279 * ПИКСЕЛ, 142 * ПИКСЕЛ))
        if self.етап == "игра" and self._струя() > 0.8:
            self._текст(екран, "Пръска! По-бавно!", 30, (255, 120, 80), (ШИР // 2, 110), True)

    def _рисувай_сипи(self, екран):
        self._прости_пиксели(екран, self._пиксели_сипи, self._надписи_сипи)

    # ---------- лютеница: бъркане с гребло в котела ----------
    ЛЮТ_X, ЛЮТ_Y = 96, 22                                    # котелът (128x128) в сцената
    ЛЮТ_ВРЕМЕ = 14

    def _начало_лютеница(self):
        self.обяснение = ["Лютеница", "A и D един след друг = бъркаш с греблото.",
                          "Ако спреш да бъркаш, загаря и пръска!"]
        self.бъркане, self.последен, self.ъгъл = 0.6, None, 0.0
        self.добро_бъркане = self.общо = self.загоряло = 0.0
        self.пръски = []                                   # [x, y, vx, vy, живот] в пиксели
        self.темп, self.мехурчета = 0.6, []                 # за простата картинка без пиксел-арт

    def _клавиш_лютеница(self, с):
        self._клавиш_бъркане(с)

    def _обнови_лютеница(self, dt):
        self.бъркане = max(0.0, self.бъркане - 0.33 * self.по_бавно * dt)    # гъста е: спира бързо
        self.общо += dt
        if self.бъркане >= 0.4:
            self.добро_бъркане += dt
        elif self.бъркане < 0.2:
            self.загоряло += dt
        шанс = 0.5 if self.бъркане < 0.2 else 0.04           # пръска, когато загаря
        if self.сл.random() < шанс:
            цx, цy = self.ЛЮТ_X + 63, self.ЛЮТ_Y + 36
            self.пръски.append([цx + self.сл.uniform(-30, 30), цy + self.сл.uniform(-4, 4),
                                self.сл.uniform(-30, 30), self.сл.uniform(-90, -50), 0.0])
        for п in self.пръски:
            п[0] += п[2] * dt; п[1] += п[3] * dt; п[3] += 220 * dt; п[4] += dt
        self.пръски = [п for п in self.пръски if п[4] < 0.8]
        if self.общо >= self.ЛЮТ_ВРЕМЕ:
            self._готово(0.8 * self.добро_бъркане / self.общо + 0.2 * (1 - min(1.0, self.загоряло / 4)) + 0.05)

    def _гребло(self):
        """Върхът на греблото обикаля в лютеницата; дръжката стърчи нагоре вдясно."""
        цx, цy = self.ЛЮТ_X + 63, self.ЛЮТ_Y + 36
        връх = (цx + 26 * math.cos(self.ъгъл), цy + 5 * math.sin(self.ъгъл))
        return връх, (връх[0] + 30, връх[1] - 64)

    def _пиксели_лютеница(self, п):
        п.blit(self.арт["bob_ognishte"][0], (76, 126))
        огън = "ogan_golyam" if self.бъркане < 0.2 else "ogan_sreden"
        рисувай_ефект(п, огън, 160, 150, self.кадър_време)
        if "lyut_kazan" in self.арт:
            мехури = int(self.кадър_време * (6 if self.бъркане < 0.2 else 3)) % 4
            п.blit(self.арт["lyut_kazan"][мехури], (self.ЛЮТ_X, self.ЛЮТ_Y))
        else:
            п.blit(self._кадър("bob_garne", 0), (100, 28))
        връх, дръжка = self._гребло()
        pygame.draw.line(п, (40, 22, 12), (връх[0] + 1, връх[1]), (дръжка[0] + 1, дръжка[1]), 5)   # контур
        pygame.draw.line(п, (112, 70, 36), връх, дръжка, 3)                                          # дръжката
        pygame.draw.line(п, (186, 132, 76), (връх[0] - 1, връх[1]), (дръжка[0] - 1, дръжка[1]))     # светло отляво
        pygame.draw.ellipse(п, (40, 22, 12), (връх[0] - 6, връх[1] - 3, 12, 7))                      # лопатката
        pygame.draw.ellipse(п, (150, 98, 52), (връх[0] - 5, връх[1] - 2, 10, 5))
        дим = 60 + int(160 * max(0.0, 0.2 - self.бъркане) / 0.2)
        рисувай_ефект(п, "para", 160, self.ЛЮТ_Y + 30, self.кадър_време, дим)
        for (x, y, _, _, t) in self.пръски:
            цвят = (204, 74, 38) if t < 0.4 else (122, 26, 16)
            pygame.draw.rect(п, цвят, (int(x), int(y), 2, 2))
        цвят = (236, 226, 204) if self.бъркане >= 0.2 else (220, 70, 40)
        self._лента(п, 272, 34, 14, 96, self.бъркане, (0.4, 1.0), цвят)

    def _надписи_лютеница(self, екран):
        self._текст(екран, "бъркане", 20, СВЕТЛО, (279 * ПИКСЕЛ, 140 * ПИКСЕЛ))
        self._текст(екран, "A  D", 26, ЗЛАТНО, (279 * ПИКСЕЛ, 22 * ПИКСЕЛ), True)
        if self.етап == "игра":
            self._текст(екран, "%d с" % max(0, math.ceil(self.ЛЮТ_ВРЕМЕ - self.общо)), 26, ЗЛАТНО, (ШИР // 2 + 200, 84), True)
            if self.бъркане < 0.2:
                self._текст(екран, "Загаря! Бъркай!", 30, (255, 120, 80), (ШИР // 2, 110), True)

    def _рисувай_лютеница(self, екран):
        self._рисувай_бъркане(екран)

    # ---------- боб: бъркане и огън ----------
    def _начало_бъркане(self):
        self.обяснение = ["Боб чорба", "S = дърва в огъня: дръж температурата в зеленото.",
                          "A и D един след друг = бъркаш, за да не загори."]
        self.темп, self.бъркане, self.последен, self.ъгъл = 0.35, 0.6, None, 0.0
        self.в_зона = self.добро_бъркане = self.общо = 0.0
        self.варене = self.настр.get("време", 12)                     # секунди (от рецептата)
        self.мехурчета = []

    def _клавиш_бъркане(self, с):
        if с.type == pygame.KEYDOWN and с.key in (pygame.K_a, pygame.K_d, pygame.K_LEFT, pygame.K_RIGHT):
            страна = "л" if с.key in (pygame.K_a, pygame.K_LEFT) else "д"
            if страна != self.последен:
                self.бъркане = min(1.0, self.бъркане + 0.14)
                self.ъгъл += 1.6
            self.последен = страна

    def _обнови_бъркане(self, dt):
        к = pygame.key.get_pressed()
        if к[pygame.K_s] or к[pygame.K_w] or к[pygame.K_UP]:
            self.темп += 0.3 * dt
        self.темп += (-0.09 + self.сл.uniform(-0.05, 0.05)) * dt
        self.темп = max(0.0, min(1.0, self.темп))
        self.бъркане = max(0.0, self.бъркане - 0.28 * self.по_бавно * dt)
        self.общо += dt
        if 0.45 <= self.темп <= 0.72:
            self.в_зона += dt
        if self.бъркане >= 0.35:
            self.добро_бъркане += dt
        if self.темп > 0.45 and self.сл.random() < self.темп * 0.5:
            self.мехурчета.append([self.сл.uniform(-90, 90), self.сл.uniform(-30, 30), 0.0])
        for м in self.мехурчета:
            м[2] += dt
        self.мехурчета = [м for м in self.мехурчета if м[2] < 0.5]
        if self.общо >= self.варене:
            self._готово(0.6 * self.в_зона / self.общо + 0.4 * self.добро_бъркане / self.общо + 0.05)

    def _рисувай_бъркане(self, екран):
        цx, цy = 480, 240
        огън = int(20 + 60 * self.темп)                     # огънят под гърнето
        for к in range(5):                                  # дървата
            pygame.draw.line(екран, (90, 56, 30), (цx - 90 + к * 40, 425), (цx - 60 + к * 40, 410), 9)
        for к, цвят in enumerate(((200, 52, 24), (240, 120, 32), (255, 200, 64))):
            pygame.draw.ellipse(екран, цвят, (цx - огън + к * 12, 405 - огън // 2 + к * 8, 2 * огън - к * 24, огън - к * 10))
        pygame.draw.ellipse(екран, (154, 84, 48), (цx - 170, цy - 80, 340, 220))   # гърнето
        pygame.draw.ellipse(екран, (200, 122, 72), (цx - 160, цy - 90, 320, 90))
        pygame.draw.ellipse(екран, (196, 122, 48), (цx - 140, цy - 80, 280, 70))   # чорбата
        for (dx, dy, t) in self.мехурчета:
            pygame.draw.circle(екран, (232, 168, 88), (цx + int(dx), цy - 45 + int(dy)), int(4 + 10 * t), 2)
        край = (цx + int(110 * math.cos(self.ъгъл)), цy - 45 + int(26 * math.sin(self.ъгъл)))   # лъжицата
        pygame.draw.line(екран, (120, 76, 40), край, (край[0] + 40, край[1] - 150), 10)
        pygame.draw.ellipse(екран, (120, 76, 40), (край[0] - 18, край[1] - 10, 36, 20))
        # термометър (вляво) и бъркане (вдясно)
        for (x, стойност, зона, надпис) in ((120, self.темп, (0.45, 0.72), "огън"), (800, self.бъркане, (0.35, 1.0), "бъркане")):
            pygame.draw.rect(екран, (40, 26, 18), (x - 6, 104, 52, 312), border_radius=10)
            pygame.draw.rect(екран, (80, 190, 90), (x, 110 + int(300 * (1 - зона[1])), 40, int(300 * (зона[1] - зона[0]))))
            pygame.draw.rect(екран, (240, 120, 40) if x < 400 else (230, 220, 200), (x + 10, 110 + int(300 * (1 - стойност)), 20, int(300 * стойност) + 1))
            self._текст(екран, надпис, 20, СВЕТЛО, (x + 20, 440))
        if self.етап == "игра":
            self._текст(екран, "%d" % max(0, math.ceil(self.варене - self.общо)), 30, ЗЛАТНО, (ШИР // 2, 90), True)

    # ---------- добави: продуктите по реда от рецептата ----------
    КУПИЧКИ_Y = 146

    def _купички_x(self):
        н = len(self.купички)
        return [160 + int((и - 1) * 80) for и in range(н)]

    def _начало_добави(self):
        продукти = self.настр.get("продукти") or [{"име": "сол", "цвят": "#f4f2ee"}]
        self.продукти = [(п["име"], tuple(pygame.Color(п.get("цвят", "#e0d0b0")))[:3]) for п in продукти][:4]
        self.колко = [п.get("колко", "") for п in продукти][:4]
        self.пълни = [dict(п) for п in продукти][:4]
        self.в = self.настр.get("в", "")                               # тенджера / тиган / (празно = купата или котела)
        self.иконки = {}
        for и, п in enumerate(self.пълни):
            път = tiles.намери_картинка(os.path.join("items", п.get("икона", "") + ".png")) if п.get("икона") else None
            if път:
                self.иконки[и] = pygame.image.load(път)
        self.следващ, self.точки, self.грешки, self.прод_старт = 0, [], 0, 0.0
        self._нареди()
        self.летящи, self.клатене = [], {}
        self.обяснение = ["Добави продуктите", "Слагай по реда от рецептата (вляво).",
                          "A  S  D = това, което е наред."]

    def _нареди(self):
        """На плота има 3 места (A S D): следващият продукт и още до 2 от останалите, разбъркани."""
        останали = list(range(self.следващ + 1, len(self.продукти)))
        self.сл.shuffle(останали)
        self.купички = ([self.следващ] if self.следващ < len(self.продукти) else []) + останали[:2]
        self.сл.shuffle(self.купички)
        self.клатене = {}

    def _сложи(self, и, точки):
        if self.в in ("тенджера", "тиган"):
            self.съдържание[self.в].append(self.пълни[self.купички[и]])
        self.точки.append(точки)
        self.летящи.append((self._купички_x()[и], self.следващ, self.време()))
        self.следващ, self.грешки, self.прод_старт = self.следващ + 1, 0, self.време()
        self._нареди()

    def _клавиш_добави(self, с):
        if с.type != pygame.KEYDOWN or с.key not in КЛАВИШИ_РЯЗАНЕ or self.следващ >= len(self.продукти):
            return
        и = КЛАВИШИ_РЯЗАНЕ.index(с.key)
        if и >= len(self.купички):
            return
        if self.купички[и] == self.следващ:
            бързо = self.време() - self.прод_старт
            self._сложи(и, max(0.0, (1.0 if бързо <= 2.5 / self.по_бавно else 0.7) - 0.35 * self.грешки))
        else:
            self.грешки += 1                                      # сбърка купичката: тя се клати
            self.клатене[и] = self.време()

    def _обнови_добави(self, dt):
        if self.следващ < len(self.продукти) and self.време() - self.прод_старт > 6:
            self._сложи(self.купички.index(self.следващ), 0.0)    # забави се: продуктът пада сам, без точки
        if self.следващ >= len(self.продукти) and self.време() - self.прод_старт > 0.7:
            self._готово(sum(self.точки) / len(self.продукти))

    def _купичка(self, п, x, y, цвят):
        pygame.draw.ellipse(п, (40, 22, 12), (x - 17, y - 7, 34, 17))          # контур
        pygame.draw.ellipse(п, (150, 84, 44), (x - 16, y - 6, 32, 15))         # глината
        pygame.draw.ellipse(п, (196, 120, 64), (x - 16, y - 6, 32, 9))         # ръбът (по-светъл)
        pygame.draw.ellipse(п, (40, 22, 12), (x - 13, y - 5, 26, 7))
        pygame.draw.ellipse(п, цвят, (x - 12, y - 4, 24, 5))                    # продуктът
        п.set_at((x - 7, y - 3), (255, 255, 255))

    def _съд_добави(self, п):
        """Къде отиват продуктите: тенджерата, тигана, купата или котела. Връща точката, в която падат."""
        if self.в == "тенджера":
            if self.арт and "tendzhera" in self.арт:
                п.blit(self.арт["tendzhera"][0], (100, 4))
            self._в_съда(п, "тенджера", 100, 4, топлина=0.5 if any(н.get("вид") == "течност" for н in self.съдържание["тенджера"]) else 0)
            return (160, 31)
        if self.в == "тиган":
            if self.арт and "tigan" in self.арт:
                п.blit(self.арт["tigan"][0], (92, 40))
            self._в_съда(п, "тиган", 92, 40)
            return (150, 64)
        if self.арт and self.предмет == "lyutenitsa" and "lyut_kazan" in self.арт:
            п.blit(pygame.transform.scale(self.арт["lyut_kazan"][int(self.кадър_време * 3) % 4], (64, 64)), (128, 26))
            return (160, 44)
        if self.арт and self.предмет == "shopska":
            п.blit(self._кадър("shopska_kupa", 9 if self.следващ >= len(self.продукти) else 8), (118, 56))
            return (160, 66)
        if self.арт and "bob_garne" in self.арт:
            п.blit(self._кадър("bob_garne", int(self.кадър_време * 3) % 4), (100, 6))
            return (160, 36)
        pygame.draw.ellipse(п, (40, 22, 12), (118, 34, 84, 60))
        pygame.draw.ellipse(п, (154, 84, 48), (120, 36, 80, 56))
        pygame.draw.ellipse(п, (196, 122, 48), (126, 38, 68, 18))
        return (160, 46)

    def _пиксели_добави(self, п):
        цел = self._съд_добави(п)
        pygame.draw.rect(п, (62, 38, 22), (6, 28, 82, 16 + 14 * len(self.продукти)))    # рецептата
        pygame.draw.rect(п, (240, 226, 190), (8, 30, 78, 12 + 14 * len(self.продукти)))
        for и, x in enumerate(self._купички_x()):
            dx = 0
            if self.време() - self.клатене.get(и, -9) < 0.4 and self.етап == "игра":
                dx = int(3 * math.sin(self.време() * 60))
            пълна = self.купички[и] >= self.следващ or self.етап != "игра"
            икона = self.иконки.get(self.купички[и])
            if икона:                                                          # продуктът (буркан, торба, шише...)
                pygame.draw.ellipse(п, (60, 36, 22), (x - 16, self.КУПИЧКИ_Y - 4, 32, 7))   # сянка на плота
                if пълна:
                    п.blit(икона, (x - 16 + dx, self.КУПИЧКИ_Y - 32))
                else:
                    празна = икона.copy(); празна.set_alpha(70)
                    п.blit(празна, (x - 16, self.КУПИЧКИ_Y - 32))
            elif пълна:
                self._купичка(п, x + dx, self.КУПИЧКИ_Y, self.продукти[self.купички[и]][1])
            else:
                self._купичка(п, x, self.КУПИЧКИ_Y, (60, 36, 22))                 # празна
        for (x0, прод, t0) in self.летящи:                                         # продуктът лети към съда
            к = (self.време() - t0) / 0.45
            if 0 <= к < 1:
                x = x0 + (цел[0] - x0) * к
                y = self.КУПИЧКИ_Y + (цел[1] - self.КУПИЧКИ_Y) * к - 40 * math.sin(math.pi * к)
                pygame.draw.rect(п, (40, 22, 12), (int(x) - 3, int(y) - 3, 6, 6))
                pygame.draw.rect(п, self.продукти[прод][1], (int(x) - 2, int(y) - 2, 4, 4))

    def _надписи_добави(self, екран):
        self._текст(екран, "Рецепта", 20, (90, 50, 24), (47 * ПИКСЕЛ, 37 * ПИКСЕЛ), True)
        for и, (име, _) in enumerate(self.продукти):
            готов = и < self.следващ
            цвят = (60, 120, 50) if готов else (170, 40, 20) if и == self.следващ else (90, 70, 50)
            знак = "✓ " if готов else "→ " if и == self.следващ else "   "
            self._текст(екран, "%s%d. %s" % (знак, и + 1, име), 16, цвят, (47 * ПИКСЕЛ, (49 + и * 14) * ПИКСЕЛ))
        for и, x in enumerate(self._купички_x()):
            горе = self.КУПИЧКИ_Y - (38 if self.иконки.get(self.купички[и]) else 17)
            self._текст(екран, ИМЕНА_РЯЗАНЕ[и], 26, ЗЛАТНО, (x * ПИКСЕЛ, горе * ПИКСЕЛ), True)
            self._текст(екран, self.продукти[self.купички[и]][0], 18, СВЕТЛО, (x * ПИКСЕЛ, (self.КУПИЧКИ_Y + 15) * ПИКСЕЛ))
            if self.колко[self.купички[и]]:
                self._текст(екран, self.колко[self.купички[и]], 15, (200, 190, 170), (x * ПИКСЕЛ, (self.КУПИЧКИ_Y + 22) * ПИКСЕЛ))

    def _рисувай_добави(self, екран):
        self._прости_пиксели(екран, self._пиксели_добави, self._надписи_добави)

    def _прости_пиксели(self, екран, пиксели, надписи):
        """Когато няма пиксел-арт: същата сцена върху обикновен фон."""
        п = self.пиксели
        п.fill((96, 62, 40))
        pygame.draw.rect(п, (110, 70, 40), (0, 143, 320, 37))
        пиксели(п)
        екран.blit(pygame.transform.scale(п, (ШИР, ВИС)), (0, 0))
        надписи(екран)

    # ---------- печене и пържене: свали навреме ----------
    def _начало_печене(self):
        self.съд = self.настр.get("съд", "скара")                    # скара (чушки) или тиган (лук, месо...)
        self.сурово = tuple(pygame.Color(self.настр.get("цвят", "#c8302a")))[:3]
        self.изпечено = tuple(pygame.Color(self.настр.get("готово", "#8a2a18")))[:3]
        брой = max(1, min(3, self.настр.get("брой", 3)))
        self.парчета = [{"d": 0.0, "скорост": self.сл.uniform(0.10, 0.17), "старт": и * 0.9 + self.сл.uniform(0, 0.6),
                         "точки": None, "кога": 0.0} for и in range(брой)]
        дума = "чушките" if self.съд == "скара" else "лука"
        self.обяснение = ["Печене", "%s се пекат над огъня. Не ги оставяй да изгорят!" % дума.capitalize(),
                          "Когато лентата е в зеленото: A S D = свали."]

    def _клавиш_печене(self, с):
        if с.type != pygame.KEYDOWN or с.key not in КЛАВИШИ_РЯЗАНЕ:
            return
        и = КЛАВИШИ_РЯЗАНЕ.index(с.key)
        if и >= len(self.парчета):
            return
        ч = self.парчета[и]
        if ч["точки"] is None and ч["d"] > 0.05:
            d = ч["d"]
            ч["точки"] = 1.0 if 0.7 <= d <= 0.92 else 0.6 if 0.58 <= d <= 1.02 else 0.25 if d >= 0.4 else 0.1
            ч["кога"] = self.време()

    def _обнови_печене(self, dt):
        for ч in self.парчета:
            if ч["точки"] is None and self.време() > ч["старт"]:
                ч["d"] += ч["скорост"] * dt
                if ч["d"] > 1.15:                                          # изгоря
                    ч["точки"], ч["кога"] = 0.0, self.време()
        if all(ч["точки"] is not None for ч in self.парчета) and self.време() - max(ч["кога"] for ч in self.парчета) > 0.6:
            self._готово(sum(ч["точки"] for ч in self.парчета) / len(self.парчета))

    def _печене_x(self):
        н = len(self.парчета)
        return [160 + int((и - (н - 1) / 2) * 60) for и in range(н)]

    def _цвят_печене(self, d):
        if d <= 0.8:
            к = d / 0.8
            return tuple(int(a + (b - a) * к) for a, b in zip(self.сурово, self.изпечено))
        к = min(1.0, (d - 0.8) / 0.35)
        return tuple(int(a + (b - a) * к) for a, b in zip(self.изпечено, (34, 22, 18)))

    def _парче(self, п, x, y, d, семе):
        цвят = self._цвят_печене(d)
        тъмно = tuple(int(c * 0.7) for c in цвят)
        светло = tuple(min(255, int(c * 1.25) + 20) for c in цвят)
        if self.съд == "скара":                                         # чушка
            pygame.draw.ellipse(п, (30, 14, 10), (x - 15, y - 6, 30, 13))
            pygame.draw.ellipse(п, цвят, (x - 14, y - 5, 28, 11))
            pygame.draw.ellipse(п, тъмно, (x - 12, y, 25, 5))
            pygame.draw.line(п, светло, (x - 8, y - 3), (x + 6, y - 3))
            pygame.draw.rect(п, (30, 14, 10), (x - 19, y - 3, 6, 5))
            pygame.draw.rect(п, (70, 130, 50), (x - 18, y - 2, 4, 3))    # дръжката
        else:                                                           # купчинка нарязан лук в тигана
            сл = random.Random(семе)
            for _ in range(16):
                px, py = x + сл.randint(-12, 10), y + сл.randint(-5, 3)
                pygame.draw.rect(п, (30, 14, 10), (px - 1, py - 1, 5, 4))
                pygame.draw.rect(п, цвят, (px, py, 3, 2))
                п.set_at((px, py), светло)
        сл = random.Random(семе * 7)                                     # загорели петна
        for _ in range(int(max(0.0, d - 0.55) * 22)):
            п.set_at((x + сл.randint(-11, 10), y + сл.randint(-3, 3)), (34, 22, 18))

    def _пиксели_печене(self, п):
        if self.арт:
            п.blit(self.арт["bob_ognishte"][0], (76, 126))
        рисувай_ефект(п, "ogan_golyam", 160, 146, self.кадър_време)
        for x in (112, 208):
            рисувай_ефект(п, "ogan_malak", x, 146, self.кадър_време + x)
        if self.съд == "скара":
            pygame.draw.rect(п, (20, 20, 26), (40, 108, 240, 4))
            pygame.draw.line(п, (110, 114, 124), (40, 108), (279, 108))
            for x in range(44, 280, 12):
                pygame.draw.line(п, (40, 40, 48), (x, 104), (x, 116))
        else:
            pygame.draw.rect(п, (20, 20, 26), (264, 102, 44, 6))         # дръжката на тигана
            pygame.draw.rect(п, (90, 56, 30), (268, 103, 38, 4))
            pygame.draw.ellipse(п, (20, 20, 26), (56, 90, 208, 30))
            pygame.draw.ellipse(п, (58, 60, 70), (60, 92, 200, 25))
            pygame.draw.ellipse(п, (236, 196, 90), (70, 96, 180, 16))   # олиото
            pygame.draw.ellipse(п, (214, 164, 60), (70, 101, 180, 11))
        for и, (x, ч) in enumerate(zip(self._печене_x(), self.парчета)):
            if ч["точки"] is None:
                y = 103 if self.съд == "скара" else 104
                self._парче(п, x, y, ч["d"], и + 1)
            else:                                                       # свалено: в чинията горе
                pygame.draw.ellipse(п, (40, 30, 30), (x - 19, 47, 38, 12))
                pygame.draw.ellipse(п, (236, 232, 224), (x - 18, 48, 36, 10))
                self._парче(п, x, 50, ч["d"], и + 1)
            if ч["точки"] is None:                                       # лента: колко е изпечено
                pygame.draw.rect(п, (40, 24, 16), (x - 16, 84, 32, 5))
                pygame.draw.rect(п, (70, 160, 76), (x - 15 + int(30 * 0.7), 85, int(30 * 0.22), 3))
                pygame.draw.rect(п, (255, 230, 150), (x - 15, 85, int(30 * min(1.0, ч["d"] / 1.15)), 3))

    def _надписи_печене(self, екран):
        for и, (x, ч) in enumerate(zip(self._печене_x(), self.парчета)):
            if ч["точки"] is None:
                self._текст(екран, ИМЕНА_РЯЗАНЕ[и], 26, ЗЛАТНО, (x * ПИКСЕЛ, 76 * ПИКСЕЛ), True)
            else:
                надпис = "изгоря" if ч["точки"] == 0 else "сурово" if ч["точки"] < 0.3 else "★" * (3 if ч["точки"] >= 1 else 2 if ч["точки"] >= 0.6 else 1)
                self._текст(екран, надпис, 20, ЗЛАТНО, (x * ПИКСЕЛ, 36 * ПИКСЕЛ), True)

    def _рисувай_печене(self, екран):
        self._прости_пиксели(екран, self._пиксели_печене, self._надписи_печене)

    # ---------- миене на чинии (чистачът на мивката) ----------
    def _начало_миене(self):
        брой = max(1, min(6, int(self.настр.get("брой", 1))))
        self.чинии_м = []
        for _ in range(брой):
            петна = [(self.сл.randint(-14, 12), self.сл.randint(-5, 4), self.сл.choice(((140, 90, 40), (200, 60, 40), (110, 120, 50))))
                     for _ in range(9)]
            self.чинии_м.append({"мръсно": 1.0, "петна": петна, "време": 0.0})
        self.текуща, self.последен, self.ъгъл, self.общо = 0, None, 0.0, 0.0
        self.пяна = []
        self.обяснение = ["Миене на чинии", "A и D един след друг = търкаш с гъбата.",
                          "Измий %d %s. Колкото по-бързо, толкова по-добре." % (брой, "чиния" if брой == 1 else "чинии")]

    def _клавиш_миене(self, с):
        if с.type != pygame.KEYDOWN or с.key not in (pygame.K_a, pygame.K_d, pygame.K_LEFT, pygame.K_RIGHT):
            return
        if self.текуща >= len(self.чинии_м):
            return
        страна = "л" if с.key in (pygame.K_a, pygame.K_LEFT) else "д"
        if страна == self.последен:
            return
        self.последен = страна
        self.ъгъл += 1.3
        ч = self.чинии_м[self.текуща]
        ч["мръсно"] = max(0.0, ч["мръсно"] - 0.11 / self.по_бавно)
        for _ in range(3):
            self.пяна.append([160 + self.сл.uniform(-26, 26), 108 + self.сл.uniform(-8, 6), 0.0, self.сл.choice((1, 2, 2, 3))])
        if ч["мръсно"] <= 0:
            self.текуща += 1

    def _обнови_миене(self, dt):
        self.общо += dt
        if self.текуща < len(self.чинии_м):
            self.чинии_м[self.текуща]["време"] += dt
        for м in self.пяна:
            м[2] += dt
        self.пяна = [м for м in self.пяна if м[2] < 1.2][-60:]
        if self.текуща >= len(self.чинии_м) or self.общо > 8 * len(self.чинии_м):
            оценки = [1.0 if ч["мръсно"] <= 0 and ч["време"] <= 3 else 0.7 if ч["мръсно"] <= 0 and ч["време"] <= 5
                      else 0.45 if ч["мръсно"] <= 0 else 0.3 * (1 - ч["мръсно"]) for ч in self.чинии_м]
            self._готово(sum(оценки) / len(оценки))

    def _чиния_м(self, п, x, y, ч):
        pygame.draw.ellipse(п, (40, 40, 52), (x - 23, y - 10, 46, 21))
        pygame.draw.ellipse(п, (58, 106, 200), (x - 22, y - 9, 44, 19))          # синият ръб
        pygame.draw.ellipse(п, (255, 255, 255), (x - 20, y - 8, 40, 16))
        pygame.draw.ellipse(п, (228, 226, 234), (x - 14, y - 5, 28, 10))
        видими = int(round(len(ч["петна"]) * ч["мръсно"]))
        for (dx, dy, цвят) in ч["петна"][:видими]:
            pygame.draw.rect(п, цвят, (x + dx, y + dy, 3, 2))
            п.set_at((x + dx + 1, y + dy - 1), цвят)

    def _пиксели_миене(self, п):
        pygame.draw.rect(п, (90, 60, 36), (0, 128, 320, 52))                   # плотът
        pygame.draw.rect(п, (120, 82, 50), (0, 128, 320, 3))
        pygame.draw.rect(п, (30, 30, 38), (94, 76, 132, 60))                   # мивката
        pygame.draw.rect(п, (150, 156, 168), (96, 78, 128, 56))
        pygame.draw.rect(п, (110, 116, 130), (100, 84, 120, 48))
        pygame.draw.rect(п, (120, 176, 220), (102, 96, 116, 34))               # водата
        pygame.draw.line(п, (190, 224, 246), (106, 98), (150, 98))
        pygame.draw.rect(п, (30, 30, 38), (154, 46, 12, 30))                    # чешмата
        pygame.draw.rect(п, (170, 176, 188), (156, 48, 8, 26))
        pygame.draw.rect(п, (30, 30, 38), (154, 44, 30, 6))
        pygame.draw.rect(п, (170, 176, 188), (156, 45, 26, 4))
        останали = len(self.чинии_м) - self.текуща - 1                        # мръсните (вляво)
        for к in range(max(0, останали)):
            self._чиния_м(п, 50, 124 - к * 5, {"мръсно": 1.0, "петна": self.чинии_м[-1 - к]["петна"]})
        for к in range(min(self.текуща, len(self.чинии_м))):                    # сушилката с чистите (вдясно)
            pygame.draw.ellipse(п, (40, 40, 52), (254 + к * 7, 80, 8, 42))
            pygame.draw.ellipse(п, (255, 255, 255), (255 + к * 7, 81, 6, 40))
        pygame.draw.rect(п, (60, 40, 24), (248, 118, 52, 6))
        if self.текуща < len(self.чинии_м):
            self._чиния_м(п, 160, 110, self.чинии_м[self.текуща])
            gx, gy = 160 + 16 * math.cos(self.ъгъл), 106 + 4 * math.sin(self.ъгъл)   # гъбата
            pygame.draw.rect(п, (40, 30, 10), (int(gx) - 8, int(gy) - 6, 16, 10))
            pygame.draw.rect(п, (250, 216, 70), (int(gx) - 7, int(gy) - 5, 14, 5))
            pygame.draw.rect(п, (70, 150, 70), (int(gx) - 7, int(gy), 14, 3))
        for (x, y, t, r) in self.пяна:
            pygame.draw.circle(п, (250, 252, 255), (int(x), int(y - t * 10)), r)
            pygame.draw.circle(п, (180, 200, 220), (int(x), int(y - t * 10)), r, 1)
        if self.текуща < len(self.чинии_м):
            self._лента(п, 272, 34, 14, 70, 1 - self.чинии_м[self.текуща]["мръсно"], (0.99, 1.0), (120, 200, 240))

    def _надписи_миене(self, екран):
        self._текст(екран, "A  D", 26, ЗЛАТНО, (279 * ПИКСЕЛ, 22 * ПИКСЕЛ), True)
        self._текст(екран, "чисто", 18, СВЕТЛО, (279 * ПИКСЕЛ, 114 * ПИКСЕЛ))
        self._текст(екран, "%d / %d" % (min(self.текуща, len(self.чинии_м)), len(self.чинии_м)), 26, ЗЛАТНО,
                    (ШИР // 2, 84), True)

    def _рисувай_миене(self, екран):
        self._прости_пиксели(екран, self._пиксели_миене, self._надписи_миене)

    # ---------- касата: маркирай и върни ресто ----------
    МОНЕТИ = ((pygame.K_1, 1), (pygame.K_2, 2), (pygame.K_3, 5), (pygame.K_4, 10), (pygame.K_5, 20), (pygame.K_6, 50))

    def _начало_ресто(self):
        self.сметка = int(self.настр.get("сметка", 7))
        self.дава = int(self.настр.get("дава", 10))
        self.стока = self.настр.get("стока", {})
        self.върнато, self.грешки, self.общо, self.съобщение = [], 0, 0.0, ""
        self.обяснение = ["Касата", "Клиентът дава %d лв за сметка %d лв. Върни рестото!" % (self.дава, self.сметка),
                          "1=1лв 2=2лв 3=5лв 4=10лв 5=20лв 6=50лв   Backspace=върни   Enter=дай"]

    def _клавиш_ресто(self, с):
        if с.type != pygame.KEYDOWN:
            return
        for клавиш, стойност in self.МОНЕТИ:
            if с.key in (клавиш, getattr(pygame, "K_KP%d" % (self.МОНЕТИ.index((клавиш, стойност)) + 1))):
                self.върнато.append(стойност)
                self.съобщение = ""
                return
        if с.key == pygame.K_BACKSPACE and self.върнато:
            self.върнато.pop()
        elif с.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            if sum(self.върнато) == self.дава - self.сметка:
                бързо = 1.0 if self.общо < 8 else 0.8 if self.общо < 15 else 0.6
                монети = len(self.върнато)
                най_малко = self._най_малко(self.дава - self.сметка)
                self._готово(max(0.35, бързо - 0.25 * self.грешки - (0.1 if монети > най_малко else 0)))
            else:
                self.грешки += 1
                разлика = sum(self.върнато) - (self.дава - self.сметка)
                self.съобщение = "Грешно! Даваш %s с %d лв." % ("повече" if разлика > 0 else "по-малко", abs(разлика))
                if self.грешки >= 3:
                    self._готово(0.1)

    def _най_малко(self, сума):
        брой = 0
        for м in (50, 20, 10, 5, 2, 1):
            брой += сума // м
            сума %= м
        return брой

    def _обнови_ресто(self, dt):
        self.общо += dt

    def _пиксели_ресто(self, п):
        pygame.draw.rect(п, (90, 60, 36), (0, 120, 320, 60))                    # тезгяхът
        pygame.draw.rect(п, (120, 82, 50), (0, 120, 320, 3))
        pygame.draw.rect(п, (40, 40, 48), (200, 60, 100, 62))                    # касовият апарат
        pygame.draw.rect(п, (110, 116, 130), (202, 62, 96, 58))
        pygame.draw.rect(п, (30, 60, 40), (210, 68, 80, 18))                    # екранчето
        pygame.draw.rect(п, (60, 40, 28), (190, 122, 120, 26))                   # чекмеджето с парите
        for и, (_, стойност) in enumerate(self.МОНЕТИ):
            x = 198 + и * 18
            if стойност <= 2:
                pygame.draw.circle(п, (40, 30, 10), (x + 6, 135), 7)
                pygame.draw.circle(п, (230, 196, 90) if стойност == 2 else (200, 200, 210), (x + 6, 135), 6)
            else:
                pygame.draw.rect(п, (30, 40, 30), (x - 1, 126, 15, 18))
                цвят = {5: (150, 110, 200), 10: (120, 180, 120), 20: (230, 170, 90), 50: (230, 130, 130)}[стойност]
                pygame.draw.rect(п, цвят, (x, 127, 13, 16))
        for и, (к, брой) in enumerate(list(self.стока.items())[:4]):         # стоката на тезгяха
            pygame.draw.ellipse(п, (40, 30, 20), (20 + и * 40, 104, 30, 16))
            pygame.draw.ellipse(п, (220, 200, 160), (21 + и * 40, 105, 28, 14))
        for и, стойност in enumerate(self.върнато[-12:]):                       # рестото на тезгяха
            x, y = 30 + (и % 6) * 22, 150 + (и // 6) * 14
            if стойност <= 2:
                pygame.draw.circle(п, (230, 196, 90) if стойност == 2 else (200, 200, 210), (x, y), 6)
            else:
                pygame.draw.rect(п, {5: (150, 110, 200), 10: (120, 180, 120), 20: (230, 170, 90), 50: (230, 130, 130)}[стойност], (x - 8, y - 5, 18, 11))

    def _надписи_ресто(self, екран):
        self._текст(екран, "%d лв" % self.сметка, 34, (140, 255, 160), (250 * ПИКСЕЛ, 77 * ПИКСЕЛ), True)
        self._текст(екран, "Сметка: %d лв   Клиентът дава: %d лв" % (self.сметка, self.дава), 28, БЯЛО, (ШИР // 2, 110), True)
        self._текст(екран, "Връщаш: %d лв" % sum(self.върнато), 30, ЗЛАТНО, (ШИР // 2 - 120, 500), True)
        for и, (_, стойност) in enumerate(self.МОНЕТИ):
            self._текст(екран, str(и + 1), 18, ЗЛАТНО, ((198 + и * 18 + 6) * ПИКСЕЛ, 116 * ПИКСЕЛ), True)
            self._текст(екран, "%dлв" % стойност, 15, БЯЛО, ((198 + и * 18 + 6) * ПИКСЕЛ, 152 * ПИКСЕЛ), True)
        имена = ", ".join("%s x%d" % (к, б) for к, б in self.стока.items())
        self._текст(екран, имена, 18, СВЕТЛО, (ШИР // 2 - 150, 300))
        if self.съобщение:
            self._текст(екран, self.съобщение, 28, (255, 120, 80), (ШИР // 2, 160), True)

    def _рисувай_ресто(self, екран):
        self._прости_пиксели(екран, self._пиксели_ресто, self._надписи_ресто)

    # ---------- доене на кравата ----------
    def _начало_доене(self):
        self.мляко, self.последен, self.общо, self.ритъм, self.кога = 0.0, None, 0.0, 0.0, -1.0
        self.капки = []
        self.обяснение = ["Доене", "A и D един след друг, спокойно - като кравата дъвче.",
                          "Твърде бързо = кравата се дразни и рита кофата!"]

    def _клавиш_доене(self, с):
        if с.type != pygame.KEYDOWN or с.key not in (pygame.K_a, pygame.K_d):
            return
        страна = "л" if с.key == pygame.K_a else "д"
        if страна == self.последен:
            return
        self.последен = страна
        интервал = self.общо - self.кога
        self.кога = self.общо
        if интервал < 0.18:                                   # прекалено бързо
            self.ритъм = max(0.0, self.ритъм - 0.3)
            self.мляко = max(0.0, self.мляко - 0.04)
        else:
            добре = 1.0 if 0.3 <= интервал <= 0.7 else 0.5
            self.ритъм = min(1.0, self.ритъм + 0.15 * добре)
            self.мляко = min(1.0, self.мляко + 0.045 * добре / self.по_бавно)
            self.капки.append([154 + (6 if страна == "д" else -6), 104.0, 0.0])

    def _обнови_доене(self, dt):
        self.общо += dt
        for к in self.капки:
            к[1] += 90 * dt
            к[2] += dt
        self.капки = [к for к in self.капки if к[2] < 0.35]
        if self.мляко >= 1.0 or self.общо > 16:
            self._готово(self.мляко)

    def _пиксели_доене(self, п):
        pygame.draw.rect(п, (90, 140, 60), (0, 130, 320, 50))                   # тревата
        pygame.draw.ellipse(п, (40, 30, 30), (60, 30, 200, 90))                  # кравата отстрани
        pygame.draw.ellipse(п, (245, 242, 236), (62, 32, 196, 86))
        for (x, y, r) in ((110, 60, 18), (190, 75, 14), (150, 48, 10)):
            pygame.draw.circle(п, (70, 58, 52), (x, y), r)
        for x in (90, 110, 210, 230):
            pygame.draw.rect(п, (40, 30, 30), (x - 6, 100, 12, 34))
            pygame.draw.rect(п, (240, 236, 228), (x - 5, 100, 10, 32))
        pygame.draw.ellipse(п, (40, 30, 30), (136, 92, 36, 22))                  # вимето
        pygame.draw.ellipse(п, (240, 170, 184), (137, 93, 34, 20))
        for x in (146, 162):
            pygame.draw.rect(п, (210, 130, 150), (x - 2, 110, 5, 8))
        pygame.draw.ellipse(п, (40, 30, 30), (20, 30, 56, 48))                   # главата
        pygame.draw.ellipse(п, (245, 242, 236), (22, 32, 52, 44))
        pygame.draw.ellipse(п, (240, 170, 184), (24, 56, 26, 18))
        pygame.draw.rect(п, (40, 40, 48), (132, 136, 44, 34))                    # кофата
        pygame.draw.rect(п, (170, 176, 188), (134, 138, 40, 30))
        h = int(28 * self.мляко)
        pygame.draw.rect(п, (250, 250, 245), (135, 167 - h, 38, h))
        for (x, y, _) in self.капки:
            pygame.draw.rect(п, (255, 255, 255), (int(x), int(y), 2, 4))
        self._лента(п, 272, 34, 14, 96, self.ритъм, (0.4, 1.0), (236, 226, 204))

    def _надписи_доене(self, екран):
        self._текст(екран, "A  D", 26, ЗЛАТНО, (279 * ПИКСЕЛ, 22 * ПИКСЕЛ), True)
        self._текст(екран, "ритъм", 20, СВЕТЛО, (279 * ПИКСЕЛ, 140 * ПИКСЕЛ))
        self._текст(екран, "Мляко: %d%%" % (self.мляко * 100), 28, ЗЛАТНО, (ШИР // 2, 90), True)

    def _рисувай_доене(self, екран):
        self._прости_пиксели(екран, self._пиксели_доене, self._надписи_доене)

    # ---------- камбаните: повтори мелодията ----------
    КАМБАНИ = ((pygame.K_a, "A", 0), (pygame.K_s, "S", 1), (pygame.K_d, "D", 2))

    def _начало_камбани(self):
        self.кръг, self.кръгове = 0, 3
        self.мелодия, self.натиснато, self.точки = [], [], []
        self.люлка = [0.0, 0.0, 0.0]
        self._нова_мелодия()
        self.обяснение = ["Камбаните", "Слушай: камбаните бият мелодия. После я повтори.",
                          "A = малката, S = средната, D = голямата камбана. 3 мелодии."]

    def _нова_мелодия(self):
        дължина = 3 + self.кръг * 2
        self.мелодия = [self.сл.randrange(3) for _ in range(дължина)]
        self.натиснато, self.показва, self.показ_от = [], True, self.време()

    def _удари(self, к):
        self.люлка[к] = 1.0

    def _клавиш_камбани(self, с):
        if с.type != pygame.KEYDOWN or self.показва:
            return
        for клавиш, _, к in self.КАМБАНИ:
            if с.key == клавиш:
                self._удари(к)
                self.натиснато.append(к)
                if len(self.натиснато) == len(self.мелодия):
                    вярно = sum(1 for а, б in zip(self.натиснато, self.мелодия) if а == б) / len(self.мелодия)
                    self.точки.append(вярно)
                    self.кръг += 1
                    if self.кръг >= self.кръгове:
                        self._готово(sum(self.точки) / len(self.точки))
                    else:
                        self._нова_мелодия()
                return

    def _обнови_камбани(self, dt):
        self.люлка = [max(0.0, л - dt * 1.5) for л in self.люлка]
        if self.показва:
            t = self.време() - self.показ_от - 0.8
            и = int(t / 0.55)
            if t >= 0 and abs(t - и * 0.55) < dt * 1.5 and и < len(self.мелодия):
                self._удари(self.мелодия[и])
            if t > len(self.мелодия) * 0.55 + 0.3:
                self.показва = False

    def _пиксели_камбани(self, п):
        pygame.draw.rect(п, (90, 60, 36), (40, 30, 240, 8))                     # гредата
        for и, (x, r) in enumerate(((100, 14), (160, 20), (220, 12))):
            ъгъл = math.sin(self.люлка[и] * 9) * self.люлка[и] * 0.5
            cx, cy = x + math.sin(ъгъл) * 30, 38 + math.cos(ъгъл) * 30
            pygame.draw.line(п, (40, 30, 20), (x, 38), (cx, cy), 2)
            точки = [(cx - r * 0.5, cy - 4), (cx + r * 0.5, cy - 4), (cx + r, cy + r * 1.6), (cx - r, cy + r * 1.6)]
            pygame.draw.polygon(п, (60, 40, 10), [(x2, y2 + 1) for x2, y2 in точки])
            pygame.draw.polygon(п, (224, 168, 58), точки)
            pygame.draw.line(п, (255, 230, 150), (cx - r * 0.4, cy), (cx - r * 0.7, cy + r * 1.3))
            pygame.draw.circle(п, (60, 50, 50), (int(cx), int(cy + r * 1.6 + 3)), 3)
            if self.люлка[и] > 0.6:
                pygame.draw.circle(п, (255, 240, 180), (int(cx), int(cy + r)), int(r * 2.2), 1)
        for и in range(len(self.мелодия)):                                       # точки: колко е повторено
            цвят = (255, 214, 90) if и < len(self.натиснато) else (90, 70, 50)
            pygame.draw.circle(п, цвят, (160 - len(self.мелодия) * 6 + и * 12, 150), 4)

    def _надписи_камбани(self, екран):
        for _, буква, и in self.КАМБАНИ:
            self._текст(екран, буква, 30, ЗЛАТНО, ((100, 160, 220)[и] * ПИКСЕЛ, 128 * ПИКСЕЛ), True)
        if self.етап == "игра":
            self._текст(екран, "Слушай..." if self.показва else "Повтори!  (мелодия %d/%d)" % (self.кръг + 1, self.кръгове),
                        30, БЯЛО, (ШИР // 2, 90), True)

    def _рисувай_камбани(self, екран):
        self._прости_пиксели(екран, self._пиксели_камбани, self._надписи_камбани)

    # ---------- свещите: да не угасне нито една ----------
    def _начало_свещи(self):
        self.свещи = [{"гори": True, "трепти": -1.0} for _ in range(5)]
        self.угаснали, self.спасени, self.общо = 0, 0, 0.0
        self.обяснение = ["Свещите", "Отецът пали свещите. Когато някоя затрепти,",
                          "натисни числото ѝ (1-5), за да я опазиш от течението. 25 секунди."]

    def _клавиш_свещи(self, с):
        if с.type != pygame.KEYDOWN:
            return
        for и in range(5):
            if с.key in (getattr(pygame, "K_%d" % (и + 1)), getattr(pygame, "K_KP%d" % (и + 1))):
                св = self.свещи[и]
                if св["трепти"] >= 0:
                    св["трепти"] = -1.0
                    self.спасени += 1
                elif not св["гори"]:
                    св["гори"] = True                                         # отново запалена (без точка)

    def _обнови_свещи(self, dt):
        self.общо += dt
        for св in self.свещи:
            if св["трепти"] >= 0:
                св["трепти"] += dt
                if св["трепти"] > 1.6 / self.по_бавно:
                    св["гори"], св["трепти"] = False, -1.0
                    self.угаснали += 1
            elif св["гори"] and self.сл.random() < dt * 0.22:
                св["трепти"] = 0.0
        if self.общо >= 25:
            всичко = self.спасени + self.угаснали
            self._готово(self.спасени / всичко if всичко else 1.0)

    def _пиксели_свещи(self, п):
        pygame.draw.rect(п, (40, 30, 26), (0, 0, 320, 180))
        pygame.draw.ellipse(п, (120, 90, 30), (40, 110, 240, 30))               # свещникът с пясък
        pygame.draw.ellipse(п, (220, 196, 140), (48, 112, 224, 20))
        pygame.draw.rect(п, (190, 150, 50), (150, 136, 20, 40))
        for и, св in enumerate(self.свещи):
            x = 70 + и * 45
            pygame.draw.rect(п, (60, 50, 40), (x - 4, 64, 9, 58))
            pygame.draw.rect(п, (250, 240, 210), (x - 3, 65, 7, 56))
            if св["гори"]:
                трепти = св["трепти"] >= 0
                наклон = int(math.sin(self.общо * 30) * 4) if трепти else int(math.sin(self.общо * 3 + и) * 1)
                височина = 10 if not трепти else 6
                pygame.draw.circle(п, (255, 200, 90), (x + наклон // 2, 55), 9 if not трепти else 6)
                pygame.draw.ellipse(п, (255, 150, 40), (x - 3 + наклон, 52 - височина, 7, височина + 6))
                pygame.draw.ellipse(п, (255, 250, 200), (x - 1 + наклон, 56 - височина // 2, 3, височина // 2 + 3))
            else:
                pygame.draw.line(п, (130, 130, 140), (x, 58), (x + 3, 44))       # пушек
        self._лента(п, 290, 34, 12, 80, max(0.0, 1 - self.общо / 25), (0.0, 1.0), (240, 200, 120))

    def _надписи_свещи(self, екран):
        for и in range(5):
            self._текст(екран, str(и + 1), 30, ЗЛАТНО, ((70 + и * 45) * ПИКСЕЛ, 150 * ПИКСЕЛ), True)
        self._текст(екран, "Опазени: %d   Угаснали: %d" % (self.спасени, self.угаснали), 26, БЯЛО, (ШИР // 2, 90), True)

    def _рисувай_свещи(self, екран):
        self._прости_пиксели(екран, self._пиксели_свещи, self._надписи_свещи)

    # ---------- кръщенето: водата в купела да е топла ----------
    def _начало_кръщене(self):
        self.темп, self.добре, self.общо = 0.3, 0.0, 0.0
        self.обяснение = ["Кръщене", "Водата в купела трябва да е топла - не студена, не гореща.",
                          "W = топла вода, S = студена. Дръж я в зеленото 8 секунди."]

    def _клавиш_кръщене(self, с):
        pass

    def _обнови_кръщене(self, dt):
        к = pygame.key.get_pressed()
        if к[pygame.K_w] or к[pygame.K_UP]:
            self.темп += 0.35 * dt
        if к[pygame.K_s] or к[pygame.K_DOWN]:
            self.темп -= 0.35 * dt
        self.темп += self.сл.uniform(-0.12, 0.08) * dt * self.по_бавно         # изстива, мени се
        self.темп = max(0.0, min(1.0, self.темп))
        self.общо += dt
        if 0.5 <= self.темп <= 0.68:
            self.добре += dt
        if self.добре >= 8 or self.общо > 20:
            self._готово(min(1.0, self.добре / 8) * (1.0 if self.общо < 14 else 0.8))

    def _пиксели_кръщене(self, п):
        pygame.draw.rect(п, (70, 62, 56), (0, 0, 320, 180))
        pygame.draw.rect(п, (120, 110, 100), (0, 140, 320, 40))
        pygame.draw.rect(п, (150, 144, 132), (140, 110, 40, 34))                # купелът
        pygame.draw.ellipse(п, (40, 36, 32), (88, 70, 144, 60))
        pygame.draw.ellipse(п, (200, 194, 180), (90, 72, 140, 56))
        т = self.темп
        вода = (int(80 + 170 * т), int(150 + 20 * (1 - abs(т - 0.6))), int(230 - 180 * т))
        pygame.draw.ellipse(п, вода, (100, 78, 120, 30))
        if т > 0.6:
            for и in range(int((т - 0.6) * 20)):
                x = 110 + (и * 23) % 100
                pygame.draw.circle(п, (240, 240, 245), (x, 70 - (int(self.общо * 20 + и * 7) % 20)), 3)
        pygame.draw.ellipse(п, (255, 230, 200), (146, 82, 28, 14))              # бебето в бяла пелена
        pygame.draw.circle(п, (250, 210, 180), (170, 86), 6)
        self._лента(п, 34, 34, 14, 96, т, (0.5, 0.68), (240, 120, 60))
        self._лента(п, 272, 34, 14, 96, min(1.0, self.добре / 8), (0.99, 1.0), (120, 200, 240))

    def _надписи_кръщене(self, екран):
        self._текст(екран, "W", 26, ЗЛАТНО, (41 * ПИКСЕЛ, 22 * ПИКСЕЛ), True)
        self._текст(екран, "S", 26, ЗЛАТНО, (41 * ПИКСЕЛ, 140 * ПИКСЕЛ), True)
        self._текст(екран, "готово", 18, СВЕТЛО, (279 * ПИКСЕЛ, 140 * ПИКСЕЛ))
        if self.етап == "игра":
            self._текст(екран, "студена" if self.темп < 0.5 else "гореща!" if self.темп > 0.68 else "топла - добре",
                        28, БЯЛО, (ШИР // 2, 90), True)

    def _рисувай_кръщене(self, екран):
        self._прости_пиксели(екран, self._пиксели_кръщене, self._надписи_кръщене)

    # ---------- венчавката: Исаевото хоро около аналоя ----------
    def _начало_венчавка(self):
        self.стъпки, self.нужни, self.ъгъл, self.общо = 0, 24, 0.0, 0.0
        self.удари, self.последен = [], None
        self.обяснение = ["Венчавка", "Младоженците обикалят три пъти около аналоя след отеца.",
                          "A и D един след друг - точно когато камбанката светне (в ритъм)."]

    def _клавиш_венчавка(self, с):
        if с.type != pygame.KEYDOWN or с.key not in (pygame.K_a, pygame.K_d):
            return
        страна = "л" if с.key == pygame.K_a else "д"
        if страна == self.последен:
            return
        self.последен = страна
        такт = 0.7
        фаза = (self.общо % такт) / такт
        точно = 1 - min(фаза, 1 - фаза) * 2                                   # 1 = точно в ритъм
        self.удари.append(точно)
        self.стъпки += 1
        self.ъгъл += 2 * math.pi * 3 / self.нужни
        if self.стъпки >= self.нужни:
            self._готово(min(1.0, (sum(self.удари) / len(self.удари)) * 1.25))

    def _обнови_венчавка(self, dt):
        self.общо += dt
        if self.общо > 40:
            self._готово(0.3 * self.стъпки / self.нужни)

    def _пиксели_венчавка(self, п):
        pygame.draw.rect(п, (70, 62, 56), (0, 0, 320, 180))
        pygame.draw.rect(п, (120, 100, 80), (0, 130, 320, 50))
        cx, cy = 160, 110
        pygame.draw.ellipse(п, (90, 70, 50), (cx - 70, cy - 18, 140, 36), 1)    # пътят около аналоя
        pygame.draw.rect(п, (40, 30, 20), (cx - 10, cy - 30, 20, 34))           # аналоят
        pygame.draw.rect(п, (200, 150, 70), (cx - 9, cy - 29, 18, 32))
        pygame.draw.polygon(п, (230, 60, 50), [(cx - 12, cy - 30), (cx + 12, cy - 30), (cx + 8, cy - 36), (cx - 8, cy - 36)])
        for и, (цвят, отм) in enumerate((((40, 40, 50), 0.0), ((255, 255, 255), -0.55), ((50, 60, 90), -0.95))):
            а = self.ъгъл + отм
            x, y = cx + 70 * math.cos(а), cy + 18 * math.sin(а)
            pygame.draw.ellipse(п, (20, 16, 14), (x - 7, y - 26, 14, 28))
            pygame.draw.ellipse(п, цвят, (x - 6, y - 25, 12, 26))
            pygame.draw.circle(п, (240, 200, 170), (int(x), int(y - 28)), 5)
            if и > 0:
                pygame.draw.circle(п, (240, 200, 60), (int(x), int(y - 34)), 3)    # венчалните корони
        фаза = (self.общо % 0.7) / 0.7
        светне = фаза < 0.18 or фаза > 0.82
        pygame.draw.circle(п, (255, 230, 120) if светне else (90, 70, 40), (290, 40), 10)
        self._лента(п, 284, 60, 12, 80, self.стъпки / self.нужни, (0.99, 1.0), (240, 200, 120))

    def _надписи_венчавка(self, екран):
        self._текст(екран, "A  D", 26, ЗЛАТНО, (290 * ПИКСЕЛ, 160 * ПИКСЕЛ), True)
        self._текст(екран, "Обиколка %d от 3" % min(3, 1 + self.стъпки * 3 // self.нужни), 28, БЯЛО, (ШИР // 2, 90), True)

    def _рисувай_венчавка(self, екран):
        self._прости_пиксели(екран, self._пиксели_венчавка, self._надписи_венчавка)

    # ---------- боядисване на яйца (Великден) ----------
    ЦВЕТОВЕ_БОЯ = ((pygame.K_1, "червено", (220, 40, 36)), (pygame.K_2, "жълто", (240, 200, 50)),
                   (pygame.K_3, "синьо", (60, 120, 210)), (pygame.K_4, "зелено", (70, 170, 70)))

    def _начало_боядисване(self):
        брой = max(2, min(6, int(self.настр.get("брой", 4))))
        self.поръчка = [0] + [self.сл.randrange(1, 4) for _ in range(брой - 1)]   # първото яйце е червено
        self.яйца, self.текущо, self.боя, self.цвят_сега, self.общо = [], 0, 0.0, None, 0.0
        self.точки = []
        self.обяснение = ["Боядисване на яйца", "По реда горе: натисни цвета (1-4) и задръж, докато яйцето",
                          "стане тъмно колкото на образеца; пусни в зеленото. Първото е червено!"]

    def _клавиш_боядисване(self, с):
        if self.текущо >= len(self.поръчка):
            return
        if с.type == pygame.KEYDOWN:
            for и, (клавиш, _, _) in enumerate(self.ЦВЕТОВЕ_БОЯ):
                if с.key == клавиш:
                    self.цвят_сега, self.боя = и, 0.0
        elif с.type == pygame.KEYUP and self.цвят_сега is not None:
            for и, (клавиш, _, _) in enumerate(self.ЦВЕТОВЕ_БОЯ):
                if с.key == клавиш and и == self.цвят_сега:
                    правилен = и == self.поръчка[self.текущо]
                    точно = 1.0 if 0.6 <= self.боя <= 0.85 else 0.6 if 0.45 <= self.боя <= 0.95 else 0.25
                    self.точки.append(точно if правилен else 0.1)
                    self.яйца.append((и, min(1.0, self.боя)))
                    self.текущо += 1
                    self.цвят_сега = None
                    if self.текущо >= len(self.поръчка):
                        self._готово(sum(self.точки) / len(self.точки))

    def _обнови_боядисване(self, dt):
        self.общо += dt
        if self.цвят_сега is not None:
            self.боя = min(1.2, self.боя + dt * 0.45 * self.по_бавно)

    def _цвят_яйце(self, и, сила):
        ц = self.ЦВЕТОВЕ_БОЯ[и][2]
        if сила <= 1:
            return tuple(int(255 + (к - 255) * сила) for к in ц)
        return tuple(int(к * max(0.3, 1 - (сила - 1) * 2.5)) for к in ц)     # прекалено дълго: потъмнява

    def _яйце(self, п, x, y, цвят):
        pygame.draw.ellipse(п, (40, 30, 24), (x - 9, y - 12, 18, 24))
        pygame.draw.ellipse(п, цвят, (x - 8, y - 11, 16, 22))
        pygame.draw.ellipse(п, tuple(min(255, к + 50) for к in цвят), (x - 5, y - 8, 5, 7))

    def _пиксели_боядисване(self, п):
        pygame.draw.rect(п, (90, 60, 36), (0, 120, 320, 60))
        for и, ц in enumerate(self.поръчка):                                   # образецът горе
            self._яйце(п, 40 + и * 26, 30, self._цвят_яйце(ц, 0.72))
        for и, (_, _, ц) in enumerate(self.ЦВЕТОВЕ_БОЯ):                      # купичките с боя
            x = 70 + и * 60
            pygame.draw.ellipse(п, (40, 30, 24), (x - 22, 118, 44, 22))
            pygame.draw.ellipse(п, (240, 236, 228), (x - 21, 119, 42, 20))
            pygame.draw.ellipse(п, ц, (x - 17, 121, 34, 10))
        if self.цвят_сега is not None:                                        # яйцето в боята
            x = 70 + self.цвят_сега * 60
            self._яйце(п, x, 112, self._цвят_яйце(self.цвят_сега, self.боя))
        elif self.текущо < len(self.поръчка):
            self._яйце(п, 290, 100, (255, 252, 244))
        for и, (ц, сила) in enumerate(self.яйца):                             # готовите в кошничката
            self._яйце(п, 40 + и * 26, 80, self._цвят_яйце(ц, сила))
        if self.текущо < len(self.поръчка):
            pygame.draw.rect(п, (255, 230, 120), (28 + self.текущо * 26, 46, 24, 2))
        self._лента(п, 300, 20, 10, 80, min(1.0, self.боя / 1.2), (0.6 / 1.2, 0.85 / 1.2), (200, 120, 200))

    def _надписи_боядисване(self, екран):
        for и, (_, име, _) in enumerate(self.ЦВЕТОВЕ_БОЯ):
            self._текст(екран, "%d %s" % (и + 1, име), 20, ЗЛАТНО, ((70 + и * 60) * ПИКСЕЛ, 150 * ПИКСЕЛ), True)
        self._текст(екран, "образец", 18, СВЕТЛО, (40 * ПИКСЕЛ - 20, 10 * ПИКСЕЛ))

    def _рисувай_боядисване(self, екран):
        self._прости_пиксели(екран, self._пиксели_боядисване, self._надписи_боядисване)


# ---------- рецептите: ястието се готви на стъпки ----------
def рецепти():
    път = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "recipes.json")
    try:
        return json.load(open(път, encoding="utf-8"))["рецепти"]
    except (OSError, ValueError, KeyError):
        return {}


class Готвене:
    """Избираш ястие, после го готвиш по рецептата: всяка стъпка е мини игра.
    Играта я вика: клавиш(събитие), обнови(), нарисувай(екран).
    Когато край е True: резултат = {"item", "quality"} (средното от стъпките) или None (отказ)."""

    def __init__(self, избор, име="", изглед=None, рецепти_=None):
        if isinstance(избор, str):                                  # стар начин: едно ястие
            избор = [(избор, име or избор, False)]
        self.избор = [(к, и or к, искано) for (к, и, искано) in избор]
        self.рецепти = рецепти_ if рецепти_ is not None else рецепти()
        self.изглед = изглед
        self.избран = 0
        self.край, self.резултат = False, None
        self.стъпка, self.качества = None, []
        self.съдържание = {"тенджера": [], "тиган": [], "печено": 0.0}
        self.етап = "избор"
        self._шрифтове = {}
        self.арт = зареди_арт()
        self.икони = {}
        for к, _, _ in self.избор:
            път = tiles.намери_картинка(os.path.join("items", к + ".png"))
            if път:
                self.икони[к] = pygame.transform.scale(pygame.image.load(път), (96, 96))
        if len(self.избор) == 1:
            self._започни()

    # стъпките на избраното ястие
    def рецепта(self, ключ=None):
        ключ = ключ or self.избор[self.избран][0]
        return self.рецепти.get(ключ) or [{"игра": None, "заглавие": "Приготви"}]

    @property
    def предмет(self):
        return self.избор[self.избран][0]

    @property
    def вид(self):
        return self.стъпка.вид if self.стъпка else self.етап

    def _започни(self):
        self.етап, self.номер = "стъпки", 0
        self._нова_стъпка()

    def _нова_стъпка(self):
        стъпки = self.рецепта()
        с = стъпки[self.номер]
        име = "%s · %d/%d" % (self.избор[self.избран][1], self.номер + 1, len(стъпки))
        self.стъпка = Стъпка(self.предмет, име, self.изглед, с.get("игра"), с, с.get("заглавие"), self.съдържание)

    def клавиш(self, с):
        if self.етап == "избор":
            if с.type != pygame.KEYDOWN:
                return
            if с.key == pygame.K_ESCAPE:
                self.край = True
            elif с.key in (pygame.K_LEFT, pygame.K_a, pygame.K_UP):
                self.избран = (self.избран - 1) % len(self.избор)
            elif с.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN):
                self.избран = (self.избран + 1) % len(self.избор)
            elif с.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e, pygame.K_s):
                self._започни()
        elif self.етап == "стъпки":
            self.стъпка.клавиш(с)
            if self.стъпка.край and self.стъпка.резултат is None:     # Esc: отказ от цялото ястие
                self.край, self.резултат = True, None
        elif с.type == pygame.KEYDOWN and с.key == pygame.K_ESCAPE and self.етап == "готово":
            self._приключи()

    def _приключи(self):
        self.край = True
        self.резултат = {"item": self.предмет, "quality": round(sum(self.качества) / len(self.качества), 2)}

    def обнови(self):
        if self.етап == "стъпки":
            self.стъпка.обнови()
            if self.стъпка.край:
                if self.стъпка.резултат is None:                     # Esc: отказ от цялото ястие
                    self.край, self.резултат = True, None
                    return
                self.качества.append(self.стъпка.резултат["quality"])
                self.номер += 1
                if self.номер < len(self.рецепта()):
                    self._нова_стъпка()
                else:
                    self.етап, self.от = "готово", time.perf_counter()
        elif self.етап == "готово" and time.perf_counter() - self.от > 2.5:
            self._приключи()

    def шрифт(self, размер, удебелен=False):
        if (размер, удебелен) not in self._шрифтове:
            self._шрифтове[(размер, удебелен)] = pygame.font.SysFont("arial", размер, bold=удебелен)
        return self._шрифтове[(размер, удебелен)]

    def _текст(self, екран, текст, размер, цвят, център, удебелен=False):
        т = self.шрифт(размер, удебелен).render(текст, True, цвят)
        екран.blit(т, т.get_rect(center=център))

    def _фон(self, екран):
        if self.арт:
            екран.blit(pygame.transform.scale(self.арт["kuhnya_fon"][0], (ШИР, ВИС)), (0, 0))
        else:
            екран.fill((80, 52, 34))
        тъмно = pygame.Surface((ШИР, ВИС), pygame.SRCALPHA)
        тъмно.fill((16, 10, 6, 170))
        екран.blit(тъмно, (0, 0))

    def нарисувай(self, екран):
        if self.етап == "стъпки":
            self.стъпка.нарисувай(екран)
            return
        self._фон(екран)
        if self.етап == "избор":
            self._текст(екран, "Какво ще готвиш?", 36, ЗЛАТНО, (ШИР // 2, 44), True)
            н = len(self.избор)
            ш = min(280, (ШИР - 60) // н - 20)
            for и, (ключ, име, искано) in enumerate(self.избор):
                r = pygame.Rect(0, 0, ш, 390)
                r.center = (ШИР // 2 + int((и - (н - 1) / 2) * (ш + 20)), 290)
                pygame.draw.rect(екран, (240, 226, 190), r, border_radius=12)     # рецептата като лист
                pygame.draw.rect(екран, ЗЛАТНО if и == self.избран else (110, 70, 40), r, 5 if и == self.избран else 2, border_radius=12)
                if ключ in self.икони:
                    екран.blit(self.икони[ключ], self.икони[ключ].get_rect(center=(r.centerx, r.top + 62)))
                self._текст(екран, име, 26, (90, 40, 20), (r.centerx, r.top + 126), True)
                if искано:
                    self._текст(екран, "гостите чакат!", 18, (190, 50, 30), (r.centerx, r.top + 152), True)
                стъпки = self.рецепта(ключ)
                ред = min(28, 196 // len(стъпки))
                for к, с in enumerate(стъпки):
                    self._текст(екран, "%d. %s" % (к + 1, с.get("заглавие", с.get("игра", ""))), 17 if ред >= 24 else 15,
                                (70, 50, 34), (r.centerx, r.top + 180 + к * ред))
            self._текст(екран, "A / D  избери     S = готви     Esc = отказ", 20, СВЕТЛО, (ШИР // 2, 515))
        else:                                                               # готово: всички стъпки
            качество = sum(self.качества) / len(self.качества)
            текст, звезди = оценка(качество)
            self._текст(екран, self.избор[self.избран][1], 40, ЗЛАТНО, (ШИР // 2, 110), True)
            for к, (с, q) in enumerate(zip(self.рецепта(), self.качества)):
                з = оценка(q)[1]
                ред = min(36, 210 // len(self.качества))
                self._текст(екран, "%d. %s   %s" % (к + 1, с.get("заглавие", ""), "★" * з + "☆" * (3 - з)), 22 if ред >= 30 else 18,
                            СВЕТЛО, (ШИР // 2, 165 + к * ред))
            self._текст(екран, текст, 44, ЗЛАТНО, (ШИР // 2, 400), True)
            self._текст(екран, "★" * звезди + "☆" * (3 - звезди), 50, (255, 210, 60), (ШИР // 2, 460), True)
