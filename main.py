# Real Life - ИГРАТА (клиент). Етап 3а: много играчи през локален сървър.
# Пускане:  python main.py   (или start.bat).  С брояч кадри:  python main.py --fps
#
# Меню:  "Играй сам"            - сървърът се пуска на този компютър, всички други са NPC
#        "Създай игра за класа" - този компютър е сървър, учениците влизат с неговия адрес
#        "Влез в игра"          - въвеждаш адреса на сървъра (напр. 192.168.1.20)
# В играта: WASD/стрелки = ходене, Esc = смени персона, F3 = кадри в секунда
# Музикантът: E = свири (миниигра "Свирене", svirene.py)
# F11 или Alt+Enter = цял екран / прозорец. Прозорецът се разтяга с мишката.  python main.py --full = направо на цял екран
import os
import queue
import socket
import sys
import threading
import time

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

import net
import render
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
        self.известие = None                 # (текст, до кога) - напр. бакшиш след песен

    # ---------- свързване ----------
    def играй_сам(self):
        import server
        self.сървър = server.Сървър(хост="127.0.0.1", порт=0).старт()
        self.свържи("127.0.0.1", self.сървър.порт)

    def създай_за_класа(self):
        import server
        try:
            self.сървър = server.Сървър(хост="0.0.0.0", порт=net.ПОРТ).старт()
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
            elif т == "tip":
                self.известие = ("Песента: %d %%  -  бакшиш +%d" % (round(с.get("percent", 0)), с.get("amount", 0)),
                                 time.perf_counter() + 5)
            elif т == "_closed":
                self.връзка = None
                self.екран_вид = "меню"
                self.мое_id = None
                self.съобщение = "Връзката със сървъра прекъсна."

    def _ново_състояние(self, с):
        сега = time.perf_counter()
        self.ден, self.минути = с["day"], с["minutes"]
        for п in с["persons"]:
            стар = self.персони.get(п["id"])
            нов = dict(self.описания.get(п["id"], {}))
            нов.update(п)
            # за изглаждане: тръгваме от там, където го рисуваме в момента
            if стар:
                нов["от_x"], нов["от_y"] = self._позиция(стар, сега)
            else:
                нов["от_x"], нов["от_y"] = п["x"], п["y"]
            нов["до_x"], нов["до_y"] = п["x"], п["y"]
            нов["кога"] = сега
            self.персони[п["id"]] = нов

    def _позиция(self, п, сега):
        к = min(1.0, (сега - п["кога"]) / ИНТЕРВАЛ_ТИК)
        return п["от_x"] + (п["до_x"] - п["от_x"]) * к, п["от_y"] + (п["до_y"] - п["от_y"]) * к

    # ---------- в играта ----------
    def изпрати_вход(self, dx, dy, сега):
        if not self.връзка or self.екран_вид != "игра":
            return
        if self.свирене:
            dx = dy = 0                       # докато свири, не ходи
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
        render.нарисувай_карта(екран, self.карта, self.плочки, self.картинки, кам_x, кам_y, рисувани)
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
            pygame.draw.rect(екран, (90, 200, 90), (690, 10, int(аз.get("energy", 0) * 1.5), 14))
        хора = sum(1 for п in рисувани if п.get("ctrl") == "human")
        екран.blit(self.малък.render("Играчи: %d" % хора, True, (200, 200, 200)), (860, 9))
        if self.адрес_за_класа:
            н = self.шрифт.render("Адрес за учениците: %s" % self.адрес_за_класа, True, (255, 220, 60))
            екран.blit(н, (10, в - 30))
        if аз and self.моя_роля() == "музикант":
            н = self.шрифт.render("E = свири на кавала", True, (255, 230, 150))
            екран.blit(н, (ш - н.get_width() - 12, в - 30))
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
                return

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
        elif self.екран_вид == "игра" and к == pygame.K_ESCAPE:
            self.смени_персона()
        elif self.екран_вид == "игра" and к == pygame.K_e and self.моя_роля() == "музикант":
            self.започни_свирене()
        return True

    # ---------- миниигра "Свирене" ----------
    def моя_роля(self):
        return self.описания.get(self.мое_id, {}).get("role", "")

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
                elif игра.свирене:
                    игра.свирене.клавиш(с)
                elif not игра.клавиш(с):
                    работи = False
            elif с.type == pygame.KEYUP and игра.свирене:
                игра.свирене.клавиш(с)
            elif с.type == pygame.MOUSEBUTTONDOWN and с.button == 1:
                игра.клик(прозорец.мишка(с.pos))
        игра.обработи_мрежата()
        к = pygame.key.get_pressed()
        dx = (к[pygame.K_d] or к[pygame.K_RIGHT]) - (к[pygame.K_a] or к[pygame.K_LEFT])
        dy = (к[pygame.K_s] or к[pygame.K_DOWN]) - (к[pygame.K_w] or к[pygame.K_UP])
        игра.изпрати_вход(dx, dy, сега)
        игра.обнови_свирене()
        if игра.свирене:
            екран = прозорец.подготви("свирене")
            игра.свирене.нарисувай(екран)
        else:
            екран = прозорец.подготви(игра.екран_вид)
            игра.нарисувай(екран, покажи_fps, часовник.get_fps())
        прозорец.покажи()
    игра.прекъсни()
    pygame.quit()


if __name__ == "__main__":
    главна()
