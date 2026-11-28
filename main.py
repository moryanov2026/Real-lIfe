# Real Life - ИГРАТА (клиент). Етап 3а: много играчи през локален сървър.
# Пускане:  python main.py   (или start.bat).  С брояч кадри:  python main.py --fps
#
# Меню:  "Играй сам"            - сървърът се пуска на този компютър, всички други са NPC
#        "Създай игра за класа" - този компютър е сървър, учениците влизат с неговия адрес
#        "Влез в игра"          - въвеждаш адреса на сървъра (напр. 192.168.1.20)
# В играта: WASD/стрелки = ходене, Esc = смени персона, F3 = кадри в секунда
# Собственикът и кръчмарят: B = режим за строене (мебели с цени, разширяване на кръчмата).
# Музикантът: E = свири (миниигра "Свирене", svirene.py).  F = седни на стол/пейка (пак F или тръгни = стани)
# F11 или Alt+Enter = цял екран / прозорец. Прозорецът се разтяга с мишката.  python main.py --full = направо на цял екран
import json
import math
import os
import queue
import socket
import sys
import threading
import time

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

import net
import poruchki
import render
import sklad
import tiles

# ---------- НАСТРОЙКИ ----------
ШИРИНА, ВИСОЧИНА = 1024, 576     # начален прозорец и размер на менютата (16 x 9 плочки по 64)
МИН_ШИРИНА, МИН_ВИСОЧИНА = 800, 450
ВИСОЧИНА_ЗА_УГОЛЕМЕНИЕ = 640     # на всеки 640 px височина играта се уголемява x1 (1080p -> x1, 4K -> x3)
# Прозорецът може да се разтяга с мишката; F11 или Alt+Enter = цял екран.
# Уголемяваме само с цели числа (x1, x2, x3), за да няма размазани пиксели.
# По-голям прозорец показва по-голяма част от картата.
КАДРИ_В_СЕКУНДА = 60
ИНТЕРВАЛ_ТИК = 1 / 20            # колко често праща сървърът (за изглаждане на движението)
ИНТЕРВАЛ_ВХОД = 0.1              # колко често пращаме клавишите, дори да не са се сменили
ЦВЯТ_ФОН = (20, 18, 26)
ЦВЯТ_ТЕКСТ = (255, 255, 240)
ЦВЯТ_БУТОН = (70, 55, 45)
ЦВЯТ_БУТОН_ГОРЕ = (110, 80, 55)


class Връзка:
    """Връзката към сървъра. Отделна нишка чете съобщенията и ги слага в опашка."""

    def __init__(self, адрес, порт):
        self.сокет = socket.create_connection((адрес, порт), timeout=3)
        self.сокет.settimeout(None)
        self.сокет.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.опашка = queue.Queue()
        threading.Thread(target=self._чети, daemon=True).start()

    def _чети(self):
        четец = net.Четец(self.сокет)
        try:
            while True:
                съобщения = четец.чети()
                if съобщения is None:
                    break
                for с in съобщения:
                    self.опашка.put(с)
        except (OSError, ValueError):
            pass
        self.опашка.put({"t": "_closed"})

    def прати(self, с):
        try:
            net.изпрати(self.сокет, с)
        except OSError:
            pass

    def затвори(self):
        try:
            self.сокет.close()
        except OSError:
            pass


class Игра:
    def __init__(self, шрифт, шрифт_малък, шрифт_голям):
        self.шрифт, self.малък, self.голям = шрифт, шрифт_малък, шрифт_голям
        self.екран_вид = "меню"              # меню / избор / игра
        self.връзка = None
        self.сървър = None                   # ако ние сме пуснали сървъра
        self.адрес_за_класа = ""
        self.съобщение = ""
        self.име = ""
        self.адрес = ""
        self.активно_поле = "име"
        self.карта = None
        self.плочки = self.картинки = None
        self.описания = {}                   # id -> име, роля, цвят
        self.персони = {}                    # id -> последно състояние + за изглаждане
        self.мое_id = None
        self.избрано = None
        self.ден, self.минути = 1, 0
        self.последен_вход = (0, 0)
        self.време_вход = 0.0
        self.бутони = []
        self.преобразувай_мишка = lambda п: п   # прозорецът го сменя (мащаб и отместване)
        self.свирене = None                  # миниигра "Свирене", когато музикантът свири
        self.готвене = None                  # мини игра при готвенето (gotvene.py)
        self.строене = None                  # режим за строене (B): {"индекс", "вариант", "отместване"}
        self.каталог = []                    # [(име, цена, [варианти])] от data/furniture.json
        self.кам = (0, 0)
        self.известие = None                 # (текст, до кога) - напр. бакшиш след песен
        self.музика_npc = None               # (кой, песен), която чуваме от NPC музиканта
        self.станции = []                    # мебели, на които се приготвя нещо (от сървъра)
        try:
            self.меню = poruchki.зареди()    # data/items.json: за подсказките "E = ..."
        except (OSError, ValueError):
            self.меню = {"предмети": {}, "сервират": [], "гости": [], "търпение": 90}
        try:
            self.склад_данни = sklad.зареди()     # data/sklad.json: продукти, чинии, заплати
        except (OSError, ValueError):
            self.склад_данни = {"продукти": {}}
        self.рецепти = sklad.рецепти()
        self.склад, self.чисти_чинии, self.мръсни, self.днес = {}, 0, [], {}
        self.отчет = None                    # отчетът за деня (идва от сървъра, когато кръчмата затвори)
        self.покажи_склад = False            # K = складът
        self.управление = None               # M = прозорецът на собственика: {"раздел", "ред"}
        self.карти = {}                      # krachma, selo (от сървъра)
        self.моя_карта = "krachma"           # на коя карта е моята персона
        self.нощ = 0.0                       # секунди нощ (кръчмата затвори, всички спят)
        self.ферма, self.магазин = {}, {}    # нивите, пазарът, сезонът; магазинът (от сървъра)
        self.църква = {}                     # празник, камбани, обред, гощавка (от сървъра)
        self.семе = 0                        # Tab: кое семе сее селянинът
        self.покажи_пазар = False            # P = пазарът и магазинът
        self.упр = {}                        # цени, заплати, пакети, уволнени, звезди, мнения (от сървъра)

    # ---------- свързване ----------
    def играй_сам(self):
        import server
        self.сървър = server.Сървър(хост="127.0.0.1", порт=0, запис=server.ЗАПИС).старт()
        self.свържи("127.0.0.1", self.сървър.порт)

    def създай_за_класа(self):
        import server
        try:
            self.сървър = server.Сървър(хост="0.0.0.0", порт=net.ПОРТ, запис=server.ЗАПИС).старт()
        except OSError:
            self.съобщение = "Порт %d е зает: може би вече има сървър на този компютър." % net.ПОРТ
            return
        self.адрес_за_класа = net.мой_ip()
        self.свържи("127.0.0.1", self.сървър.порт)

    def влез(self):
        адрес = self.адрес.strip()
        if not адрес:
            self.съобщение = "Напиши адреса на сървъра (напр. 192.168.1.20)."
            return
        порт = net.ПОРТ
        if ":" in адрес:
            адрес, п = адрес.rsplit(":", 1)
            порт = int(п) if п.isdigit() else порт
        self.свържи(адрес, порт)

    def свържи(self, адрес, порт):
        try:
            self.връзка = Връзка(адрес, порт)
        except OSError:
            self.съобщение = "Няма връзка със сървъра %s:%d. Пуснат ли е? Същата мрежа ли е?" % (адрес, порт)
            return
        self.връзка.прати({"t": "hello", "name": self.име.strip() or "Играч"})
        self.съобщение = "Свързване..."

    def прекъсни(self):
        if self.връзка:
            self.връзка.затвори()
            self.връзка = None
        if self.сървър:
            self.сървър.спри()
            self.сървър = None

    # ---------- съобщения от сървъра ----------
    def обработи_мрежата(self):
        if not self.връзка:
            return
        while True:
            try:
                с = self.връзка.опашка.get_nowait()
            except queue.Empty:
                return
            т = с.get("t")
            if т == "welcome":
                self.карта = с["map"]
                self.карти = dict(с.get("maps") or {"krachma": с["map"]})
                self.моя_карта = "krachma"
                self.описания = {о["id"]: о for о in с["persons"]}
                self.плочки = tiles.зареди_плочки()
                self.картинки = render.зареди_картинки(self.плочки, с["persons"])
                self.екран_вид = "избор"
                self.съобщение = ""
            elif т == "state":
                self._ново_състояние(с)
            elif т == "picked":
                self.мое_id = с["person"]
                self.екран_вид = "игра"
                self.съобщение = ""
            elif т == "error":
                self.съобщение = с.get("text", "Грешка")
            elif т == "map":                     # някой построи нещо: новата кръчма
                self.карти["krachma"] = с["map"]
                if self.моя_карта == "krachma":
                    self.карта = с["map"]
            elif т == "build_result":
                self.известие = (с.get("text", ""), time.perf_counter() + (2.0 if с.get("ok") else 3.0))
            elif т == "use_result":             # E: поръча / приготвя / взе / сервира / причина
                self.известие = (с.get("text", ""), time.perf_counter() + 2.5)
            elif т == "manage_result":          # прозорецът на собственика
                self.известие = (с.get("text", ""), time.perf_counter() + 1.5)
            elif т == "order_result":           # E при музиканта: засвири / спря / причина
                self.известие = (с.get("text", ""), time.perf_counter() + 3)
            elif т == "announce":               # празник, камбани, сватба: до всички
                self.известие = (с.get("text", ""), time.perf_counter() + 5)
            elif т == "report":                 # кръчмата затвори: отчетът за деня
                self.отчет = с.get("report")
            elif т == "tip":
                self.известие = ("Песента: %d %%  -  бакшиш +%d" % (round(с.get("percent", 0)), с.get("amount", 0)),
                                 time.perf_counter() + 5)
            elif т == "_closed":
                self.връзка = None
                self.екран_вид = "меню"
                self.мое_id = None
                self.съобщение = "Връзката със сървъра прекъсна."
                return

    def _ново_състояние(self, с):
        сега = time.perf_counter()
        self.ден, self.минути = с["day"], с["minutes"]
        self.станции = с.get("stations", [])
        self.склад = с.get("stock", self.склад)
        self.чисти_чинии = с.get("plates", self.чисти_чинии)
        self.мръсни = с.get("dirty", [])
        self.днес = с.get("today", {})
        self.упр = с.get("manage", self.упр)
        self.нощ = с.get("night", 0)
        self.ферма = с.get("farm", self.ферма)
        self.магазин = с.get("shop", self.магазин)
        self.църква = с.get("church", self.църква)
        for п in с["persons"]:
            стар = self.персони.get(п["id"])
            нов = dict(self.описания.get(п["id"], {}))
            нов.update(п)
            # кога е седнал (за анимацията на сядане)
            if п.get("sit") and not (стар and стар.get("sit")):
                нов["седна_в"] = time.perf_counter()
            elif стар and п.get("sit"):
                нов["седна_в"] = стар.get("седна_в", 0)
            # за изглаждане: тръгваме от там, където го рисуваме в момента
            if стар:
                нов["от_x"], нов["от_y"] = self._позиция(стар, сега)
            else:
                нов["от_x"], нов["от_y"] = п["x"], п["y"]
            нов["до_x"], нов["до_y"] = п["x"], п["y"]
            нов["кога"] = сега
            if стар and стар.get("map") != п.get("map"):   # мина през врата: без плъзгане
                нов["от_x"], нов["от_y"] = п["x"], п["y"]
            self.персони[п["id"]] = нов
        аз = self.персони.get(self.мое_id)
        if аз and аз.get("map", "krachma") != self.моя_карта and аз.get("map") in self.карти:
            self.моя_карта = аз["map"]               # минах през вратата: другата карта
            self.карта = self.карти[self.моя_карта]
            self.строене = None

    def _позиция(self, п, сега):
        к = min(1.0, (сега - п["кога"]) / ИНТЕРВАЛ_ТИК)
        return п["от_x"] + (п["до_x"] - п["от_x"]) * к, п["от_y"] + (п["до_y"] - п["от_y"]) * к

    # ---------- в играта ----------
    def изпрати_вход(self, dx, dy, сега):
        if not self.връзка or self.екран_вид != "игра":
            return
        if self.свирене or self.готвене or self.управление or self.покажи_склад or self.отчет or self.покажи_пазар:
            dx = dy = 0                       # докато свири / готви / гледа прозорец, не ходи
        if (dx, dy) != self.последен_вход or сега - self.време_вход > ИНТЕРВАЛ_ВХОД:
            self.връзка.прати({"t": "input", "dx": dx, "dy": dy})
            self.последен_вход, self.време_вход = (dx, dy), сега

    def избери(self, пид):
        if self.връзка:
            self.връзка.прати({"t": "pick", "person": пид})

    def смени_персона(self):
        if self.връзка:
            self.връзка.прати({"t": "leave_person"})
        self.мое_id = None
        self.екран_вид = "избор"

    # ---------- рисуване ----------
    def нарисувай(self, екран, покажи_fps, fps):
        екран.fill(ЦВЯТ_ФОН)
        self.бутони = []
        if self.екран_вид == "меню":
            self._меню(екран)
        elif self.екран_вид == "избор":
            self._избор(екран)
        else:
            self._игра(екран)
        if покажи_fps:
            екран.blit(self.шрифт.render("FPS %d" % fps, True, (255, 230, 120)),
                       (екран.get_width() - 90, екран.get_height() - 28))

    def _бутон(self, екран, rect, текст, действие, мишка):
        rect = pygame.Rect(rect)
        pygame.draw.rect(екран, ЦВЯТ_БУТОН_ГОРЕ if rect.collidepoint(мишка) else ЦВЯТ_БУТОН, rect, border_radius=6)
        pygame.draw.rect(екран, (25, 20, 30), rect, 2, border_radius=6)
        н = self.шрифт.render(текст, True, ЦВЯТ_ТЕКСТ)
        екран.blit(н, н.get_rect(center=rect.center))
        self.бутони.append((rect, действие))

    def _поле(self, екран, rect, текст, име_поле, мишка):
        rect = pygame.Rect(rect)
        активно = self.активно_поле == име_поле
        pygame.draw.rect(екран, (245, 240, 230) if активно else (200, 195, 185), rect, border_radius=4)
        pygame.draw.rect(екран, (25, 20, 30), rect, 2, border_radius=4)
        курсор = "|" if активно and int(time.time() * 2) % 2 == 0 else ""
        екран.blit(self.шрифт.render(текст + курсор, True, (30, 25, 20)), (rect.x + 8, rect.y + 8))
        self.бутони.append((rect, ("поле", име_поле)))

    def _меню(self, екран):
        м = self.преобразувай_мишка(pygame.mouse.get_pos())
        заглавие = self.голям.render("Real Life", True, (255, 220, 120))
        екран.blit(заглавие, заглавие.get_rect(center=(ШИРИНА // 2, 70)))
        екран.blit(self.шрифт.render("Твоето име:", True, ЦВЯТ_ТЕКСТ), (312, 140))
        self._поле(екран, (312, 165, 400, 40), self.име, "име", м)
        self._бутон(екран, (312, 230, 400, 50), "Играй сам", "сам", м)
        self._бутон(екран, (312, 295, 400, 50), "Създай игра за класа", "клас", м)
        екран.blit(self.шрифт.render("Адрес на сървъра:", True, ЦВЯТ_ТЕКСТ), (312, 370))
        self._поле(екран, (312, 395, 250, 40), self.адрес, "адрес", м)
        self._бутон(екран, (572, 390, 140, 50), "Влез", "влез", м)
        if self.съобщение:
            н = self.шрифт.render(self.съобщение, True, (255, 150, 120))
            екран.blit(н, н.get_rect(center=(ШИРИНА // 2, 480)))

    def _избор(self, екран):
        м = self.преобразувай_мишка(pygame.mouse.get_pos())
        екран.blit(self.голям.render("Избери персона", True, (255, 220, 120)), (40, 20))
        екран.blit(self.малък.render("Свободните персони ги играе компютърът (NPC). Esc = изход в менюто.",
                                     True, (200, 200, 200)), (40, 70))
        y = 100
        for пид, о in self.описания.items():
            п = self.персони.get(пид, {})
            зает = п.get("ctrl") == "human"
            rect = pygame.Rect(40, y, 944, 36)
            if not зает and rect.collidepoint(м):
                pygame.draw.rect(екран, (60, 50, 45), rect)
            pygame.draw.rect(екран, о.get("color", [200, 200, 200]), (48, y + 8, 20, 20))
            цвят = (130, 130, 130) if зает else ЦВЯТ_ТЕКСТ
            екран.blit(self.шрифт.render(о["name"], True, цвят), (80, y + 7))
            екран.blit(self.шрифт.render(о["role"], True, цвят), (320, y + 7))
            статус = "играе: %s" % п.get("player", "") if зает else "свободна (NPC)"
            екран.blit(self.шрифт.render(статус, True, (255, 200, 80) if зает else (140, 220, 140)), (600, y + 7))
            if not зает:
                self.бутони.append((rect, ("избери", пид)))
            y += 40
        if self.съобщение:
            екран.blit(self.шрифт.render(self.съобщение, True, (255, 150, 120)), (40, ВИСОЧИНА - 40))

    def _рисувани(self):
        """Персоните с изгладени позиции (за рисуване в този кадър)."""
        сега = time.perf_counter()
        рисувани = []
        for п in self.персони.values():
            if п.get("away") or п.get("map", "krachma") != self.моя_карта:
                continue                         # вкъщи е или е на другата карта
            x, y = self._позиция(п, сега)
            копие = dict(п)
            копие["x"], копие["y"] = x, y
            рисувани.append(копие)
        return рисувани

    def изглед_около_мен(self, повърхност):
        """Малкото прозорче в минииграта: кръчмата около моята персона (хорото около Стоян)."""
        повърхност.fill((14, 10, 12))
        if not self.карта or not self.картинки:
            return
        рисувани = self._рисувани()
        аз = next((п for п in рисувани if п["id"] == self.мое_id), None)
        if not аз:
            return
        ш, в = повърхност.get_size()
        кам_x, кам_y = int(аз["x"] - ш / 2), int(аз["y"] - 40 - в / 2)
        render.нарисувай_карта(повърхност, self.карта, self.плочки, self.картинки, кам_x, кам_y, рисувани)
        render.нарисувай_хоро(повърхност, рисувани, кам_x, кам_y, self.картинки)
        render.нарисувай_имена(повърхност, self.малък, рисувани, кам_x, кам_y, self.мое_id)

    def _игра(self, екран):
        рисувани = self._рисувани()
        аз = next((п for п in рисувани if п["id"] == self.мое_id), None)
        ш, в = екран.get_size()
        ш_карта = self.карта["width"] * tiles.ПЛОЧКА
        в_карта = self.карта["height"] * tiles.ПЛОЧКА
        кам_x = кам_y = 0
        if аз:
            кам_x = min(max(аз["x"] - ш / 2, 0), max(0, ш_карта - ш))
            кам_y = min(max(аз["y"] - 32 - в / 2, -36), max(-36, в_карта - в))
        if ш_карта < ш:                  # картата е по-малка от екрана: в средата
            кам_x = (ш_карта - ш) / 2
        if в_карта + 36 < в:
            кам_y = (в_карта - в) / 2
        кам_x, кам_y = int(кам_x), int(кам_y)
        self.кам = (кам_x, кам_y)
        под = []
        if self.моя_карта == "selo":                # растенията на нивите (под хората)
            for (x, y, култура, етап, жадно, мъртво) in self.ферма.get("plots", []):
                if култура:
                    име = "%s_mrtvo" % култура if мъртво else "%s_%d" % (култура, етап)
                    к = render.картинка_растение(име)
                    if к:
                        под.append((к, x * tiles.ПЛОЧКА, y * tiles.ПЛОЧКА, жадно))
        render.нарисувай_карта(екран, self.карта, self.плочки, self.картинки, кам_x, кам_y, рисувани, под)
        for (x, y) in (self.мръсни if self.моя_карта == "krachma" else []):   # мръсните чинии по масите
            екран.blit(render.картинка_предмет("chiniya_mrasna", 32), (int(x) - 16 - кам_x, int(y) - 16 - кам_y))
        render.нарисувай_хоро(екран, рисувани, кам_x, кам_y, self.картинки)
        render.нарисувай_имена(екран, self.малък, рисувани, кам_x, кам_y, self.мое_id)
        # табло
        pygame.draw.rect(екран, ЦВЯТ_ФОН, (0, 0, ш, 34))
        екран.blit(self.шрифт.render("Ден %d  %02d:%02d" % (self.ден, self.минути // 60, self.минути % 60),
                                     True, ЦВЯТ_ТЕКСТ), (10, 7))
        if аз:
            екран.blit(self.шрифт.render("%s (%s)" % (аз["name"], аз["role"]), True, (120, 255, 120)), (170, 7))
            екран.blit(self.шрифт.render("Пари: %d" % аз.get("money", 0), True, ЦВЯТ_ТЕКСТ), (470, 7))
            екран.blit(self.шрифт.render("Енергия", True, ЦВЯТ_ТЕКСТ), (600, 7))
            pygame.draw.rect(екран, (60, 60, 60), (690, 10, 150, 14))
            енергия = аз.get("energy", 0)
            pygame.draw.rect(екран, (90, 200, 90) if енергия >= 30 else (230, 160, 60) if енергия >= 15 else (230, 70, 50),
                             (690, 10, int(енергия * 1.5), 14))
            if енергия < 30:
                екран.blit(self.малък.render("уморен - седни (F)", True, (255, 180, 90)), (690, 26))
        хора = sum(1 for п in рисувани if п.get("ctrl") == "human")
        екран.blit(self.малък.render("Играчи: %d" % хора, True, (200, 200, 200)), (860, 9))
        if self.адрес_за_класа:
            н = self.шрифт.render("Адрес за учениците: %s" % self.адрес_за_класа, True, (255, 220, 60))
            екран.blit(н, (10, в - 30))
        if аз and self.моя_роля() != "музикант":
            н = self.малък.render("F = седни / стани     P = пазар" + ("     K = склад" if not poruchki.гост(self.моя_роля(), self.меню) else "")
                                  + ("     M = управление" if self.моя_роля() == "собственик" else ""),
                                  True, (230, 220, 200))
            екран.blit(н, (ш - н.get_width() - 12, в - 26))
        if аз and self.моя_роля() == "музикант":
            н = self.шрифт.render("E = свири на кавала    F = седни", True, (255, 230, 150))
            екран.blit(н, (ш - н.get_width() - 12, в - 30))
        render.нарисувай_поръчки(екран, рисувани, self.станции if self.моя_карта == "krachma" else [],
                                 кам_x, кам_y, self.меню.get("търпение", 90))
        for п in рисувани:                        # какво мисли гостът, след като е ял: сърце / сиво сърце
            настр = п.get("mood", -1)
            if настр is None or настр < 0.3 or п.get("away"):
                continue
            x, y = int(п["x"]) - кам_x, int(п["y"]) - кам_y - 100 - int(4 * math.sin(time.time() * 4))
            цвят = (230, 50, 70) if настр >= 0.55 else (150, 150, 160)
            pygame.draw.circle(екран, (40, 20, 20), (x - 5, y), 7)
            pygame.draw.circle(екран, (40, 20, 20), (x + 5, y), 7)
            pygame.draw.polygon(екран, (40, 20, 20), [(x - 12, y + 2), (x + 12, y + 2), (x, y + 15)])
            pygame.draw.circle(екран, цвят, (x - 5, y), 5)
            pygame.draw.circle(екран, цвят, (x + 5, y), 5)
            pygame.draw.polygon(екран, цвят, [(x - 10, y + 2), (x + 10, y + 2), (x, y + 12)])
        м = self._музикант_до_мен(рисувани, аз)
        if м:
            текст = ("E = кажи на %s да спре" if м.get("song") else "E = кажи на %s да свири") % м["name"]
        else:
            текст = self._подсказка_e(рисувани, аз)
        if текст and not self.строене:
            н = self.шрифт.render(текст, True, (255, 230, 150))
            екран.blit(н, (ш - н.get_width() - 12, в - 56))
        if self.строене:
            self._нарисувай_строене(екран, кам_x, кам_y, ш, в)
        if self.ферма.get("season"):
            дата = self.църква.get("date", "")
            т = self.малък.render("%s%s · %s" % ((дата[0].upper() + дата[1:] + " · ") if дата else "", self.ферма["season"],
                                                 self.ферма.get("weather", "")), True, (200, 230, 255))
            екран.blit(т, (10, 38))
        ред2 = []
        if self.църква.get("holiday"):
            ред2.append("Празник: %s" % self.църква["holiday"])
        if self.църква.get("nameday"):
            ред2.append("Имен ден: %s" % ", ".join(self.църква["nameday"]))
        if self.църква.get("fast") and not self.църква.get("holiday"):
            ред2.append(self.църква["fast"])
        if ред2:
            т = self.шрифт.render("   ".join(ред2), True, (255, 200, 120))
            екран.blit(т, (10, 56))
        гощ = self.църква.get("feast") or {}
        if гощ:                                    # гощавката: какво още трябва на трапезата
            редове = ["%s - до %s" % (гощ.get("name", ""), гощ.get("until", ""))]
            for к, б in гощ.get("need", {}).items():
                if б > 0:
                    редове.append("  %s: още %d" % (self.меню.get("предмети", {}).get(к, {}).get("име", к), б))
            фон = pygame.Surface((250, 20 * len(редове) + 10), pygame.SRCALPHA)
            фон.fill((40, 20, 10, 190))
            екран.blit(фон, (ш - 262, 44))
            for и, ред in enumerate(редове):
                екран.blit(self.малък.render(ред, True, (255, 230, 160) if и == 0 else (240, 230, 210)), (ш - 254, 49 + и * 20))
        if self.църква.get("bells") and self.моя_карта == "selo" and getattr(self, "село_инфо", None):
            к = self.село_инфо.get("камбанария")
            if к:
                т = self.шрифт.render("Дин-дон!", True, (255, 240, 160))
                екран.blit(т, (к[0] * 64 + 32 - кам_x - т.get_width() // 2, к[1] * 64 - 300 - кам_y))
        if self.моя_карта in ("selo", "magazin", "tsarkva"):
            т = self.малък.render({"selo": "Селото", "magazin": "Магазинът", "tsarkva": "Църквата"}[self.моя_карта], True, (230, 230, 200))
            екран.blit(т, (ш // 2 - т.get_width() // 2, 38))
        if self.моя_карта == "selo" and getattr(self, "село_инфо", None):
            for ключ, текст in (("кокошарник", "яйца: %d" % self.ферма.get("eggs", 0)), ("крава", "мляко!" if self.ферма.get("cow") else "")):
                к = self.село_инфо.get(ключ)
                if к and текст:
                    т = self.малък.render(текст, True, (255, 250, 220))
                    екран.blit(т, (к[0] * 64 + 32 - кам_x - т.get_width() // 2, к[1] * 64 - 40 - кам_y))
        if self.нощ > 0:                          # нощ: всички спят
            тъмно = pygame.Surface((ш, в), pygame.SRCALPHA)
            тъмно.fill((8, 10, 30, int(200 * min(1.0, self.нощ / 1.5))))
            екран.blit(тъмно, (0, 0))
            т = self.голям.render("Нощ... всички спят", True, (200, 210, 255))
            екран.blit(т, т.get_rect(center=(ш // 2, в // 2 - 120)))
        if self.покажи_склад:
            self._нарисувай_склад(екран)
        if self.покажи_пазар:
            self._нарисувай_пазар(екран)
        if self.управление is not None:
            self._нарисувай_управление(екран)
        if self.отчет:
            self._нарисувай_отчет(екран)
        if self.известие and time.perf_counter() < self.известие[1]:
            н = self.голям.render(self.известие[0], True, (255, 230, 120))
            фон = pygame.Surface((н.get_width() + 24, н.get_height() + 12), pygame.SRCALPHA)
            фон.fill((0, 0, 0, 170))
            екран.blit(фон, фон.get_rect(center=(ш // 2, 90)))
            екран.blit(н, н.get_rect(center=(ш // 2, 90)))

    # ---------- мишка и клавиши ----------
    def клик(self, позиция):
        for rect, действие in self.бутони:
            if rect.collidepoint(позиция):
                if isinstance(действие, tuple) and действие[0] == "поле":
                    self.активно_поле = действие[1]
                elif isinstance(действие, tuple) and действие[0] == "избери":
                    self.избери(действие[1])
                elif действие == "сам":
                    self.играй_сам()
                elif действие == "клас":
                    self.създай_за_класа()
                elif действие == "влез":
                    self.влез()
                elif isinstance(действие, tuple) and действие[0] == "мебел":
                    self.строене.update(индекс=действие[1], вариант=0)
                elif isinstance(действие, tuple) and действие[0] == "разшири" and self.връзка:
                    self.връзка.прати({"t": "build", "op": "expand", "side": действие[1]})
                return
        if self.екран_вид == "игра" and self.строене and self.връзка and 40 < позиция[1] < self.строене.get("долу", 9999):
            x, y = self._клетка(позиция)
            self.връзка.прати({"t": "build", "op": "place", "name": self._избрана_мебел(), "x": x, "y": y})

    def текст(self, знаци):
        if self.екран_вид != "меню":
            return
        if self.активно_поле == "име" and len(self.име) < 20:
            self.име += знаци
        elif self.активно_поле == "адрес" and len(self.адрес) < 30:
            self.адрес += знаци

    def клавиш(self, събитие):
        """Връща False, ако трябва да спрем играта."""
        к = събитие.key
        if self.екран_вид == "меню":
            if к == pygame.K_ESCAPE:
                return False
            if к == pygame.K_BACKSPACE:
                if self.активно_поле == "име":
                    self.име = self.име[:-1]
                else:
                    self.адрес = self.адрес[:-1]
            elif к == pygame.K_TAB:
                self.активно_поле = "адрес" if self.активно_поле == "име" else "име"
            elif к == pygame.K_RETURN:
                self.влез() if self.адрес.strip() else self.играй_сам()
        elif self.екран_вид == "избор" and к == pygame.K_ESCAPE:
            self.прекъсни()
            self.екран_вид = "меню"
            self.адрес_за_класа = ""
        elif self.екран_вид == "игра" and self.отчет and к in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_e):
            self.отчет = None                    # прочетох отчета
        elif self.екран_вид == "игра" and self.управление is not None:
            self._клавиш_управление(к)
        elif self.екран_вид == "игра" and к == pygame.K_m and not self.строене:
            if self.моя_роля() == "собственик":
                self.управление = {"раздел": 0, "ред": 0}
                self.покажи_склад = False
            else:
                self.известие = ("Само собственикът управлява кръчмата (M)", time.perf_counter() + 2.5)
        elif self.екран_вид == "игра" and к == pygame.K_TAB and self.моя_роля() in ("селянин", "собственик") and self.ферма.get("seeds"):
            self.семе = (self.семе + 1) % len(self.ферма["seeds"])
            self.известие = ("Семе: %s" % self._име_продукт(self._семе()), time.perf_counter() + 1.5)
        elif self.екран_вид == "игра" and к == pygame.K_p and not self.строене:
            self.покажи_пазар = not self.покажи_пазар
        elif self.екран_вид == "игра" and self.покажи_пазар and к == pygame.K_ESCAPE:
            self.покажи_пазар = False
        elif self.екран_вид == "игра" and к == pygame.K_k and not self.строене:
            self.покажи_склад = not self.покажи_склад
        elif self.екран_вид == "игра" and self.покажи_склад and к == pygame.K_ESCAPE:
            self.покажи_склад = False
        elif self.екран_вид == "игра" and self.строене and к in (pygame.K_ESCAPE, pygame.K_b):
            self.строене = None
        elif self.екран_вид == "игра" and self.строене and к in (pygame.K_q, pygame.K_e):
            варианти = self.каталог[self.строене["индекс"]][2]
            self.строене["вариант"] = (self.строене["вариант"] + (1 if к == pygame.K_e else -1)) % len(варианти)
        elif self.екран_вид == "игра" and к == pygame.K_b:
            self.започни_строене()
        elif self.екран_вид == "игра" and к == pygame.K_ESCAPE:
            self.смени_персона()
        elif self.екран_вид == "игра" and к == pygame.K_f:
            if self.връзка:
                self.връзка.прати({"t": "sit"})
        elif self.екран_вид == "игра" and к == pygame.K_e and self.моя_роля() == "музикант":
            self.започни_свирене()
        elif self.екран_вид == "игра" and к == pygame.K_e and self.връзка:
            рисувани = self._рисувани()
            аз = next((п for п in рисувани if п["id"] == self.мое_id), None)
            if self._музикант_до_мен(рисувани, аз):
                self.връзка.прати({"t": "order_song"})   # кажи на музиканта да свири / да спре
            else:
                _, действие, предмет = self._какво_прави_e(рисувани, аз)
                if действие in ("cook", "wash", "milk", "till", "church"):
                    import gotvene
                    gotvene.УМОРА = max(0.0, min(1.0, (30 - (аз or {}).get("energy", 100)) / 30.0))
                if действие == "cook":                   # приготвяне: мини игра (gotvene.py)
                    import gotvene
                    self.готвене = gotvene.Готвене(предмет)   # избор на ястие, после рецептата стъпка по стъпка
                elif действие == "church":               # отецът / звънарят: камбани, свещи, венчавка, кръщене
                    import gotvene
                    вид = {"bells": "камбани", "candles": "свещи", "сватба": "венчавка", "кръщене": "кръщене"}[предмет]
                    име = {"bells": "Камбаните", "candles": "Свещите", "сватба": "Венчавка", "кръщене": "Кръщене"}[предмет]
                    self.готвене = gotvene.Стъпка("_church_" + предмет, име, вид=вид)
                elif действие == "milk":                 # кравата: мини игра "Доене"
                    import gotvene
                    self.готвене = gotvene.Стъпка("_mlyako", "Доене", вид="доене")
                elif действие == "till":                 # касата в магазина: мини игра "Ресто"
                    import gotvene
                    self.готвене = gotvene.Стъпка("_kasa", "Касата", вид="ресто", настройки=предмет)
                elif действие == "wash":                 # мивката: мини игра "Миене на чинии"
                    import gotvene
                    self.готвене = gotvene.Стъпка("_chinii", "Миене на чинии", вид="миене", настройки={"брой": предмет})
                else:
                    self.връзка.прати({"t": "use", "seed": self._семе()})   # поръчай / вземи / сервирай / ферма
        return True

    # ---------- режим за строене (B) ----------
    def започни_строене(self):
        import world
        if self.моя_роля() not in world.СТРОИТЕЛИ:
            self.известие = ("Само собственикът и кръчмарят могат да строят", time.perf_counter() + 3)
            return
        if self.моя_карта != "krachma":
            self.известие = ("Строи се вътре в кръчмата", time.perf_counter() + 3)
            return
        if not self.каталог:
            with open(world.ПЪТ_КАТАЛОГ, encoding="utf-8") as f:
                д = json.load(f)
            self.каталог = [(м["име"], м["цена"], [в for в in м["варианти"] if в in self.плочки])
                            for р in д["раздели"] for м in р["мебели"]]
            self.каталог = [м for м in self.каталог if м[2]]
            self.разширяване = д.get("разширяване", {})
        self.строене = {"индекс": 0, "вариант": 0, "отместване": 0}

    def _избрана_мебел(self):
        м = self.каталог[self.строене["индекс"]]
        return м[2][self.строене["вариант"] % len(м[2])]

    def _клетка(self, позиция):
        return (int((позиция[0] + self.кам[0]) // tiles.ПЛОЧКА), int((позиция[1] + self.кам[1]) // tiles.ПЛОЧКА))

    def _предмет_в(self, x, y):
        for о in reversed(self.карта["objects"]):
            д = self.плочки.get(о["name"], {"w": 1, "h": 1})
            if о["x"] <= x < о["x"] + д["w"] and о["y"] <= y < о["y"] + д["h"]:
                return о
        return None

    def _може(self, име, x, y):
        д = self.плочки[име]
        for yy in range(y, y + д["h"]):
            for xx in range(x, x + д["w"]):
                if not (0 <= xx < self.карта["width"] and 0 <= yy < self.карта["height"]):
                    return False
                if not self.карта["floor"][yy][xx] or self._предмет_в(xx, yy):
                    return False
        return True

    def колело(self, посока):
        if self.строене:
            self.строене["отместване"] = max(0, min(len(self.каталог) - 1, self.строене["отместване"] - посока))

    def десен_клик(self, позиция):
        if self.екран_вид == "игра" and self.строене and self.връзка:
            x, y = self._клетка(позиция)
            self.връзка.прати({"t": "build", "op": "remove", "x": x, "y": y})

    def _нарисувай_строене(self, екран, кам_x, кам_y, ш, в):
        П = tiles.ПЛОЧКА
        мишка = self.преобразувай_мишка(pygame.mouse.get_pos())
        долу = в - 100
        self.строене["долу"] = долу
        # мрежа върху пода
        мрежа = pygame.Surface((ш, в), pygame.SRCALPHA)
        for y in range(self.карта["height"]):
            for x in range(self.карта["width"]):
                if self.карта["floor"][y][x]:
                    pygame.draw.rect(мрежа, (255, 255, 255, 40), (x * П - кам_x, y * П - кам_y, П, П), 1)
        екран.blit(мрежа, (0, 0))
        # призрак на избраната мебел под мишката
        if мишка[1] < долу and мишка[1] > 40:
            име = self._избрана_мебел()
            x, y = self._клетка(мишка)
            д = self.плочки[име]
            може = self._може(име, x, y)
            призрак = self.картинки[име].copy()
            призрак.set_alpha(170)
            tiles.нарисувай_плочка(екран, призрак, д, x, y, кам_x, кам_y)
            цвят = (90, 230, 110, 90) if може else (240, 70, 60, 90)
            рамка = pygame.Surface((д["w"] * П, д["h"] * П), pygame.SRCALPHA)
            рамка.fill(цвят)
            екран.blit(рамка, (x * П - кам_x, y * П - кам_y))
            pygame.draw.rect(екран, цвят[:3], (x * П - кам_x, y * П - кам_y, д["w"] * П, д["h"] * П), 2)
        # каталог долу
        pygame.draw.rect(екран, (28, 22, 20), (0, долу, ш, 100))
        pygame.draw.line(екран, (200, 150, 70), (0, долу), (ш, долу), 2)
        x = 10
        for и in range(self.строене["отместване"], len(self.каталог)):
            if x + 84 > ш:
                break
            име, цена, варианти = self.каталог[и]
            кутия = pygame.Rect(x, долу + 8, 84, 84)
            избрана = и == self.строене["индекс"]
            pygame.draw.rect(екран, (110, 80, 40) if избрана else (52, 42, 36), кутия, border_radius=6)
            pygame.draw.rect(екран, (255, 220, 120) if избрана else (20, 14, 10), кутия, 2, border_radius=6)
            к = self.картинки[варианти[self.строене["вариант"] % len(варианти)] if избрана else варианти[0]]
            мащаб = min(68 / к.get_width(), 48 / к.get_height())
            малка = pygame.transform.scale(к, (max(1, int(к.get_width() * мащаб)), max(1, int(к.get_height() * мащаб))))
            екран.blit(малка, малка.get_rect(center=(кутия.centerx, кутия.y + 28)))
            екран.blit(self.малък.render(име[:12], True, (240, 230, 210)), (кутия.x + 4, кутия.y + 52))
            екран.blit(self.малък.render("%d пари" % цена, True, (255, 210, 90)), (кутия.x + 4, кутия.y + 67))
            self.бутони.append((кутия, ("мебел", и)))
            x += 92
        # разширяване
        цена = self.разширяване.get("цена", 200)
        for и, (текст, страна) in enumerate((("Разшири надясно", "right"), ("Разшири надолу", "down"))):
            r = pygame.Rect(ш - 230, 44 + и * 40, 220, 34)
            pygame.draw.rect(екран, (70, 55, 45) if not r.collidepoint(мишка) else (110, 80, 55), r, border_radius=6)
            pygame.draw.rect(екран, (25, 20, 30), r, 2, border_radius=6)
            н = self.малък.render("%s  (%d)" % (текст, цена), True, ЦВЯТ_ТЕКСТ)
            екран.blit(н, н.get_rect(center=r.center))
            self.бутони.append((r, ("разшири", страна)))
        подсказка = "СТРОЕНЕ: клик = купи и сложи   десен бутон = вдигни (връща парите)   Q/E = завърти   колелце = още   B = изход"
        н = self.малък.render(подсказка, True, (255, 230, 150))
        фон = pygame.Surface((н.get_width() + 12, н.get_height() + 6), pygame.SRCALPHA)
        фон.fill((0, 0, 0, 170))
        екран.blit(фон, (6, долу - 28))
        екран.blit(н, (12, долу - 25))

    # ---------- миниигра "Свирене" ----------
    def моя_роля(self):
        return self.описания.get(self.мое_id, {}).get("role", "")

    def _подсказка_e(self, рисувани, аз):
        return self._какво_прави_e(рисувани, аз)[0]

    def миниигра(self):
        return self.свирене or self.готвене

    def обнови_готвене(self):
        """Вика се всеки кадър; когато мини играта при готвенето свърши, казва на сървъра."""
        if not self.готвене:
            return
        self.готвене.обнови()
        if self.готвене.край:
            if self.готвене.резултат and self.връзка and self.готвене.резултат["item"] == "_chinii":
                self.връзка.прати({"t": "wash", "quality": self.готвене.резултат["quality"]})
            elif self.готвене.резултат and self.връзка and self.готвене.резултат["item"].startswith("_church_"):
                self.връзка.прати({"t": "church", "op": self.готвене.резултат["item"][8:],
                                   "quality": self.готвене.резултат["quality"]})
            elif self.готвене.резултат and self.връзка and self.готвене.резултат["item"] == "_mlyako":
                self.връзка.прати({"t": "milk", "quality": self.готвене.резултат["quality"]})
            elif self.готвене.резултат and self.връзка and self.готвене.резултат["item"] == "_kasa":
                self.връзка.прати({"t": "till", "quality": self.готвене.резултат["quality"]})
            elif self.готвене.резултат and self.връзка:
                self.връзка.прати({"t": "cook", "item": self.готвене.резултат["item"],
                                   "quality": self.готвене.резултат["quality"]})
            self.готвене = None

    def _какво_прави_e(self, рисувани, аз):
        """Какво ще направи E точно сега: (подсказка, "cook"/"use"/None, предмет)."""
        т = self._какво_прави_e_текст(рисувани, аз)
        return т if isinstance(т, tuple) else (т, None, None)

    def _какво_прави_e_текст(self, рисувани, аз):
        if not аз or self.моя_роля() == "музикант":
            return ""
        предмети = self.меню.get("предмети", {})
        име = lambda к: предмети.get(к, {}).get("име", к)
        роля = self.моя_роля()
        if poruchki.гост(роля, self.меню):
            if аз.get("want"):
                return "Чакаш: %s" % име(аз["want"])
            if аз.get("sit") and not аз.get("eat"):
                return "E = поръчай"
            return ""
        помощ = self._помощник_e(аз, роля)
        if помощ is not None:
            return помощ
        if роля not in self.меню.get("сервират", []):
            return ""
        if аз.get("hold"):
            for п in рисувани:
                if (п.get("want") == аз["hold"] and п.get("sit")
                        and ((п["x"] - аз["x"]) ** 2 + (п["y"] - аз["y"]) ** 2) ** 0.5 <= poruchki.ДО_ГОСТ):
                    return "E = сервирай на %s" % п["name"]
            гощ = self.църква.get("feast") or {}
            if гощ.get("need", {}).get(аз["hold"], 0) > 0:
                return "Носиш: %s - занеси го на голямата маса (%s, E)" % (име(аз["hold"]), гощ.get("name", "гощавка").lower())
            return "Носиш: %s - занеси го на госта, който го иска" % име(аз["hold"])
        if not self.карта:
            return ""
        готови = {(с["x"], с["y"]): с for с in self.станции}
        близки = sorted((poruchki.до_станция(аз["x"], аз["y"], x, y), x, y, предмет)
                        for (x, y, _, предмет) in poruchki.станции_на_карта(self.карта, self.меню))
        близки = [б for б in близки if б[0] <= poruchki.ДО_СТАНЦИЯ]
        if not близки:
            return ""
        for _, x, y, предмет in близки:
            с = готови.get((x, y))
            if с and с.get("ready"):
                return "E = вземи %s" % име(с["item"]).lower()
        искани = {п.get("want") for п in рисувани if п.get("want") and п.get("sit")}
        свободни = [б for б in близки if (б[1], б[2]) not in готови]
        мои = [б for б in свободни if роля in предмети.get(б[3], {}).get("кой", [])]
        мои.sort(key=lambda б: (б[3] not in искани, б[0]))           # първо това, което гостите чакат
        if мои:                                                    # всичко, което мога да сготвя тук
            избор = []
            for б in мои:
                if б[3] not in [и[0] for и in избор]:
                    избор.append((б[3], име(б[3]), б[3] in искани))
            може = [и for и in избор if not self._липсват(и[0])]    # само ако има продукти и чиния
            if not може:
                return "%s: няма %s" % (избор[0][1], ", ".join(self._липсват(избор[0][0])).lower())
            избор = може
            if len(избор) == 1:
                return ("E = приготви %s" % име(избор[0][0]).lower(), "cook", избор)
            return ("E = готви (%s)" % ", ".join(и[1].lower() for и in избор), "cook", избор)
        if свободни:
            предмет = свободни[0][3]
            return "%s го приготвя %s" % (име(предмет), " или ".join(предмети[предмет]["кой"]))
        return "Приготвя се: %s" % име(готови[(близки[0][1], близки[0][2])]["item"]).lower()

    def _липсват(self, предмет):
        д = self.склад_данни
        липса = [д["продукти"][к]["име"] for к in sklad.липсват(предмет, д, self.рецепти, self.склад)]
        if предмет in д.get("с_чиния", []) and self.чисти_чинии < 1:
            липса.append("чисти чинии")
        return липса

    def _до_мебел(self, аз, имена):
        р = self.склад_данни.get("до_мебел", 80)
        return any(poruchki.до_станция(аз["x"], аз["y"], о["x"], о["y"]) <= р
                   for о in self.карта["objects"] if о["name"] in имена)

    def _семе(self):
        семена = self.ферма.get("seeds", [])
        return семена[self.семе % len(семена)] if семена else None

    def _име_продукт(self, к):
        return self.склад_данни.get("продукти", {}).get(к, {}).get("име", к or "")

    def _близо(self, аз, клетка, разстояние):
        x, y = клетка[0] * tiles.ПЛОЧКА + 32, (клетка[1] + 1) * tiles.ПЛОЧКА - 8
        return math.hypot(x - аз["x"], y - аз["y"]) <= разстояние

    def _ферма_e(self, аз, роля):
        """Подсказките на селянина в селото."""
        инфо = getattr(self, "село_инфо", None)
        if инфо is None:
            try:
                with open(os.path.join(tiles.ПАПКА, "data", "selo.json"), encoding="utf-8") as f:
                    self.село_инфо = инфо = json.load(f)
            except (OSError, ValueError):
                self.село_инфо = инфо = {}
        реколта = аз.get("harvest") or {}
        if реколта and any(self._близо(аз, к, 90) for к in инфо.get("пазар", [])):
            return "E = продай на пазара (%s)" % ", ".join("%d %s" % (б, self._име_продукт(к).lower()) for к, б in реколта.items())
        if инфо.get("кладенец") and self._близо(аз, инфо["кладенец"], 90):
            return "E = напълни кофата с вода"
        if инфо.get("кокошарник") and self._близо(аз, инфо["кокошарник"], 100):
            return "E = събери яйцата (%d)" % self.ферма.get("eggs", 0) if self.ферма.get("eggs") else "Кокошките още не са снесли"
        if инфо.get("крава") and self._близо(аз, инфо["крава"], 100):
            return ("E = издои кравата", "milk", None) if self.ферма.get("cow") else "Кравата вече е издоена - след малко пак"
        ниви = {(п[0], п[1]): п for п in self.ферма.get("plots", [])}
        близки = [к for к in ниви if self._близо(аз, к, 70)]
        if not близки:
            if реколта:
                return "Носиш реколта - занеси я на пазара (сергиите)"
            return "Tab = семе (%s)   Нивите са до къщата ти" % self._име_продукт(self._семе()) if self._семе() else ""
        к = min(близки, key=lambda к: math.hypot(к[0] * 64 + 32 - аз["x"], к[1] * 64 + 56 - аз["y"]))
        _, _, култура, етап, жадно, мъртво = ниви[к]
        if мъртво:
            return "E = изчисти изсъхналото"
        if култура and етап >= 3:
            return "E = набери %s" % self._име_продукт(култура).lower()
        if not култура:
            return "E = засади %s   (Tab = друго семе)" % self._име_продукт(self._семе()).lower() if self._семе() else "Зима е - нищо не расте"
        if аз.get("bucket", 0) > 0 and жадно:
            return "E = полей (кофата: %d)" % аз["bucket"]
        if жадно:
            return "Нивата е жадна - напълни кофата на кладенеца"
        return "%s расте..." % self._име_продукт(култура)

    def _магазин_e(self, аз, роля):
        """Подсказките на продавача и касиера."""
        клиенти = sorted((п for п in self.персони.values() if п.get("map") == "magazin" and п.get("list")),
                         key=lambda п: п["y"])
        пред = [п for п in клиенти if math.hypot(п["x"] - аз["x"], п["y"] - аз["y"]) <= 230]
        if not пред:
            return "Чакаш клиенти"
        к = min(пред, key=lambda п: math.hypot(п["x"] - аз["x"], п["y"] - аз["y"]))
        if роля == "продавач" and not к.get("basket"):
            return "E = сложи стоката на %s: %s" % (к["name"], ", ".join("%s x%d" % (self._име_продукт(п).lower(), б) for п, б in к["list"].items()))
        if к.get("basket") and роля == "касиер":
            стока = {self._име_продукт(п).lower(): б for п, б in к["basket"].items()}
            return ("E = маркирай: %d лв (дава %d)" % (к.get("bill", 0), к.get("pays", 0)), "till",
                    {"сметка": к.get("bill", 0), "дава": к.get("pays", 0), "стока": стока})
        return "Касиерът маркира" if к.get("basket") else "Продавачът слага стоката"

    def _до_обект(self, аз, име, разстояние=110):
        for о in self.карта["objects"]:
            if о["name"] == име:
                д = self.плочки.get(име, {"w": 1, "h": 1})
                cx, cy = (о["x"] + д["w"] / 2) * tiles.ПЛОЧКА, (о["y"] + д["h"]) * tiles.ПЛОЧКА
                if math.hypot(cx - аз["x"], cy - аз["y"]) <= разстояние + д["w"] * 20:
                    return True
        return False

    def _църква_e(self, аз, роля):
        ц = self.църква
        if роля == "звънар":
            if self.моя_карта == "selo" and getattr(self, "село_инфо", None) and self.село_инфо.get("камбанария") \
                    and self._близо(аз, self.село_инфо["камбанария"], 100):
                return ("E = бий камбаните!", "church", "bells") if ц.get("bells") else "Камбаните бият по пладне и в 18:00"
            return "Иди на камбанарията (до църквата)" if ц.get("bells") else "Камбаните бият по пладне и в 18:00"
        if self.моя_карта != "tsarkva":
            if ц.get("rite"):
                return "Днес има %s - иди в църквата!" % ц["rite"]
            return "Църквата е в селото, вдясно"
        if not ц.get("candles") and self._до_обект(аз, "svechnik"):
            return ("E = запали свещите", "church", "candles")
        if ц.get("rite") == "сватба" and self._до_обект(аз, "ikonostas"):
            return ("E = венчай младоженците", "church", "сватба")
        if ц.get("rite") == "кръщене" and self._до_обект(аз, "kupel"):
            return ("E = кръсти бебето", "church", "кръщене")
        if ц.get("rite"):
            return "Днес има %s - иди до %s" % (ц["rite"], "иконостаса" if ц["rite"] == "сватба" else "купела")
        return "Свещите горят" if ц.get("candles") else "Сутрин: запали свещите (свещника вляво)"

    def _помощник_e(self, аз, роля):
        """Подсказките за снабдителя и чистача (и собственика). None = нищо от тези."""
        д = self.склад_данни
        if роля in ("свещеник", "звънар"):
            return self._църква_e(аз, роля)
        if self.моя_карта == "selo" and getattr(self, "село_инфо", None) is None:
            self._ферма_e(аз, роля)                    # зарежда data/selo.json
        if self.моя_карта == "selo" and роля in ("селянин", "собственик"):
            т = self._ферма_e(аз, роля)
            if т or роля == "селянин":
                return т
        if роля in ("продавач", "касиер"):
            return self._магазин_e(аз, роля) if self.моя_карта == "magazin" else "Магазинът е в селото"
        if аз.get("hold") == "shtayga":
            if self._до_мебел(аз, д.get("склад", ["shelf"])):
                return "E = разтовари в склада"
            return "Носиш щайга с продукти - занеси я в склада (рафта)"
        if роля in ("чистач", "собственик") and аз.get("hold", "") in ("", "chiniya_mrasna"):
            н = аз.get("plates", 0)
            if н and self._до_мебел(аз, [д.get("мивка", "sink")]):
                return ("E = измий чиниите (%d)" % н, "wash", н)
            if н < д.get("носи_чинии", 4) and any(math.hypot(x - аз["x"], y - аз["y"]) <= poruchki.ДО_ГОСТ
                                                  for x, y in self.мръсни):
                return "E = вземи мръсната чиния"
            if н:
                return "Носиш %d мръсни чинии - занеси ги на мивката" % н
        пазар_тук = (self._до_мебел(аз, ["sergia"]) if self.моя_карта == "selo"
                     else not self.карти.get("selo") and self._до_мебел(аз, [д.get("пазар", "door")]))
        if роля in ("снабдител", "собственик") and not аз.get("hold") and пазар_тук:
            списък = sklad.за_пазар(д, self.склад)
            if not списък:
                return "В склада има от всичко (K = виж склада)"
            имена = [д["продукти"][к]["име"].lower() for к in списък]
            return "E = иди на пазара: %s%s  (-%d)" % (", ".join(имена[:4]), "..." if len(имена) > 4 else "",
                                                     sklad.цена_на_пазар(д, списък))
        if роля == "снабдител":
            малко = sklad.за_пазар(д, self.склад)
            if not малко:
                return "Складът е пълен (K = виж)"
            if self.карти.get("selo") and self.моя_карта == "krachma":
                return "Свършват продукти - пазарът е в селото (излез през вратата долу)"
            return "Свършват продукти - иди до сергиите на пазара" if self.моя_карта == "selo" else "Свършват продукти - иди до вратата (пазара)"
        if роля == "чистач":
            return "Мръсните чинии са по масите" if self.мръсни else "Всичко е чисто"
        return None

    # ---------- прозорецът на собственика (M) ----------
    РАЗДЕЛИ = ("Цени", "Заплати", "Персонал", "Пазар")

    def _редове_управление(self):
        """[(ключ, текст вляво, стойност, бележка)] за избрания раздел."""
        у, раздел = self.упр, self.управление["раздел"]
        предмети = self.меню.get("предмети", {})
        if раздел == 0:
            return [(к, предмети.get(к, {}).get("име", к), в, "нормална %d" % предмети.get(к, {}).get("цена", 0))
                    for к, в in у.get("prices", {}).items()]
        if раздел == 1:
            база = self.склад_данни.get("заплати", {})
            return [(к, к, в, "нормална %d" % база.get(к, 0)) for к, в in у.get("wages", {}).items()]
        if раздел == 2:
            заплати = у.get("wages", {})
            return [(пид, "%s (%s)" % (о["name"], о["role"]), "уволнен" if пид in у.get("fired", []) else "работи",
                     "заплата %d" % заплати.get(о["role"], 0))
                    for пид, о in self.описания.items() if о["role"] in заплати]
        продукти = self.склад_данни.get("продукти", {})
        return [(к, п["име"], в, "пакет %d порции за %d   (в склада %d)" % (п["пакет"], п["цена"], self.склад.get(к, 0)))
                for к, в in у.get("packs", {}).items() for п in [продукти.get(к, {"име": к, "пакет": 1, "цена": 0})]]

    def _клавиш_управление(self, к):
        у = self.управление
        редове = self._редове_управление()
        if к in (pygame.K_ESCAPE, pygame.K_m):
            self.управление = None
        elif к in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d, pygame.K_TAB):
            у["раздел"] = (у["раздел"] + (-1 if к in (pygame.K_LEFT, pygame.K_a) else 1)) % len(self.РАЗДЕЛИ)
            у["ред"] = 0
        elif к in (pygame.K_UP, pygame.K_w):
            у["ред"] = max(0, у["ред"] - 1)
        elif к in (pygame.K_DOWN, pygame.K_s):
            у["ред"] = min(len(редове) - 1, у["ред"] + 1)
        elif редове and self.връзка:
            ключ, _, стойност, _ = редове[min(у["ред"], len(редове) - 1)]
            промяна = 1 if к in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS) else -1 if к in (pygame.K_MINUS, pygame.K_KP_MINUS) else 0
            if у["раздел"] == 2 and к in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                self.връзка.прати({"t": "manage", "op": "hire" if стойност == "уволнен" else "fire", "key": ключ})
            elif промяна and у["раздел"] != 2:
                оп = ("price", "wage", None, "pack")[у["раздел"]]
                self.връзка.прати({"t": "manage", "op": оп, "key": ключ, "value": стойност + промяна})

    def _звезди(self, стойност):
        цели = int(round(стойност))
        return "★" * цели + "☆" * (5 - цели)

    def _нарисувай_управление(self, екран):
        у, ш_, в_ = self.управление, *екран.get_size()
        редове = self._редове_управление()
        кутия = pygame.Rect(0, 0, 720, 520)
        кутия.center = (ш_ // 2, в_ // 2)
        фон = pygame.Surface(кутия.size, pygame.SRCALPHA)
        фон.fill((24, 16, 10, 240))
        екран.blit(фон, кутия)
        pygame.draw.rect(екран, (220, 180, 90), кутия, 3, border_radius=6)
        екран.blit(self.голям.render("Кръчмата", True, (255, 230, 150)), (кутия.x + 20, кутия.y + 10))
        зв = self.упр.get("rep", 3)
        т = self.шрифт.render("Име на кръчмата: %s %.1f" % (self._звезди(зв), зв), True, (255, 210, 90))
        екран.blit(т, (кутия.right - т.get_width() - 20, кутия.y + 18))
        x = кутия.x + 20
        for и, име in enumerate(self.РАЗДЕЛИ):                     # разделите
            т = self.шрифт.render(име, True, (30, 20, 10) if и == у["раздел"] else (230, 220, 200))
            r = pygame.Rect(x, кутия.y + 58, т.get_width() + 24, 30)
            pygame.draw.rect(екран, (255, 210, 90) if и == у["раздел"] else (70, 50, 34), r, border_radius=6)
            екран.blit(т, т.get_rect(center=r.center))
            x = r.right + 8
        у["ред"] = min(у["ред"], max(0, len(редове) - 1))
        от = max(0, у["ред"] - 11)                                  # дълъг списък: превърта се
        for и, (ключ, текст, стойност, бележка) in enumerate(редове[от:от + 12]):
            y = кутия.y + 104 + и * 24
            if и + от == у["ред"]:
                pygame.draw.rect(екран, (90, 64, 40), (кутия.x + 12, y - 2, кутия.w - 24, 23), border_radius=4)
            екран.blit(self.малък.render(текст, True, (240, 235, 220)), (кутия.x + 24, y))
            цвят = (255, 110, 90) if стойност == "уволнен" else (255, 230, 150)
            т = self.шрифт.render(str(стойност), True, цвят)
            екран.blit(т, (кутия.x + 330 - т.get_width(), y - 2))
            екран.blit(self.малък.render(бележка, True, (170, 160, 140)), (кутия.x + 350, y))
        подсказка = ("Enter = наеми / уволни" if у["раздел"] == 2 else "+ / - = смени")
        екран.blit(self.малък.render("← → раздел    ↑ ↓ ред    %s    M = затвори" % подсказка, True, (200, 190, 170)),
                   (кутия.x + 20, кутия.y + 400))
        обяснение = ("Скъпо = повече пари от всяко ястие, но идват по-малко гости и името пада.",
                     "Ниска заплата = персоналът работи по-бавно; висока = по-бързо.",
                     "Уволненият не работи и не взима заплата - но работата му остава.",
                     "Колко пакета купува снабдителят, когато нещо свършва.")[у["раздел"]]
        екран.blit(self.малък.render(обяснение, True, (150, 200, 230)), (кутия.x + 20, кутия.y + 376))
        мнения = self.упр.get("opinions", [])[-4:]                    # какво казват гостите
        екран.blit(self.малък.render("Какво казват гостите:", True, (200, 190, 170)), (кутия.x + 20, кутия.y + 426))
        for и, м in enumerate(reversed(мнения)):
            текст = "%s %s: „%s“ %s" % (м.get("час", ""), м.get("име", ""), м.get("текст", ""), "★" * м.get("звезди", 0))
            екран.blit(self.малък.render(текст, True, (230, 220, 200)), (кутия.x + 30, кутия.y + 446 + и * 18))

    def _нарисувай_пазар(self, екран):
        """P: пазарът (колко стока има и по колко е) и магазинът; сезонът и времето."""
        ш, в = екран.get_size()
        кутия = pygame.Rect(0, 0, 680, 470)
        кутия.center = (ш // 2, в // 2)
        фон = pygame.Surface(кутия.size, pygame.SRCALPHA)
        фон.fill((14, 22, 16, 240))
        екран.blit(фон, кутия)
        pygame.draw.rect(екран, (140, 200, 120), кутия, 3, border_radius=6)
        екран.blit(self.голям.render("Пазарът", True, (200, 255, 180)), (кутия.x + 20, кутия.y + 10))
        if self.ферма.get("season"):
            т = self.шрифт.render("%s, днес: %s" % (self.ферма["season"].capitalize(), self.ферма.get("weather", "")), True, (200, 230, 255))
            екран.blit(т, (кутия.right - т.get_width() - 20, кутия.y + 18))
        екран.blit(self.малък.render("Сергиите (местно: колкото по-малко, толкова по-скъпо)", True, (200, 190, 170)), (кутия.x + 20, кутия.y + 58))
        for и, (к, (брой, цена)) in enumerate(self.ферма.get("market", {}).items()):
            y = кутия.y + 84 + и * 24
            екран.blit(render.картинка_предмет(self.склад_данни.get("продукти", {}).get(к, {}).get("икона", к), 16), (кутия.x + 24, y + 2))
            цвят = (255, 140, 110) if брой < 10 else (230, 230, 220)
            екран.blit(self.малък.render("%s: %d бр." % (self._име_продукт(к), брой), True, цвят), (кутия.x + 48, y))
            т = self.малък.render("%.2f лв/бр." % цена, True, цвят)
            екран.blit(т, (кутия.x + 300 - т.get_width(), y))
        маг = self.магазин
        if маг:
            x = кутия.x + 340
            екран.blit(self.малък.render("Магазинът (каса %d лв)" % маг.get("cash", 0), True, (200, 190, 170)), (x, кутия.y + 58))
            for и, (к, брой) in enumerate(маг.get("stock", {}).items()):
                y = кутия.y + 84 + и * 24
                екран.blit(self.малък.render("%s: %d бр. по %d лв" % (self._име_продукт(к), брой, маг.get("prices", {}).get(к, 0)),
                                             True, (255, 140, 110) if брой < 3 else (230, 230, 220)), (x, y))
        н = self.малък.render("P = затвори", True, (200, 190, 170))
        екран.blit(н, (кутия.right - н.get_width() - 16, кутия.bottom - 30))

    def _нарисувай_склад(self, екран):
        д = self.склад_данни
        продукти = list(д.get("продукти", {}).items())
        ш, в = екран.get_size()
        редове = (len(продукти) + 1) // 2
        кутия = pygame.Rect(0, 0, 640, 120 + редове * 30)
        кутия.center = (ш // 2, в // 2)
        фон = pygame.Surface(кутия.size, pygame.SRCALPHA)
        фон.fill((24, 16, 10, 235))
        екран.blit(фон, кутия)
        pygame.draw.rect(екран, (170, 116, 64), кутия, 3, border_radius=6)
        екран.blit(self.голям.render("Склад", True, (255, 230, 150)), (кутия.x + 20, кутия.y + 10))
        праг = д.get("праг", 3)
        for и, (к, п) in enumerate(продукти):
            x = кутия.x + 20 + (и % 2) * 310
            y = кутия.y + 60 + (и // 2) * 30
            екран.blit(render.картинка_предмет(п.get("икона", к), 16), (x, y + 4))
            брой = self.склад.get(к, 0)
            цвят = (255, 110, 90) if брой < 1 else (255, 210, 90) if брой < праг else (230, 230, 220)
            екран.blit(self.малък.render(п["име"], True, цвят), (x + 24, y + 3))
            т = self.малък.render(str(брой), True, цвят)
            екран.blit(т, (x + 280 - т.get_width(), y + 3))
        y = кутия.bottom - 54
        мръсни = len(self.мръсни)
        екран.blit(self.малък.render("Чисти чинии: %d     Мръсни по масите: %d" % (self.чисти_чинии, мръсни),
                                     True, (190, 220, 255)), (кутия.x + 20, y))
        if self.моя_роля() == "собственик" and self.днес:
            д2 = self.днес
            екран.blit(self.малък.render("Днес: приходи %d   бакшиши %d   продукти -%d   гости %d"
                                         % (д2.get("приходи", 0), д2.get("бакшиши", 0), д2.get("продукти", 0),
                                            д2.get("обслужени", 0)), True, (150, 230, 150)), (кутия.x + 20, y + 24))
        н = self.малък.render("K = затвори", True, (200, 190, 170))
        екран.blit(н, (кутия.right - н.get_width() - 16, кутия.y + 16))

    def _нарисувай_отчет(self, екран):
        о = self.отчет
        ш, в = екран.get_size()
        редове = []
        for к, брой in о.get("продажби", {}).items():
            цена = self.меню.get("предмети", {}).get(к, {}).get("цена", 0)
            редове.append(("   %s x %d" % (self.меню.get("предмети", {}).get(к, {}).get("име", к), брой), "+%d" % (цена * брой), (230, 230, 220)))
        редове.append(("Приходи от гостите", "+%d" % о.get("приходи", 0), (150, 230, 150)))
        редове.append(("Продукти от пазара", "-%d" % о.get("продукти", 0), (255, 160, 130)))
        for име, сума in о.get("заплати", {}).items():
            редове.append(("   заплата: %s" % име, "-%d" % сума, (255, 190, 160)))
        редове.append(("Заплати общо", "-%d" % о.get("заплати_общо", 0), (255, 160, 130)))
        печалба = о.get("печалба", 0)
        редове.append(("ПЕЧАЛБА", ("+%d" if печалба >= 0 else "%d") % печалба, (120, 255, 120) if печалба >= 0 else (255, 90, 80)))
        кутия = pygame.Rect(0, 0, 620, 170 + len(редове) * 24)
        кутия.center = (ш // 2, в // 2)
        фон = pygame.Surface(кутия.size, pygame.SRCALPHA)
        фон.fill((24, 16, 10, 240))
        екран.blit(фон, кутия)
        pygame.draw.rect(екран, (220, 180, 90), кутия, 3, border_radius=6)
        заглавие = self.голям.render("Ден %d - кръчмата затвори" % о.get("ден", 0), True, (255, 230, 150))
        екран.blit(заглавие, заглавие.get_rect(midtop=(кутия.centerx, кутия.y + 12)))
        инфо = "Обслужени гости: %d     Ядосани: %d     Бакшиши за персонала: %d" % (
            о.get("обслужени", 0), о.get("ядосани", 0), о.get("бакшиши", 0))
        екран.blit(self.малък.render(инфо, True, (220, 210, 190)), (кутия.x + 24, кутия.y + 60))
        for и, (текст, сума, цвят) in enumerate(редове):
            y = кутия.y + 92 + и * 24
            екран.blit(self.малък.render(текст, True, цвят), (кутия.x + 24, y))
            т = self.малък.render(сума, True, цвят)
            екран.blit(т, (кутия.right - 24 - т.get_width(), y))
        if о.get("неплатени"):
            екран.blit(self.малък.render("Няма пари за заплатите на: " + ", ".join(о["неплатени"]), True, (255, 90, 80)),
                       (кутия.x + 24, кутия.bottom - 60))
        if "репутация" in о:
            т = self.малък.render("Име на кръчмата: %s %.1f" % (self._звезди(о["репутация"]), о["репутация"]), True, (255, 210, 90))
            екран.blit(т, (кутия.right - 24 - т.get_width(), кутия.y + 60 + 20))
        if о.get("магазин") or о.get("утре"):
            м = о.get("магазин") or {}
            утре = о.get("утре") or {}
            т = "Магазинът: %d клиента, приходи %d, стока -%d, заплати -%d.   Утре: %s, %s%s" % (
                м.get("клиенти", 0), м.get("приходи", 0), м.get("доставка", 0), м.get("заплати", 0),
                утре.get("сезон", ""), утре.get("време", ""), (" - " + утре["празник"]) if утре.get("празник") else "")
            if о.get("гощавка"):
                екран.blit(self.малък.render("Гощавка (сватба/кръщене): +%d" % о["гощавка"], True, (255, 210, 140)),
                           (кутия.x + 24, кутия.bottom - 108))
            екран.blit(self.малък.render(т, True, (180, 220, 255)), (кутия.x + 24, кутия.bottom - 84))
        екран.blit(self.малък.render("В касата на собственика: %d" % о.get("каса", 0), True, (255, 230, 150)),
                   (кутия.x + 24, кутия.bottom - 36))
        н = self.малък.render("Enter = нов ден", True, (200, 190, 170))
        екран.blit(н, (кутия.right - н.get_width() - 20, кутия.bottom - 36))

    def _поръчват(self):
        import world
        return world.ПОРЪЧВАТ_МУЗИКА

    def _музикант_до_мен(self, рисувани, аз):
        """NPC музикантът, ако е близо до мен и аз мога да му поръчам песен."""
        import world
        if not аз or self.моя_роля() not in world.ПОРЪЧВАТ_МУЗИКА:
            return None
        for п in рисувани:
            if (п.get("role") == "музикант" and п.get("ctrl") == "npc"
                    and ((п["x"] - аз["x"]) ** 2 + (п["y"] - аз["y"]) ** 2) ** 0.5 <= world.ДО_МУЗИКАНТА):
                return п
        return None

    def обнови_музика_npc(self):
        """Пуска (или спира) песента, която свири NPC музикантът. По-тихо, когато сме далеч."""
        if self.свирене:                     # аз свиря в минииграта: тя си пуска музиката
            self.музика_npc = None
            return
        import world
        аз = self.персони.get(self.мое_id) if self.екран_вид == "игра" else None
        най, разст = None, 1e9
        if аз:
            for п in self.персони.values():
                if п.get("song"):
                    р = ((п["до_x"] - аз["до_x"]) ** 2 + (п["до_y"] - аз["до_y"]) ** 2) ** 0.5
                    if р < разст:
                        най, разст = п, р
        чува = най is not None and разст < 14 * tiles.ПЛОЧКА
        try:
            if not pygame.mixer.get_init():
                if not чува:
                    return
                pygame.mixer.init(22050, -16, 1, 512)
            if not чува:
                if self.музика_npc:
                    pygame.mixer.music.fadeout(800)
                    self.музика_npc = None
                return
            ключ = (най["id"], най["song"])
            if ключ != self.музика_npc:
                път = os.path.join(world.ПАПКА_МУЗИКА, най["song"] + ".ogg")
                self.музика_npc = ключ
                if not os.path.exists(път):
                    return                       # песен без запис: само се вижда, че свири
                pygame.mixer.music.load(път)
                pygame.mixer.music.play(start=max(0.0, float(най.get("song_t", 0))))
            сила = 1.0 - max(0.0, разст - 4 * tiles.ПЛОЧКА) / (10 * tiles.ПЛОЧКА)
            pygame.mixer.music.set_volume(max(0.15, min(1.0, сила)))
        except pygame.error:
            self.музика_npc = None               # няма звукова карта: играта продължава без звук

    def започни_свирене(self):
        import svirene
        self.свирене = svirene.Свирене("kaval", изглед=self.изглед_около_мен)
        self.време_настроение = 0.0
        if self.връзка:
            self.връзка.прати({"t": "play", "on": True})

    def обнови_свирене(self):
        """Вика се всеки кадър; когато песента свърши, казва на сървъра резултата."""
        if not self.свирене:
            return
        self.свирене.обнови()
        сега = time.perf_counter()
        if self.връзка and self.свирене.етап == "свири" and сега - self.време_настроение > 0.5:
            self.връзка.прати({"t": "mood", "mood": round(self.свирене.настроение, 2)})
            self.време_настроение = сега
        if self.свирене.край:
            if self.връзка:
                self.връзка.прати({"t": "play", "on": False, "result": self.свирене.резултат})
            self.свирене = None


class Прозорец:
    """Прозорец, който се разтяга, и цял екран. Рисуваме на малък екран и го уголемяваме
    с цяло число, за да остане пикселната графика остра; около него остават тъмни ленти."""

    def __init__(self):
        self.цял_екран = False
        self.размер_прозорец = (ШИРИНА, ВИСОЧИНА)
        self.повърхност = None
        self.отвори()
        self.екран = None
        self.мащаб = 1
        self.отместване = (0, 0)

    def отвори(self):
        if self.цял_екран:
            self.повърхност = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.повърхност = pygame.display.set_mode(self.размер_прозорец, pygame.RESIZABLE)

    def смени_цял_екран(self):
        if not self.цял_екран:
            self.размер_прозорец = self.повърхност.get_size()
        self.цял_екран = not self.цял_екран
        self.отвори()

    def преоразмерен(self, размер):
        if not self.цял_екран:
            self.размер_прозорец = (max(МИН_ШИРИНА, размер[0]), max(МИН_ВИСОЧИНА, размер[1]))
            if self.размер_прозорец != tuple(размер):
                self.отвори()

    def подготви(self, вид):
        """Връща повърхността, на която да рисуваме в този кадър."""
        W, H = self.повърхност.get_size()
        if вид == "свирене":
            # миниигрите са с платно 960x540: на Full HD точно x2
            размер = (960, 540)
            self.мащаб = max(1, min(W // 960, H // 540))
            if W < 960 or H < 540:
                self.мащаб = min(W / 960, H / 540)
        elif вид == "игра":
            # колкото по-голям прозорецът, толкова повече от картата се вижда
            self.мащаб = max(1, H // ВИСОЧИНА_ЗА_УГОЛЕМЕНИЕ)
            размер = (W // self.мащаб, H // self.мащаб)
        else:
            # менютата са с фиксиран размер, в средата
            self.мащаб = max(1, min(W // ШИРИНА, H // ВИСОЧИНА))
            if W < ШИРИНА or H < ВИСОЧИНА:      # малък прозорец: менюто се смалява, за да се побере
                self.мащаб = min(W / ШИРИНА, H / ВИСОЧИНА)
            размер = (ШИРИНА, ВИСОЧИНА)
        if self.екран is None or self.екран.get_size() != размер:
            self.екран = pygame.Surface(размер)
        голям = (int(размер[0] * self.мащаб), int(размер[1] * self.мащаб))
        self.отместване = ((W - голям[0]) // 2, (H - голям[1]) // 2)
        return self.екран

    def покажи(self):
        self.повърхност.fill((0, 0, 0))
        голям = pygame.transform.scale(self.екран, (int(self.екран.get_width() * self.мащаб),
                                                     int(self.екран.get_height() * self.мащаб)))   # scale, не smoothscale
        self.повърхност.blit(голям, self.отместване)
        pygame.display.flip()

    def мишка(self, позиция):
        """Позиция на мишката в прозореца -> позиция върху малкия екран."""
        return (int((позиция[0] - self.отместване[0]) / self.мащаб), int((позиция[1] - self.отместване[1]) / self.мащаб))


def самопроверка():
    """python main.py --selftest (или RealLife.exe --selftest): играе сама за няколко секунди
    и записва selftest.txt до играта. Ползва го build.bat, за да провери готовия .exe."""
    import traceback
    изход = os.path.join(tiles.ПАПКА, "selftest.txt")
    os.environ["REALLIFE_BEZ_ZAPIS"] = "1"          # пробата не пипа запазената игра
    try:
        pygame.init()
        pygame.display.set_mode((960, 540))
        игра = Игра(pygame.font.SysFont("arial", 20), pygame.font.SysFont("arial", 14),
                    pygame.font.SysFont("arial", 40, bold=True))
        игра.играй_сам()
        def чакай(условие):
            край = time.time() + 5
            while not условие() and time.time() < край:
                игра.обработи_мрежата()
                time.sleep(0.05)
            assert условие()
        чакай(lambda: игра.екран_вид == "избор")
        игра.избери("muzikant")
        чакай(lambda: игра.екран_вид == "игра")
        екран = pygame.Surface((1024, 576))
        игра.нарисувай(екран, False, 60)
        игра.клавиш(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e, mod=0))
        assert игра.свирене and игра.свирене.списък, "няма песни"
        игра.свирене.клавиш(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0))
        игра.свирене.обнови()
        игра.свирене.нарисувай(pygame.Surface((960, 540)))
        песни = len(игра.свирене.списък)
        игра.прекъсни()
        with open(изход, "w", encoding="utf-8") as f:
            f.write("OK: играта, сървърът, картинките и минииграта работят (%d песни)\n" % песни)
        return 0
    except Exception:
        with open(изход, "w", encoding="utf-8") as f:
            f.write("ГРЕШКА:\n" + traceback.format_exc())
        return 1


def главна():
    if "--selftest" in sys.argv:
        sys.exit(самопроверка())
    покажи_fps = "--fps" in sys.argv
    pygame.init()
    pygame.display.set_caption("Real Life")
    прозорец = Прозорец()
    if "--full" in sys.argv:
        прозорец.смени_цял_екран()
    игра = Игра(pygame.font.SysFont("arial", 20), pygame.font.SysFont("arial", 14),
                pygame.font.SysFont("arial", 40, bold=True))
    игра.преобразувай_мишка = прозорец.мишка
    часовник = pygame.time.Clock()
    pygame.key.start_text_input()
    работи = True
    while работи:
        часовник.tick(КАДРИ_В_СЕКУНДА)
        сега = time.perf_counter()
        for с in pygame.event.get():
            if с.type == pygame.QUIT:
                работи = False
            elif с.type == pygame.VIDEORESIZE:
                прозорец.преоразмерен(с.size)
            elif с.type == pygame.TEXTINPUT:
                игра.текст(с.text)
            elif с.type == pygame.KEYDOWN:
                if с.key == pygame.K_F3:
                    покажи_fps = not покажи_fps
                elif с.key == pygame.K_F11 or (с.key == pygame.K_RETURN and с.mod & pygame.KMOD_ALT):
                    прозорец.смени_цял_екран()
                elif игра.миниигра():
                    игра.миниигра().клавиш(с)
                elif not игра.клавиш(с):
                    работи = False
            elif с.type == pygame.KEYUP and игра.миниигра():
                игра.миниигра().клавиш(с)
            elif с.type == pygame.MOUSEBUTTONDOWN and с.button == 1:
                игра.клик(прозорец.мишка(с.pos))
            elif с.type == pygame.MOUSEBUTTONDOWN and с.button == 3:
                игра.десен_клик(прозорец.мишка(с.pos))
            elif с.type == pygame.MOUSEWHEEL:
                игра.колело(с.y)
        игра.обработи_мрежата()
        к = pygame.key.get_pressed()
        dx = (к[pygame.K_d] or к[pygame.K_RIGHT]) - (к[pygame.K_a] or к[pygame.K_LEFT])
        dy = (к[pygame.K_s] or к[pygame.K_DOWN]) - (к[pygame.K_w] or к[pygame.K_UP])
        игра.изпрати_вход(dx, dy, сега)
        игра.обнови_свирене()
        игра.обнови_готвене()
        игра.обнови_музика_npc()
        if игра.миниигра():
            екран = прозорец.подготви("свирене")
            игра.миниигра().нарисувай(екран)
        else:
            екран = прозорец.подготви(игра.екран_вид)
            игра.нарисувай(екран, покажи_fps, часовник.get_fps())
        прозорец.покажи()
    игра.прекъсни()
    pygame.quit()


if __name__ == "__main__":
    главна()
