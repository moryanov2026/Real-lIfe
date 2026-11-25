# Real Life - РЕДАКТОР НА КАРТИ. Тук подреждаме плочките (под, стени, предмети).
# Пускане:  python editor.py                (отваря data/maps/start.json)
#           python editor.py data/maps/kashta.json   (друга карта; ако я няма, прави нова)
#
# ИНСТРУМЕНТИ (бутоните горе вляво или клавиши 1-6):
#   1 Четка    - ляв бутон слага избраната плочка, десен маха (както досега)
#   2 Стая     - влачи правоъгълник: под вътре + стени отвсякъде (съседните стаи делят стена)
#   3 Стена    - влачи права линия от стени (преградна стена вътре в сграда)
#   4 Врата    - клик върху стена = врата (още един клик = пак стена)
#   5 Прозорец - клик върху стена = прозорец (още един клик = пак стена)
#   6 Гума     - влачи правоъгълник: маха всичко в него (и пода)
#   7 Мебели   - лентата долу показва само обзавеждането; клик = сложи, десен бутон = махни,
#                Q / E = завърти (мебелта под мишката или избраната), не се слага върху стена
#   Ctrl+Z = назад (отменя последната промяна)    C = изчисти цялата карта
#   Стените сами избират вида си: с лице (горна стена) или ръб отгоре (странични, долна).
#
# Мишка:   колелце над лентата долу = превърта плочките
# Клавиши: стрелки/WASD = мести изгледа    Ctrl+S = запази    P = старт на героя
#          G = мрежа    F = запълни целия под с избрания под    R = презареди картинките
#          T = избраната плочка твърда/проходима    L = под/предмет
#          [ ] = по-тясна/по-широка карта    - = = по-ниска/по-висока    Esc = изход
import copy
import os
import sys

import pygame

import tiles
from render import нарисувай_карта

ПЛОЧКА = tiles.ПЛОЧКА
ПРОЗОРЕЦ_Ш, ПРОЗОРЕЦ_В = 1280, 720
УВЕЛИЧЕНИЕ = 1                   # плочката 64 се вижда в истински размер
ВИСОЧИНА_ЛЕНТА = 110             # лентата с плочки долу
ВИСОЧИНА_ГОРЕ = 24               # лентата с текст горе
КУТИЯ_ИКОНА = 64                 # място за една плочка в лентата
СКОРОСТ_ИЗГЛЕД = 600             # пиксела в секунда при местене на изгледа
ПЪТ_ПО_ПОДРАЗБИРАНЕ = os.path.join(tiles.ПАПКА, "data", "maps", "start.json")
ИНСТРУМЕНТИ = [("четка", "1 Четка"), ("стая", "2 Стая"), ("стена", "3 Стена"),
               ("врата", "4 Врата"), ("прозорец", "5 Прозорец"), ("гума", "6 Гума"), ("мебел", "7 Мебели")]
# Изгледи на една мебел в различни посоки: table, table_right / chair_down, chair_right, chair_up ...
ПОСОКИ = ("_down", "_right", "_up", "_left")
БУТОН_Ш, БУТОН_В = 112, 26
СТЕНИ = tiles.СТЕНИ                # wall, window, door


class Редактор:
    def __init__(self, път):
        self.път = път
        if os.path.exists(път):
            self.карта = tiles.зареди_карта(път)
        else:                                   # нова карта: празна, стаите се рисуват с инструмента "Стая"
            self.карта = tiles.празна_карта()
            self.карта["floor"] = [[""] * self.карта["width"] for _ in range(self.карта["height"])]
        self.инструмент = "четка"
        self.начало = None                      # клетката, от която влачим (стая, стена, гума)
        self.история = []                       # за Ctrl+Z
        self.презареди()
        self.кам_x = self.кам_y = -32
        self.мрежа = True
        self.промяна = False
        self.съобщение = "Готов. Ляв бутон = сложи, десен = махни, Ctrl+S = запази"
        self.изход_питане = False

    def презареди(self):
        self.плочки = tiles.зареди_плочки()
        self.картинки = tiles.зареди_картинки(self.плочки)
        # Под първо, после предметите; по азбучен ред, за да са частите на тайлсета една до друга
        self.списък = sorted(self.плочки, key=lambda и: (self.плочки[и]["layer"] != "floor", и))
        self.избрана = getattr(self, "избрана", self.списък[0])
        if self.избрана not in self.плочки:
            self.избрана = self.списък[0]
        self.отместване_лента = 0

    # ---------- промени по картата ----------
    def обект_в(self, x, y):
        """Връща предмета, който заема клетката (x, y), или None."""
        for о in reversed(self.карта["objects"]):
            д = self.плочки.get(о["name"], {"w": 1, "h": 1})
            if о["x"] <= x < о["x"] + д["w"] and о["y"] <= y < о["y"] + д["h"]:
                return о
        return None

    def сложи(self, x, y):
        if not (0 <= x < self.карта["width"] and 0 <= y < self.карта["height"]):
            return
        име = self.избрана
        д = self.плочки[име]
        if д["layer"] == "floor":
            if self.карта["floor"][y][x] != име:
                self.карта["floor"][y][x] = име
                self.промяна = True
            return
        if x + д["w"] > self.карта["width"] or y + д["h"] > self.карта["height"]:
            self.съобщение = "Не се побира: %s заема %dx%d клетки" % (име, д["w"], д["h"])
            return
        о = self.обект_в(x, y)
        if о and о["name"] == име and о["x"] == x and о["y"] == y:
            return                         # вече е тук (при влачене с мишката)
        # махаме всичко, което е на клетките, които новият предмет ще заеме
        for yy in range(y, y + д["h"]):
            for xx in range(x, x + д["w"]):
                стар = self.обект_в(xx, yy)
                while стар:
                    self.карта["objects"].remove(стар)
                    стар = self.обект_в(xx, yy)
        self.карта["objects"].append({"name": име, "x": x, "y": y})
        self.промяна = True

    def махни(self, x, y):
        if not (0 <= x < self.карта["width"] and 0 <= y < self.карта["height"]):
            return
        о = self.обект_в(x, y)
        if о:
            self.карта["objects"].remove(о)
        elif self.карта["floor"][y][x]:
            self.карта["floor"][y][x] = ""
        else:
            return
        self.промяна = True

    # ---------- стаи и стени ----------
    def запомни(self):
        """Снимка на картата преди промяна (за Ctrl+Z)."""
        self.история.append(copy.deepcopy(self.карта))
        del self.история[:-60]

    def назад(self):
        if self.история:
            self.карта = self.история.pop()
            self.промяна = True
            self.съобщение = "Назад (остават %d стъпки)" % len(self.история)
        else:
            self.съобщение = "Няма какво да се върне"

    def _обекти_в(self, x, y):
        return [о for о in self.карта["objects"] if о["x"] == x and о["y"] == y]

    def _стена_в(self, x, y):
        for о in self._обекти_в(x, y):
            if о["name"] in СТЕНИ:
                return о
        return None

    def _сложи_стена(self, x, y, име="wall"):
        for о in self._обекти_в(x, y):
            self.карта["objects"].remove(о)
        стар = self.обект_в(x, y)            # голям предмет (напр. легло), който стъпва тук
        while стар:
            self.карта["objects"].remove(стар)
            стар = self.обект_в(x, y)
        self.карта["objects"].append({"name": име, "x": x, "y": y})
        if not self.карта["floor"][y][x]:
            self.карта["floor"][y][x] = "floor"

    def _в_картата(self, x, y):
        return 0 <= x < self.карта["width"] and 0 <= y < self.карта["height"]

    def _правоъгълник(self, а, б):
        x0, x1 = sorted((а[0], б[0]))
        y0, y1 = sorted((а[1], б[1]))
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.карта["width"] - 1, x1), min(self.карта["height"] - 1, y1)
        return x0, y0, x1, y1

    def _линия(self, а, б):
        """Права линия (хоризонтална или вертикална, според по-дългата посока)."""
        if abs(б[0] - а[0]) >= abs(б[1] - а[1]):
            return [(x, а[1]) for x in range(min(а[0], б[0]), max(а[0], б[0]) + 1)]
        return [(а[0], y) for y in range(min(а[1], б[1]), max(а[1], б[1]) + 1)]

    def направи_стая(self, а, б):
        x0, y0, x1, y1 = self._правоъгълник(а, б)
        if x1 - x0 < 2 or y1 - y0 < 2:
            self.съобщение = "Стаята трябва да е поне 3x3 клетки (стени + под вътре)"
            return
        под = self.избрана if self.плочки[self.избрана]["layer"] == "floor" else "floor"
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                ръб = x in (x0, x1) or y in (y0, y1)
                if ръб:
                    if not self._стена_в(x, y):            # общата стена и вратите в нея остават
                        self._сложи_стена(x, y)
                else:
                    стена = self._стена_в(x, y)            # стари стени вътре изчезват (стаите се сливат)
                    if стена:
                        self.карта["objects"].remove(стена)
                    self.карта["floor"][y][x] = под
        self.промяна = True
        self.съобщение = "Стая %d x %d (вътре %d x %d). Сложи врата с инструмента 4." % (
            x1 - x0 + 1, y1 - y0 + 1, x1 - x0 - 1, y1 - y0 - 1)

    def направи_стена(self, а, б):
        клетки = [к for к in self._линия(а, б) if self._в_картата(*к)]
        for x, y in клетки:
            if not self._стена_в(x, y):
                self._сложи_стена(x, y)
        self.промяна = True
        self.съобщение = "Стена от %d клетки" % len(клетки)

    def гума(self, а, б):
        x0, y0, x1, y1 = self._правоъгълник(а, б)
        self.карта["objects"] = [о for о in self.карта["objects"]
                                 if not (x0 <= о["x"] <= x1 and y0 <= о["y"] <= y1)]
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.карта["floor"][y][x] = ""
        self.промяна = True
        self.съобщение = "Изтрито %d x %d" % (x1 - x0 + 1, y1 - y0 + 1)

    def отвор(self, x, y, име):
        """Врата или прозорец върху стена (втори клик го връща на стена)."""
        стена = self._стена_в(x, y)
        if not стена:
            self.съобщение = "%s се слага върху стена" % ("Вратата" if име == "door" else "Прозорецът")
            return False
        стена["name"] = "wall" if стена["name"] == име else име
        self.промяна = True
        self.съобщение = {"door": "Врата", "window": "Прозорец", "wall": "Пак стена"}[стена["name"]]
        return True

    def изчисти(self):
        self.запомни()
        self.карта["objects"] = []
        self.карта["floor"] = [[""] * self.карта["width"] for _ in range(self.карта["height"])]
        self.промяна = True
        self.съобщение = "Картата е изчистена (Ctrl+Z връща)"

    def избери_инструмент(self, ключ):
        self.инструмент = ключ
        self.начало = None
        self.отместване_лента = 0
        if ключ == "мебел" and not self.е_мебел(self.избрана):
            мебели = self.лента()
            if мебели:
                self.избрана = мебели[0]
        self.съобщение = {"четка": "Четка: ляв бутон слага, десен маха",
                          "стая": "Стая: влачи правоъгълник (подът е избраният от лентата)",
                          "стена": "Стена: влачи права линия",
                          "врата": "Врата: клик върху стена",
                          "прозорец": "Прозорец: клик върху стена",
                          "гума": "Гума: влачи правоъгълник",
                          "мебел": "Мебели: клик = сложи, десен = махни, Q/E = завърти"}[ключ]

    def бутон_под(self, позиция):
        for и, (ключ, _) in enumerate(ИНСТРУМЕНТИ):
            if pygame.Rect(8, ВИСОЧИНА_ГОРЕ + 8 + и * (БУТОН_В + 4), БУТОН_Ш, БУТОН_В).collidepoint(позиция):
                return ключ
        return None

    def преоразмери(self, dw, dh):
        ш = max(4, self.карта["width"] + dw)
        в = max(4, self.карта["height"] + dh)
        под = self.карта["floor"]
        празно = "" if self.инструмент != "четка" else "floor"
        под = [ред[:ш] + [празно] * (ш - len(ред)) for ред in под[:в]]
        под += [[празно] * ш for _ in range(в - len(под))]
        self.карта.update(width=ш, height=в, floor=под)
        self.карта["objects"] = [о for о in self.карта["objects"] if о["x"] < ш and о["y"] < в]
        self.промяна = True
        self.съобщение = "Размер на картата: %d x %d клетки" % (ш, в)

    def запази(self):
        tiles.запиши_карта(self.карта, self.път)
        self.промяна = False
        self.съобщение = "Запазено в " + os.path.relpath(self.път, tiles.ПАПКА)

    def смени_свойство(self, ключ):
        д = self.плочки[self.избрана]
        if ключ == "solid":
            д["solid"] = not д["solid"]
            self.съобщение = "%s: %s" % (self.избрана, "твърда (не се минава)" if д["solid"] else "проходима")
        else:
            д["layer"] = "object" if д["layer"] == "floor" else "floor"
            self.съобщение = "%s: %s" % (self.избрана, "под" if д["layer"] == "floor" else "предмет")
            self.списък = sorted(self.плочки, key=lambda и: (self.плочки[и]["layer"] != "floor", и))
        tiles.запиши_плочки(self.плочки)

    # ---------- мишка ----------
    def клетка_под_мишката(self, позиция):
        mx, my = позиция
        if my < ВИСОЧИНА_ГОРЕ or my >= ПРОЗОРЕЦ_В - ВИСОЧИНА_ЛЕНТА or self.бутон_под(позиция):
            return None
        x = (mx // УВЕЛИЧЕНИЕ + self.кам_x) // ПЛОЧКА
        y = ((my - ВИСОЧИНА_ГОРЕ) // УВЕЛИЧЕНИЕ + self.кам_y) // ПЛОЧКА
        return int(x), int(y)

    def е_мебел(self, име):
        д = self.плочки.get(име, {})
        return д.get("layer") == "object" and име not in СТЕНИ and "sheet" not in д

    def лента(self):
        """Какво се вижда в долната лента: при "Мебели" само обзавеждането."""
        if self.инструмент == "мебел":
            return [и for и in self.списък if self.е_мебел(и)]
        return self.списък

    @staticmethod
    def основа(име):
        for с in ПОСОКИ:
            if име.endswith(с):
                return име[:-len(с)]
        return име

    def изгледи(self, име):
        """Всички изгледи на същата мебел, по реда надолу, надясно, нагоре, наляво."""
        о = self.основа(име)
        ред = [о] + [о + с for с in ПОСОКИ]
        return [и for и in ред if и in self.плочки] or [име]

    def завърти(self, посока):
        клетка = self.клетка_под_мишката(pygame.mouse.get_pos())
        о = self.обект_в(*клетка) if клетка else None
        if о and self.е_мебел(о["name"]):
            в = self.изгледи(о["name"])
            if len(в) > 1:
                self.запомни()
                о["name"] = в[(в.index(о["name"]) + посока) % len(в)]
                self.промяна = True
                self.съобщение = "Завъртяна: " + о["name"]
                return
        в = self.изгледи(self.избрана)
        if len(в) > 1:
            self.избрана = в[(в.index(self.избрана) + посока) % len(в)]
            self.съобщение = "Избрана: " + self.избрана
        else:
            self.съобщение = "%s има само един изглед (нарисувайте и %s_right.png)" % (self.избрана, self.основа(self.избрана))

    def сложи_мебел(self, x, y):
        if not self.е_мебел(self.избрана):
            self.съобщение = "Избери мебел от лентата долу"
            return False
        д = self.плочки[self.избрана]
        for yy in range(y, y + д["h"]):
            for xx in range(x, x + д["w"]):
                if self._стена_в(xx, yy):
                    self.съобщение = "Не може върху стена"
                    return False
        self.сложи(x, y)
        return True

    def махни_мебел(self, x, y):
        о = self.обект_в(x, y)
        if о and self.е_мебел(о["name"]):
            self.карта["objects"].remove(о)
            self.промяна = True
            return True
        return False

    def плочка_в_лентата(self, позиция):
        mx, my = позиция
        if my < ПРОЗОРЕЦ_В - ВИСОЧИНА_ЛЕНТА + 8:
            return None
        лента = self.лента()
        и = mx // (КУТИЯ_ИКОНА + 8) + self.отместване_лента
        return лента[и] if 0 <= и < len(лента) else None

    # ---------- рисуване ----------
    def нарисувай(self, прозорец, шрифт):
        прозорец.fill((20, 18, 26))
        изглед_ш = ПРОЗОРЕЦ_Ш // УВЕЛИЧЕНИЕ
        изглед_в = (ПРОЗОРЕЦ_В - ВИСОЧИНА_ЛЕНТА - ВИСОЧИНА_ГОРЕ) // УВЕЛИЧЕНИЕ
        изглед = pygame.Surface((изглед_ш, изглед_в))
        изглед.fill((35, 32, 45))
        к_x, к_y = int(self.кам_x), int(self.кам_y)
        # рамка на картата
        pygame.draw.rect(изглед, (10, 10, 14), (-к_x, -к_y, self.карта["width"] * ПЛОЧКА,
                                               self.карта["height"] * ПЛОЧКА))
        нарисувай_карта(изглед, self.карта, self.плочки, self.картинки, к_x, к_y)
        if self.мрежа:
            for x in range(self.карта["width"] + 1):
                pygame.draw.line(изглед, (0, 0, 0), (x * ПЛОЧКА - к_x, -к_y),
                                 (x * ПЛОЧКА - к_x, self.карта["height"] * ПЛОЧКА - к_y))
            for y in range(self.карта["height"] + 1):
                pygame.draw.line(изглед, (0, 0, 0), (-к_x, y * ПЛОЧКА - к_y),
                                 (self.карта["width"] * ПЛОЧКА - к_x, y * ПЛОЧКА - к_y))
        # старт на героя
        сх, су = self.карта["start"]
        pygame.draw.rect(изглед, (255, 220, 60), (сх * ПЛОЧКА - к_x + 4, су * ПЛОЧКА - к_y + 4,
                                                  ПЛОЧКА - 8, ПЛОЧКА - 8), 2)
        # призрак на избраната плочка под мишката
        клетка = self.клетка_под_мишката(pygame.mouse.get_pos())
        if клетка and self.инструмент not in ("четка", "мебел"):
            self._нарисувай_призрак(изглед, клетка, к_x, к_y)
        elif клетка:
            д = self.плочки[self.избрана]
            призрак = self.картинки[self.избрана].copy()
            призрак.set_alpha(150)
            tiles.нарисувай_плочка(изглед, призрак, д, клетка[0], клетка[1], к_x, к_y)
            pygame.draw.rect(изглед, (255, 255, 255), (клетка[0] * ПЛОЧКА - к_x, клетка[1] * ПЛОЧКА - к_y,
                                                       д["w"] * ПЛОЧКА, д["h"] * ПЛОЧКА), 1)
        прозорец.blit(pygame.transform.scale(изглед, (изглед_ш * УВЕЛИЧЕНИЕ, изглед_в * УВЕЛИЧЕНИЕ)),
                      (0, ВИСОЧИНА_ГОРЕ))
        # бутони с инструментите
        мишка = pygame.mouse.get_pos()
        for и, (ключ, надпис) in enumerate(ИНСТРУМЕНТИ):
            r = pygame.Rect(8, ВИСОЧИНА_ГОРЕ + 8 + и * (БУТОН_В + 4), БУТОН_Ш, БУТОН_В)
            избран = ключ == self.инструмент
            pygame.draw.rect(прозорец, (230, 190, 60) if избран else ((70, 66, 90) if r.collidepoint(мишка) else (45, 42, 58)), r)
            pygame.draw.rect(прозорец, (15, 12, 20), r, 1)
            прозорец.blit(шрифт.render(надпис, True, (20, 15, 10) if избран else (235, 235, 235)), (r.x + 8, r.y + 5))

        # горна лента
        pygame.draw.rect(прозорец, (20, 18, 26), (0, 0, ПРОЗОРЕЦ_Ш, ВИСОЧИНА_ГОРЕ))
        текст = "%s  (%dx%d)%s   |   %s" % (os.path.basename(self.път), self.карта["width"],
                                          self.карта["height"], " *незапазена*" if self.промяна else "",
                                          self.съобщение)
        прозорец.blit(шрифт.render(текст, True, (255, 255, 240)), (8, 4))

        # долна лента с плочките
        горе = ПРОЗОРЕЦ_В - ВИСОЧИНА_ЛЕНТА
        pygame.draw.rect(прозорец, (28, 26, 36), (0, горе, ПРОЗОРЕЦ_Ш, ВИСОЧИНА_ЛЕНТА))
        x = 4
        for име in self.лента()[self.отместване_лента:]:
            if x + КУТИЯ_ИКОНА > ПРОЗОРЕЦ_Ш:
                break
            к = self.картинки[име]
            # иконата се уголемява с цяло число пъти (без размазване)
            мащаб = max(1, min(КУТИЯ_ИКОНА // к.get_width(), КУТИЯ_ИКОНА // к.get_height()))
            if к.get_width() > КУТИЯ_ИКОНА or к.get_height() > КУТИЯ_ИКОНА:
                мащаб = 0.5
            голяма = pygame.transform.scale(к, (int(к.get_width() * мащаб), int(к.get_height() * мащаб)))
            кутия = pygame.Rect(x, горе + 8, КУТИЯ_ИКОНА, КУТИЯ_ИКОНА)
            pygame.draw.rect(прозорец, (45, 42, 58), кутия)
            прозорец.blit(голяма, голяма.get_rect(center=кутия.center))
            if име == self.избрана:
                pygame.draw.rect(прозорец, (255, 220, 60), кутия.inflate(4, 4), 2)
            етикет = шрифт.render(име[:10], True, (200, 200, 200))
            прозорец.blit(етикет, (x, горе + 8 + КУТИЯ_ИКОНА + 4))
            x += КУТИЯ_ИКОНА + 8
        д = self.плочки[self.избрана]
        инфо = "Избрана: %s | %s | %s | заема %dx%d   (T твърда, L под/предмет)" % (
            self.избрана, "под" if д["layer"] == "floor" else "предмет",
            "твърда" if д["solid"] else "проходима", д["w"], д["h"])
        прозорец.blit(шрифт.render(инфо, True, (255, 220, 60)), (ПРОЗОРЕЦ_Ш - 620, горе - 20))

    def _нарисувай_призрак(self, изглед, клетка, к_x, к_y):
        """Показва какво ще стане, преди да пуснеш мишката."""
        слой = pygame.Surface(изглед.get_size(), pygame.SRCALPHA)
        def кл(x, y, цвят):
            pygame.draw.rect(слой, цвят, (x * ПЛОЧКА - к_x, y * ПЛОЧКА - к_y, ПЛОЧКА, ПЛОЧКА))
        а = self.начало or клетка
        if self.инструмент == "стая":
            x0, y0, x1, y1 = self._правоъгълник(а, клетка)
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    ръб = x in (x0, x1) or y in (y0, y1)
                    кл(x, y, (255, 210, 60, 120) if ръб else (90, 220, 120, 60))
            текст = "%d x %d" % (x1 - x0 + 1, y1 - y0 + 1)
        elif self.инструмент == "стена":
            for x, y in self._линия(а, клетка):
                кл(x, y, (255, 210, 60, 130))
            текст = "%d" % len(self._линия(а, клетка))
        elif self.инструмент == "гума":
            x0, y0, x1, y1 = self._правоъгълник(а, клетка)
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    кл(x, y, (240, 70, 60, 90))
            текст = "%d x %d" % (x1 - x0 + 1, y1 - y0 + 1)
        else:                                   # врата / прозорец
            добре = self._стена_в(*клетка) is not None
            кл(*клетка, (90, 220, 120, 110) if добре else (240, 70, 60, 110))
            текст = ""
        изглед.blit(слой, (0, 0))
        if текст:
            ш = pygame.font.SysFont("arial", 16, bold=True).render(текст, True, (255, 255, 255))
            изглед.blit(ш, (клетка[0] * ПЛОЧКА - к_x + ПЛОЧКА + 4, клетка[1] * ПЛОЧКА - к_y + ПЛОЧКА + 2))

    # ---------- главен цикъл ----------
    def обработи_събитие(self, с):
        """Връща False, когато трябва да спрем."""
        if с.type == pygame.QUIT:
            return self.поискай_изход()
        if с.type == pygame.MOUSEWHEEL:
            if pygame.mouse.get_pos()[1] >= ПРОЗОРЕЦ_В - ВИСОЧИНА_ЛЕНТА:
                self.отместване_лента = max(0, min(len(self.лента()) - 1, self.отместване_лента - с.y))
        if с.type == pygame.MOUSEBUTTONDOWN and с.button in (1, 3):
            бутон = self.бутон_под(с.pos)
            име = self.плочка_в_лентата(с.pos) if с.button == 1 else None
            клетка = self.клетка_под_мишката(с.pos)
            if бутон and с.button == 1:
                self.избери_инструмент(бутон)
            elif име:
                self.избрана = име
                if self.инструмент not in ("четка", "стая", "мебел"):
                    self.инструмент = "четка"
            elif клетка:
                if self.инструмент == "четка":
                    self.запомни()               # едно Ctrl+Z връща цялото рисуване с влачене
                elif self.инструмент == "мебел":
                    self.запомни()
                    готово = self.сложи_мебел(*клетка) if с.button == 1 else self.махни_мебел(*клетка)
                    if not готово:
                        self.история.pop()
                elif с.button == 1 and self.инструмент in ("стая", "стена", "гума"):
                    self.начало = клетка
                elif с.button == 1 and self.инструмент in ("врата", "прозорец"):
                    self.запомни()
                    if not self.отвор(*клетка, "door" if self.инструмент == "врата" else "window"):
                        self.история.pop()
                elif с.button == 3 and self.инструмент != "четка":
                    self.начало = None           # десен бутон отказва влаченето
        if с.type == pygame.MOUSEBUTTONUP and с.button == 1 and self.начало:
            клетка = self.клетка_под_мишката(с.pos) or self.начало
            self.запомни()
            {"стая": self.направи_стая, "стена": self.направи_стена, "гума": self.гума}[self.инструмент](self.начало, клетка)
            self.начало = None
        if с.type == pygame.KEYDOWN:
            ctrl = с.mod & pygame.KMOD_CTRL
            if с.key == pygame.K_ESCAPE:
                return self.поискай_изход()
            self.изход_питане = False
            if с.key == pygame.K_s and ctrl:
                self.запази()
            elif с.key == pygame.K_z and ctrl:
                self.назад()
            elif pygame.K_1 <= с.key <= pygame.K_7:
                self.избери_инструмент(ИНСТРУМЕНТИ[с.key - pygame.K_1][0])
            elif с.key in (pygame.K_q, pygame.K_e):
                self.завърти(-1 if с.key == pygame.K_q else 1)
            elif с.key == pygame.K_c and not ctrl:
                self.изчисти()
            elif с.key == pygame.K_p:
                клетка = self.клетка_под_мишката(pygame.mouse.get_pos())
                if клетка:
                    self.карта["start"] = list(клетка)
                    self.промяна = True
                    self.съобщение = "Старт на героя: %d, %d" % клетка
            elif с.key == pygame.K_g:
                self.мрежа = not self.мрежа
            elif с.key == pygame.K_f and self.плочки[self.избрана]["layer"] == "floor":
                self.карта["floor"] = [[self.избрана] * self.карта["width"] for _ in range(self.карта["height"])]
                self.промяна = True
            elif с.key == pygame.K_r:
                self.презареди()
                self.съобщение = "Картинките са презаредени (%d плочки)" % len(self.плочки)
            elif с.key == pygame.K_t:
                self.смени_свойство("solid")
            elif с.key == pygame.K_l:
                self.смени_свойство("layer")
            elif с.key == pygame.K_RIGHTBRACKET:
                self.преоразмери(1, 0)
            elif с.key == pygame.K_LEFTBRACKET:
                self.преоразмери(-1, 0)
            elif с.key == pygame.K_EQUALS:
                self.преоразмери(0, 1)
            elif с.key == pygame.K_MINUS:
                self.преоразмери(0, -1)
        return True

    def поискай_изход(self):
        if self.промяна and not self.изход_питане:
            self.изход_питане = True
            self.съобщение = "Има незапазени промени! Ctrl+S за запис или Esc още веднъж за изход."
            return True
        return False


def главна():
    път = sys.argv[1] if len(sys.argv) > 1 else ПЪТ_ПО_ПОДРАЗБИРАНЕ
    път = os.path.abspath(път)
    pygame.init()
    прозорец = pygame.display.set_mode((ПРОЗОРЕЦ_Ш, ПРОЗОРЕЦ_В))
    pygame.display.set_caption("Real Life - редактор на карти")
    шрифт = pygame.font.SysFont("arial", 14)
    часовник = pygame.time.Clock()
    р = Редактор(път)
    работи = True
    while работи:
        време = часовник.tick(60) / 1000.0
        for с in pygame.event.get():
            if not р.обработи_събитие(с):
                работи = False
        к = pygame.key.get_pressed()
        if not (pygame.key.get_mods() & pygame.KMOD_CTRL):
            р.кам_x += ((к[pygame.K_d] or к[pygame.K_RIGHT]) - (к[pygame.K_a] or к[pygame.K_LEFT])) * СКОРОСТ_ИЗГЛЕД * време
            р.кам_y += ((к[pygame.K_s] or к[pygame.K_DOWN]) - (к[pygame.K_w] or к[pygame.K_UP])) * СКОРОСТ_ИЗГЛЕД * време
        бутони = pygame.mouse.get_pressed()
        клетка = р.клетка_под_мишката(pygame.mouse.get_pos())
        if клетка and р.инструмент == "четка" and бутони[0] and not р.плочка_в_лентата(pygame.mouse.get_pos()):
            р.сложи(*клетка)
        elif клетка and р.инструмент == "четка" and бутони[2]:
            р.махни(*клетка)
        р.нарисувай(прозорец, шрифт)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    главна()
