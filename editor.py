# Real Life - РЕДАКТОР НА КАРТИ. Тук подреждаме плочките (под, стени, предмети).
# Пускане:  python editor.py                (отваря data/maps/start.json)
#           python editor.py data/maps/kashta.json   (друга карта; ако я няма, прави нова)
#
# Мишка:   ляв бутон = слага избраната плочка, десен бутон = маха
#          колелце над лентата долу = превърта плочките
# Клавиши: стрелки/WASD = мести изгледа    Ctrl+S = запази    P = старт на героя
#          G = мрежа    F = запълни целия под с избрания под    R = презареди картинките
#          T = избраната плочка твърда/проходима    L = под/предмет
#          [ ] = по-тясна/по-широка карта    - = = по-ниска/по-висока    Esc = изход
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


class Редактор:
    def __init__(self, път):
        self.път = път
        self.карта = tiles.зареди_карта(път) if os.path.exists(път) else tiles.празна_карта()
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

    def преоразмери(self, dw, dh):
        ш = max(4, self.карта["width"] + dw)
        в = max(4, self.карта["height"] + dh)
        под = self.карта["floor"]
        под = [ред[:ш] + ["floor"] * (ш - len(ред)) for ред in под[:в]]
        под += [["floor"] * ш for _ in range(в - len(под))]
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
        if my < ВИСОЧИНА_ГОРЕ or my >= ПРОЗОРЕЦ_В - ВИСОЧИНА_ЛЕНТА:
            return None
        x = (mx // УВЕЛИЧЕНИЕ + self.кам_x) // ПЛОЧКА
        y = ((my - ВИСОЧИНА_ГОРЕ) // УВЕЛИЧЕНИЕ + self.кам_y) // ПЛОЧКА
        return int(x), int(y)

    def плочка_в_лентата(self, позиция):
        mx, my = позиция
        if my < ПРОЗОРЕЦ_В - ВИСОЧИНА_ЛЕНТА + 8:
            return None
        и = mx // (КУТИЯ_ИКОНА + 8) + self.отместване_лента
        return self.списък[и] if 0 <= и < len(self.списък) else None

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
        if клетка:
            д = self.плочки[self.избрана]
            призрак = self.картинки[self.избрана].copy()
            призрак.set_alpha(150)
            tiles.нарисувай_плочка(изглед, призрак, д, клетка[0], клетка[1], к_x, к_y)
            pygame.draw.rect(изглед, (255, 255, 255), (клетка[0] * ПЛОЧКА - к_x, клетка[1] * ПЛОЧКА - к_y,
                                                       д["w"] * ПЛОЧКА, д["h"] * ПЛОЧКА), 1)
        прозорец.blit(pygame.transform.scale(изглед, (изглед_ш * УВЕЛИЧЕНИЕ, изглед_в * УВЕЛИЧЕНИЕ)),
                      (0, ВИСОЧИНА_ГОРЕ))

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
        for име in self.списък[self.отместване_лента:]:
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

    # ---------- главен цикъл ----------
    def обработи_събитие(self, с):
        """Връща False, когато трябва да спрем."""
        if с.type == pygame.QUIT:
            return self.поискай_изход()
        if с.type == pygame.MOUSEWHEEL:
            if pygame.mouse.get_pos()[1] >= ПРОЗОРЕЦ_В - ВИСОЧИНА_ЛЕНТА:
                self.отместване_лента = max(0, min(len(self.списък) - 1, self.отместване_лента - с.y))
        if с.type == pygame.MOUSEBUTTONDOWN and с.button == 1:
            име = self.плочка_в_лентата(с.pos)
            if име:
                self.избрана = име
        if с.type == pygame.KEYDOWN:
            ctrl = с.mod & pygame.KMOD_CTRL
            if с.key == pygame.K_ESCAPE:
                return self.поискай_изход()
            self.изход_питане = False
            if с.key == pygame.K_s and ctrl:
                self.запази()
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
        if клетка and бутони[0]:
            р.сложи(*клетка)
        elif клетка and бутони[2]:
            р.махни(*клетка)
        р.нарисувай(прозорец, шрифт)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    главна()
