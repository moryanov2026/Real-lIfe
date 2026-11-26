# Real Life - МИНИИГРА "СВИРЕНЕ" (ритъм игра като игрите с китара). Правилата: rules/krachma.md, 10а.
# Отваря се от играта, когато музикантът натисне E. Може да се пусне и сама:  python svirene.py
#
# Платно 960x540 (на Full HD = точно x2). Нотите падат по лентите; когато стигнат линията,
# натискаш клавиша на лентата: D F J K, Space (кавалът има 3 ленти: D F J).
#   Ниво Лесно / Средно / Трудно (← → при избора на песен): колко бързо падат нотите и колко са.
#   Перфектно = до 50-70 мс от нотата, Добре = до 100-150 мс (според нивото), иначе Пропуск.
#   Комбо: 10 поредни = x2, 20 = x3, 30 = x4. Резултатът (0-100 %) решава бакшиша.
# Песните са в data/songs/*.json. Звукът (кавал и тъпан) се прави от програмата,
# докато класът запише истински: assets/music/<песен>.ogg ще се пуска вместо него.
# Ако има и <песен>_melodiya.ogg + <песен>_fon.ogg (прави ги pesen.bat), съпроводът свири винаги,
# а мелодията се чува само докато уцелваш: пропуснеш ли, заглъхва (като в игрите с китара).
# Натиснеш ли без нота - кавалът изсвирва фалшиво.
import array
import glob
import json
import math
import os
import random

import pygame

ПАПКА = os.path.dirname(os.path.abspath(__file__))
ПАПКА_ПЕСНИ = os.path.join(ПАПКА, "data", "songs")
ПАПКА_МУЗИКА = os.path.join(ПАПКА, "assets", "music")
ШИР, ВИС = 960, 540
ЛИНИЯ_Y = 444                       # линията за удар (средата на бутоните долу)
# Нива на трудност (избират се с ← → преди песента):
#   скорост = пиксела в секунда, с които падат нотите; разстояние = най-малко секунди между две ноти
#   (по-близките се махат); перфектно/добре = колко може да се сбърка (секунди); бакшиш = част от бакшиша
НИВА = [
    {"име": "Лесно",  "скорост": 170, "разстояние": 0.45, "перфектно": 0.070, "добре": 0.150, "бакшиш": 0.5},
    {"име": "Средно", "скорост": 240, "разстояние": 0.30, "перфектно": 0.060, "добре": 0.120, "бакшиш": 0.75},
    {"име": "Трудно", "скорост": 330, "разстояние": 0.0,  "перфектно": 0.050, "добре": 0.100, "бакшиш": 1.0},
]
КЛАВИШИ = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k, pygame.K_SPACE]
ИМЕНА_КЛАВИШИ = ["D", "F", "J", "K", "␣"]
ЦВЕТОВЕ = [(214, 58, 46), (236, 184, 52), (72, 168, 88), (66, 120, 214), (170, 90, 190)]
ЧЕСТОТА_ЗВУК = 22050


# ---------- звук: кавал и тъпан, направени от програмата ----------
def _честота():
    """Звуковата карта може вече да е пусната с други настройки (pygame.init() я пуска с 44100 стерео)."""
    return pygame.mixer.get_init()[0] if pygame.mixer.get_init() else ЧЕСТОТА_ЗВУК


def _звук(проби):
    """Пробите са моно, 16 бита; повтаряме ги за всеки канал и ги правим в нужния формат."""
    честота, формат, канали = pygame.mixer.get_init()
    if формат in (32, -32):                       # звукова карта с дробни числа
        данни = array.array("f", (п / 32768.0 for п in проби for _ in range(канали)))
    else:
        данни = array.array("h", (п for п in проби for _ in range(канали)))
    return pygame.mixer.Sound(buffer=данни.tobytes())


def кавал_тон(честота, дълж=0.42):
    сл = random.Random(int(честота))
    чз = _честота()
    n = int(чз * дълж)
    проби = []
    for i in range(n):
        t = i / чз
        обвивка = min(1.0, t / 0.035) * (1.0 if t < дълж - 0.09 else max(0.0, (дълж - t) / 0.09))
        f = честота * (1 + 0.004 * math.sin(2 * math.pi * 5.5 * t))          # леко вибрато
        ф = 2 * math.pi * f * t
        стойност = math.sin(ф) + 0.28 * math.sin(2 * ф) + 0.1 * math.sin(3 * ф)
        стойност += (сл.random() - 0.5) * 0.35                               # дъх (кавалът "шуми")
        проби.append(int(7000 * обвивка * стойност))
    return _звук(проби)


def фалшива_нота():
    """Кавалът "изпищява": два разстроени тона, които падат надолу, и дъх."""
    сл = random.Random(9)
    чз = _честота()
    n = int(чз * 0.22)
    проби, ф1, ф2 = [], 0.0, 0.0
    for i in range(n):
        t = i / чз
        f = 980 - 900 * t
        ф1 += 2 * math.pi * f / чз
        ф2 += 2 * math.pi * f * 1.06 / чз
        обвивка = min(1.0, t / 0.01) * math.exp(-t * 9)
        проби.append(int(5000 * обвивка * (math.sin(ф1) + math.sin(ф2) + (сл.random() - 0.5) * 0.8)))
    return _звук(проби)


def тъпан(силен):
    сл = random.Random(3 if силен else 4)
    дълж = 0.30 if силен else 0.08
    чз = _честота()
    n = int(чз * дълж)
    проби, фаза = [], 0.0
    for i in range(n):
        t = i / чз
        if силен:                                   # "бум": нисък тон, който пада
            f = 45 + 75 * math.exp(-t * 18)
            фаза += 2 * math.pi * f / чз
            стойност = math.sin(фаза) * math.exp(-t * 9) * 1.0 + (сл.random() - 0.5) * math.exp(-t * 60) * 0.6
            проби.append(int(9000 * стойност))
        else:                                       # "чук": пръчката
            проби.append(int(3500 * (сл.random() - 0.5) * math.exp(-t * 70)))
    return _звук(проби)


# ---------- песни ----------
def песни(инструмент=None):
    резултат = []
    for път in sorted(glob.glob(os.path.join(ПАПКА_ПЕСНИ, "*.json"))):
        with open(път, encoding="utf-8") as f:
            п = json.load(f)
        п["file"] = os.path.splitext(os.path.basename(път))[0]
        if инструмент is None or п.get("instrument") == инструмент:
            резултат.append(п)
    return резултат


def мин_сек(s):
    s = max(0, int(s))
    return "%d:%02d" % (s // 60, s % 60)


class Нота:
    __slots__ = ("t", "лента", "степен", "оценка")

    def __init__(self, t, лента, степен):
        self.t, self.лента, self.степен, self.оценка = t, лента, степен, None


class Свирене:
    """Самата миниигра. игра.обнови() и игра.нарисувай(екран 960x540) всеки кадър;
    игра.клавиш(събитие). Когато свърши: self.край = True и self.резултат = {...}."""

    def __init__(self, инструмент="kaval", шрифтове=None, звук=True):
        self.инструмент = инструмент
        self.списък = песни(инструмент) or песни()
        self.избрана = 0
        self.ниво = 0                   # 0 = Лесно
        self.етап = "избор"            # избор -> броене -> свири -> резултат
        self.край = False
        self.резултат = None
        self.ш = шрифтове or {}
        self.звук = звук and self._пусни_звук()
        self.картинки = self._картинки()
        self.натиснати = set()
        self.искри = []                 # (лента, време)
        self.надпис = None              # (текст, цвят, време)

    # ---------- подготовка ----------
    def _пусни_звук(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(ЧЕСТОТА_ЗВУК, -16, 1, 512)
            pygame.mixer.set_num_channels(24)
            return True
        except pygame.error:
            return False

    def _картинки(self):
        """Ученическите картинки от assets/music/ (ако ги има)."""
        к = {}
        for име in ("kaval", "fon_svirene", "grif_kaval", "muzikant_golyam",
                    "nota_0", "nota_1", "nota_2", "nota_3", "nota_4"):
            път = os.path.join(ПАПКА_МУЗИКА, име + ".png")
            if os.path.exists(път):
                к[име] = pygame.image.load(път)
                if pygame.display.get_surface():
                    к[име] = к[име].convert_alpha()
        return к

    def шрифт(self, размер, удебелен=False):
        ключ = (размер, удебелен)
        if ключ not in self.ш:
            self.ш[ключ] = pygame.font.SysFont("arial", размер, bold=удебелен)
        return self.ш[ключ]

    def започни(self):
        п = self.списък[self.избрана]
        self.песен = п
        self.ленти = int(п.get("lanes", 3))
        н_ниво = НИВА[self.ниво]
        self.скорост = н_ниво["скорост"]
        self.ПЕРФЕКТНО, self.ДОБРЕ = н_ниво["перфектно"], н_ниво["добре"]
        self.ноти, последна = [], -9.0
        for н in п["notes"]:                     # на по-лесно ниво махаме нотите, които са твърде близо
            if н[0] - последна >= н_ниво["разстояние"]:
                self.ноти.append(Нота(*н))
                последна = н[0]
        self.дължина = float(п.get("length_s", self.ноти[-1].t + 3))
        self.точки = self.комбо = self.най_комбо = 0
        self.брой = {"Перфектно": 0, "Добре": 0, "Пропуск": 0}
        self.следваща = 0                     # първата нота, която още не е минала
        осмина = п["eighth_ms"] / 1000.0
        # ударите на тъпана: в началото на всяка група осмини (силен в началото на такта)
        self.удари, t, бр = [], 0.0, 0
        while t < self.дължина:
            for и, група in enumerate(п["groups"]):
                self.удари.append((t, и == 0))
                t += група * осмина
        self.следващ_удар = 0
        self.звуци = {}
        if self.звук:
            for ст in sorted({н.степен for н in self.ноти}):
                полутон = п["scale"][min(ст, len(п["scale"]) - 1)]
                self.звуци[ст] = кавал_тон(п["base_hz"] * 2 ** (полутон / 12))
            self.бум, self.чук = тъпан(True), тъпан(False)
        self.музика = os.path.join(ПАПКА_МУЗИКА, п["file"] + ".ogg")
        self.има_запис = os.path.exists(self.музика)   # истински запис: без изкуствени тонове и тъпан
        мел = os.path.join(ПАПКА_МУЗИКА, п["file"] + "_melodiya.ogg")
        фон = os.path.join(ПАПКА_МУЗИКА, п["file"] + "_fon.ogg")
        self.части = None                              # (канал съпровод, канал мелодия)
        self.сила_мелодия = self.цел_мелодия = 1.0
        if self.звук:
            self.фалш = фалшива_нота()
        if self.звук and os.path.exists(мел) and os.path.exists(фон):
            self.има_запис = True
            pygame.mixer.set_reserved(2)               # каналите 0 и 1 са само за песента
            звук_фон, звук_мел = pygame.mixer.Sound(фон), pygame.mixer.Sound(мел)
            self.части = (pygame.mixer.Channel(0), pygame.mixer.Channel(1))
        self.етап = "свири"
        self.начало = pygame.time.get_ticks() / 1000.0
        if self.части:
            self.части[0].play(звук_фон)
            self.части[1].play(звук_мел)
        elif self.звук and self.има_запис:
            pygame.mixer.music.load(self.музика)
            pygame.mixer.music.play()

    def време(self):
        return pygame.time.get_ticks() / 1000.0 - self.начало

    # ---------- управление ----------
    def клавиш(self, с):
        if с.type == pygame.KEYUP:
            if с.key in КЛАВИШИ:
                self.натиснати.discard(КЛАВИШИ.index(с.key))
            return
        if с.type != pygame.KEYDOWN:
            return
        if self.етап == "избор":
            if с.key in (pygame.K_UP, pygame.K_w):
                self.избрана = (self.избрана - 1) % len(self.списък)
            elif с.key in (pygame.K_DOWN, pygame.K_s):
                self.избрана = (self.избрана + 1) % len(self.списък)
            elif с.key in (pygame.K_LEFT, pygame.K_a):
                self.ниво = (self.ниво - 1) % len(НИВА)
            elif с.key in (pygame.K_RIGHT, pygame.K_d):
                self.ниво = (self.ниво + 1) % len(НИВА)
            elif с.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.започни()
            elif с.key == pygame.K_ESCAPE:
                self.край, self.резултат = True, None
        elif self.етап == "свири":
            if с.key == pygame.K_ESCAPE:
                self._приключи(прекъснато=True)
            elif с.key in КЛАВИШИ[:self.ленти]:
                лента = КЛАВИШИ.index(с.key)
                self.натиснати.add(лента)
                self._удари(лента, self.време())
        elif self.етап == "резултат":
            if с.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self.край = True

    def _удари(self, лента, t):
        най, най_dt = None, 9
        for н in self.ноти[self.следваща:]:
            if н.t - t > self.ДОБРЕ:
                break
            if н.оценка is None and н.лента == лента and abs(н.t - t) < най_dt:
                най, най_dt = н, abs(н.t - t)
        if най is None or най_dt > self.ДОБРЕ:
            self.комбо = 0                      # натиснато без нота: комбото пада
            self.надпис = ("Пропуск", (200, 80, 70), t)
            self.цел_мелодия = 0.0              # кавалът заглъхва...
            if self.звук:
                self.фалш.play()                # ...и изсвирва фалшиво
            return
        self.цел_мелодия = 1.0                  # уцели: кавалът пак се чува
        най.оценка = "Перфектно" if най_dt <= self.ПЕРФЕКТНО else "Добре"
        self.брой[най.оценка] += 1
        self.комбо += 1
        self.най_комбо = max(self.най_комбо, self.комбо)
        self.точки += (300 if най.оценка == "Перфектно" else 100) * self.множител()
        self.искри.append((лента, t))
        self.надпис = (най.оценка + "!", (255, 230, 120) if най.оценка == "Перфектно" else (190, 230, 255), t)
        if self.звук and not self.има_запис and най.степен in self.звуци:
            self.звуци[най.степен].play()

    def множител(self):
        return min(4, 1 + self.комбо // 10)

    def точност(self):
        минали = sum(1 for н in self.ноти if н.оценка is not None)
        if not минали:
            return 0.0
        return 100.0 * (self.брой["Перфектно"] + 0.6 * self.брой["Добре"]) / минали

    def _приключи(self, прекъснато=False):
        общо = len(self.ноти)
        процент = 100.0 * (self.брой["Перфектно"] + 0.6 * self.брой["Добре"]) / max(1, общо)
        self.резултат = {"song": self.песен["name"], "percent": round(процент, 1), "points": self.точки,
                         "perfect": self.брой["Перфектно"], "good": self.брой["Добре"],
                         "miss": общо - self.брой["Перфектно"] - self.брой["Добре"],
                         "max_combo": self.най_комбо, "stopped": прекъснато,
                         "level": НИВА[self.ниво]["име"], "tip_factor": НИВА[self.ниво]["бакшиш"]}
        if self.звук:
            pygame.mixer.music.stop()
            if self.части:
                for канал in self.части:
                    канал.stop()
                pygame.mixer.set_reserved(0)
        self.етап = "резултат"

    # ---------- всеки кадър ----------
    def обнови(self):
        if self.етап != "свири":
            return
        t = self.време()
        while self.следваща < len(self.ноти) and self.ноти[self.следваща].t < t - self.ДОБРЕ:
            н = self.ноти[self.следваща]
            if н.оценка is None:
                н.оценка = "Пропуск"
                self.брой["Пропуск"] += 1
                self.комбо = 0
                self.цел_мелодия = 0.0          # пропусната нота: кавалът замлъква до следващия удар
            self.следваща += 1
        if self.части:                              # плавно усилване / заглъхване на мелодията
            self.сила_мелодия += (self.цел_мелодия - self.сила_мелодия) * 0.25
            self.части[1].set_volume(max(0.0, self.сила_мелодия))
        if self.звук and not self.има_запис:
            while self.следващ_удар < len(self.удари) and self.удари[self.следващ_удар][0] <= t:
                (self.бум if self.удари[self.следващ_удар][1] else self.чук).play()
                self.следващ_удар += 1
        if t > self.дължина:
            self._приключи()

    # ---------- рисуване ----------
    def нарисувай(self, екран):
        self._фон(екран)
        if self.етап == "избор":
            self._избор(екран)
        elif self.етап == "свири":
            self._свири(екран)
        else:
            self._резултат(екран)

    def _фон(self, екран):
        if "fon_svirene" in self.картинки:
            екран.blit(self.картинки["fon_svirene"], (0, 0))
            return
        for y in range(0, ВИС, 4):                           # топла тъмна кръчма
            к = y / ВИС
            pygame.draw.rect(екран, (int(46 + 30 * к), int(30 + 16 * к), int(26 + 8 * к)), (0, y, ШИР, 4))
        for x in range(0, ШИР, 96):                            # греди
            pygame.draw.rect(екран, (34, 22, 16), (x, 0, 10, ВИС))
        pygame.draw.circle(екран, (70, 48, 30), (ШИР - 40, 30), 110)   # светлина от лампа
        pygame.draw.circle(екран, (88, 60, 34), (ШИР - 40, 30), 55)
        pygame.draw.circle(екран, (255, 210, 120), (ШИР - 40, 30), 8)
        if "kaval" in self.картинки:
            екран.blit(self.картинки["kaval"], (28, 54))
        if "muzikant_golyam" in self.картинки:
            екран.blit(self.картинки["muzikant_golyam"], (130, 220))

    def _текст(self, екран, текст, размер, цвят, център=None, ляво=None, удебелен=False):
        повърхност = self.шрифт(размер, удебелен).render(текст, True, цвят)
        сянка = self.шрифт(размер, удебелен).render(текст, True, (20, 12, 8))
        rect = повърхност.get_rect(center=център) if център else повърхност.get_rect(topleft=ляво)
        екран.blit(сянка, rect.move(2, 2))
        екран.blit(повърхност, rect)

    def _избор(self, екран):
        self._текст(екран, "Свирене на кавал", 40, (255, 230, 150), център=(ШИР // 2 + 60, 70), удебелен=True)
        self._текст(екран, "Песен: ↑ ↓     Ниво: ← →     Enter = свири     Esc = назад", 18, (230, 220, 200), център=(ШИР // 2 + 60, 118))
        # ниво на трудност
        for и, н in enumerate(НИВА):
            r = pygame.Rect(330 + и * 150, 400, 136, 36)
            избрано = и == self.ниво
            pygame.draw.rect(екран, (200, 150, 60) if избрано else (60, 40, 28), r, border_radius=6)
            pygame.draw.rect(екран, (255, 230, 150) if избрано else (30, 20, 14), r, 2, border_radius=6)
            self._текст(екран, н["име"], 20, (30, 18, 10) if избрано else (230, 215, 190), център=r.center, удебелен=избрано)
        ВИДИМИ = 4                                   # колко песни се виждат; списъкът се превърта
        първа = max(0, min(self.избрана - 1, len(self.списък) - ВИДИМИ))
        if първа > 0:
            self._текст(екран, "▲", 16, (255, 230, 150), център=(550, 150))
        if първа + ВИДИМИ < len(self.списък):
            self._текст(екран, "▼", 16, (255, 230, 150), център=(550, 386))
        for и, п in enumerate(self.списък):
            if not (първа <= и < първа + ВИДИМИ):
                continue
            y = 158 + (и - първа) * 56
            r = pygame.Rect(300, y, 500, 50)
            pygame.draw.rect(екран, (110, 70, 36) if и == self.избрана else (60, 40, 28), r, border_radius=6)
            pygame.draw.rect(екран, (255, 210, 120) if и == self.избрана else (30, 20, 14), r, 2, border_radius=6)
            self._текст(екран, п["name"], 24, (255, 245, 225), ляво=(r.x + 16, r.y + 6), удебелен=True)
            брой, последна = 0, -9.0
            for н in п["notes"]:                     # колко ноти ще има на избраното ниво
                if н[0] - последна >= НИВА[self.ниво]["разстояние"]:
                    брой, последна = брой + 1, н[0]
            инфо = "%s, %s, %s мин, %d ноти" % (п.get("kind", ""), п.get("meter", ""), мин_сек(п.get("length_s", 0)), брой)
            self._текст(екран, инфо, 15, (225, 205, 170), ляво=(r.x + 16, r.y + 32))
        self._текст(екран, "Клавиши: " + "  ".join(ИМЕНА_КЛАВИШИ[:int(self.списък[self.избрана].get("lanes", 3))]),
                    20, (255, 230, 150), център=(ШИР // 2 + 60, 470))

    def _гриф(self):
        ширина = self.ленти * 64 + 32
        return pygame.Rect((ШИР - ширина) // 2 + 40, 0, ширина, ВИС)

    def _свири(self, екран):
        t = self.време()
        г = self._гриф()
        # грифът: тъмно дърво с прагчета, които текат надолу
        if "grif_kaval" in self.картинки:
            картинка = self.картинки["grif_kaval"]
            отм = int(t * self.скорост) % 64
            for y in range(-64, ВИС, 64):
                екран.blit(картинка, (г.x, y + отм), (0, 0, г.w, 64))
        else:
            pygame.draw.rect(екран, (44, 28, 18), г)
            pygame.draw.rect(екран, (24, 14, 10), г, 3)
            отм = int(t * self.скорост) % 64
            for y in range(отм - 64, ВИС, 64):
                pygame.draw.line(екран, (78, 54, 34), (г.x + 4, y), (г.right - 4, y), 2)
            for л in range(self.ленти + 1):
                x = г.x + 16 + л * 64
                pygame.draw.line(екран, (96, 70, 44), (x, 0), (x, ВИС), 1)
        # линията и бутоните
        pygame.draw.rect(екран, (230, 210, 170), (г.x + 8, ЛИНИЯ_Y - 2, г.w - 16, 4))
        for л in range(self.ленти):
            cx = г.x + 16 + л * 64 + 32
            натиснат = л in self.натиснати
            цв = ЦВЕТОВЕ[л]
            pygame.draw.circle(екран, (20, 12, 8), (cx, ЛИНИЯ_Y), 28)
            pygame.draw.circle(екран, цв if натиснат else [c // 3 for c in цв], (cx, ЛИНИЯ_Y), 25)
            pygame.draw.circle(екран, (240, 230, 210), (cx, ЛИНИЯ_Y), 25, 3)
            self._текст(екран, ИМЕНА_КЛАВИШИ[л], 18, (255, 255, 255), център=(cx, ЛИНИЯ_Y + 46), удебелен=True)
        # нотите
        for н in self.ноти[max(0, self.следваща - 4):]:
            y = ЛИНИЯ_Y - (н.t - t) * self.скорост
            if y < -40:
                break
            if н.оценка in ("Перфектно", "Добре") or y > ЛИНИЯ_Y + 34:
                continue
            cx = г.x + 16 + н.лента * 64 + 32
            if ("nota_%d" % н.лента) in self.картинки:
                екран.blit(self.картинки["nota_%d" % н.лента], (cx - 32, int(y) - 16))
                continue
            цв = ЦВЕТОВЕ[н.лента] if н.оценка is None else (90, 80, 76)
            r = pygame.Rect(cx - 27, int(y) - 12, 54, 24)
            pygame.draw.rect(екран, (20, 12, 8), r.inflate(4, 4), border_radius=12)
            pygame.draw.rect(екран, цв, r, border_radius=12)
            pygame.draw.rect(екран, [min(255, c + 70) for c in цв], (r.x + 8, r.y + 4, r.w - 16, 5), border_radius=3)
        # искри при удар
        for (л, т0) in list(self.искри):
            възраст = t - т0
            if възраст > 0.25:
                self.искри.remove((л, т0))
                continue
            cx = г.x + 16 + л * 64 + 32
            радиус = int(26 + 60 * възраст)
            pygame.draw.circle(екран, (255, 240, 180), (cx, ЛИНИЯ_Y), радиус, 3)
            for к in range(8):
                ъ = к * math.pi / 4 + т0
                pygame.draw.circle(екран, ЦВЕТОВЕ[л], (int(cx + math.cos(ъ) * радиус), int(ЛИНИЯ_Y + math.sin(ъ) * радиус)), 3)
        # надпис Перфектно / Добре / Пропуск
        if self.надпис and t - self.надпис[2] < 0.6:
            self._текст(екран, self.надпис[0], 30, self.надпис[1], център=(г.centerx, ЛИНИЯ_Y - 120), удебелен=True)
        # дясно: песен, време, точки, комбо
        x = г.right + 36
        self._текст(екран, self.песен["name"], 26, (255, 230, 150), ляво=(x, 40), удебелен=True)
        self._текст(екран, "%s, %s  -  %s" % (self.песен.get("kind", ""), self.песен.get("meter", ""), НИВА[self.ниво]["име"]),
                    16, (225, 205, 170), ляво=(x, 74))
        pygame.draw.rect(екран, (30, 20, 14), (x, 104, 220, 12))
        pygame.draw.rect(екран, (236, 184, 52), (x, 104, int(220 * min(1, t / self.дължина)), 12))
        self._текст(екран, "%s / %s" % (мин_сек(t), мин_сек(self.дължина)), 16, (240, 230, 210), ляво=(x, 122))
        self._текст(екран, "Точки: %d" % self.точки, 24, (255, 255, 255), ляво=(x, 170), удебелен=True)
        self._текст(екран, "Комбо: %d" % self.комбо, 22, (255, 255, 255), ляво=(x, 206))
        if self.множител() > 1:
            self._текст(екран, "x%d" % self.множител(), 40, (255, 200, 80), ляво=(x, 238), удебелен=True)
        self._текст(екран, "Точност: %d %%" % round(self.точност()), 20, (200, 230, 200), ляво=(x, 300))
        self._текст(екран, "Esc = спри", 14, (200, 180, 150), ляво=(x, 500))
        if t < 3.0:                                               # броене преди първата нота
            self._текст(екран, str(3 - int(t)), 90, (255, 240, 200), център=(г.centerx, 220), удебелен=True)

    def _резултат(self, екран):
        р = self.резултат
        self._текст(екран, "Спряно" if р["stopped"] else "Браво!", 48, (255, 230, 150), център=(ШИР // 2 + 60, 80), удебелен=True)
        self._текст(екран, "%s  (%s)" % (р["song"], р["level"]), 26, (240, 225, 200), център=(ШИР // 2 + 60, 130))
        редове = [("Резултат", "%d %%" % round(р["percent"])), ("Точки", str(р["points"])),
                  ("Перфектно", str(р["perfect"])), ("Добре", str(р["good"])),
                  ("Пропуснати", str(р["miss"])), ("Най-дълго комбо", str(р["max_combo"]))]
        for и, (ляво, дясно) in enumerate(редове):
            y = 190 + и * 40
            self._текст(екран, ляво, 24, (230, 215, 190), ляво=(330, y))
            self._текст(екран, дясно, 24, (255, 255, 255), ляво=(600, y), удебелен=True)
        self._текст(екран, "Enter = обратно в кръчмата", 18, (255, 230, 150), център=(ШИР // 2 + 60, 490))


# ---------- пускане самостоятелно (за проба) ----------
def главна():
    pygame.init()
    прозорец = pygame.display.set_mode((ШИР, ВИС), pygame.RESIZABLE)
    pygame.display.set_caption("Real Life - Свирене")
    екран = pygame.Surface((ШИР, ВИС))
    игра = Свирене()
    часовник = pygame.time.Clock()
    while not игра.край:
        часовник.tick(120)
        for с in pygame.event.get():
            if с.type == pygame.QUIT:
                игра.край = True
            else:
                игра.клавиш(с)
        игра.обнови()
        игра.нарисувай(екран)
        W, H = прозорец.get_size()
        k = max(1, min(W // ШИР, H // ВИС))
        прозорец.fill((0, 0, 0))
        прозорец.blit(pygame.transform.scale(екран, (ШИР * k, ВИС * k)), ((W - ШИР * k) // 2, (H - ВИС * k) // 2))
        pygame.display.flip()
    print(игра.резултат)
    pygame.quit()


if __name__ == "__main__":
    главна()
