# Тест без прозорец: сървър, двама играчи, NPC, сблъсъци, клиентът и редакторът.
import os
import socket
import time

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame

import net
import server
import world


def клиент(порт, име):
    s = socket.create_connection(("127.0.0.1", порт))
    s.settimeout(3)
    return s, net.Четец(s)


def чакай(четец, вид):
    край = time.time() + 3
    while time.time() < край:
        for с in четец.чети() or []:
            if с.get("t") == вид:
                return с
    raise AssertionError("не дойде съобщение " + вид)


def последно_състояние(четец, сек=0.3):
    край = time.time() + сек
    посл = None
    while time.time() < край:
        for с in четец.чети() or []:
            if с.get("t") == "state":
                посл = с
    return {п["id"]: п for п in посл["persons"]}


pygame.init()
сър = server.Сървър(хост="127.0.0.1", порт=0).старт()
s1, ч1 = клиент(сър.порт, "Ани")
s2, ч2 = клиент(сър.порт, "Боби")
net.изпрати(s1, {"t": "hello", "name": "Ани"})
net.изпрати(s2, {"t": "hello", "name": "Боби"})
добре = чакай(ч1, "welcome")
assert len(добре["persons"]) >= 5 and "floor" in добре["map"]
чакай(ч2, "welcome")

# 1) Ани взима кръчмаря; Боби не може да вземе същия
net.изпрати(s1, {"t": "pick", "person": "krachmar"})
чакай(ч1, "picked")
net.изпрати(s2, {"t": "pick", "person": "krachmar"})
assert чакай(ч2, "error")
net.изпрати(s2, {"t": "pick", "person": "servitior"})
чакай(ч2, "picked")

# 2) Ани ходи надясно
преди = последно_състояние(ч1)
net.изпрати(s1, {"t": "input", "dx": 1, "dy": 0})
time.sleep(0.6)
net.изпрати(s1, {"t": "input", "dx": 0, "dy": 0})
след = последно_състояние(ч1)
assert след["krachmar"]["x"] > преди["krachmar"]["x"] + 40, "кръчмарят не тръгна"
assert след["krachmar"]["ctrl"] == "human" and след["krachmar"]["player"] == "Ани"

# 3) NPC се движат сами
npc_преди = {к: (п["x"], п["y"]) for к, п in след.items() if п["ctrl"] == "npc"}
time.sleep(3)
npc_след = последно_състояние(ч1)
мръднали = sum(1 for к, (x, y) in npc_преди.items() if (npc_след[к]["x"], npc_след[к]["y"]) != (x, y))
assert мръднали >= 3, "NPC не се движат"

# 4) Сблъсъци: бутаме Боби към горния ляв ъгъл, не бива да влезе в стена
net.изпрати(s2, {"t": "input", "dx": -1, "dy": -1})
time.sleep(4)
боби = сър.свят.персони["servitior"]
assert not any(боби.кутия().colliderect(о) for о in сър.свят.препятствия), "влезе в стена!"
for п in сър.свят.персони.values():
    if п.седи is not None:
        continue                                    # седналият е до масата: там му е мястото
    assert not any(п.кутия().colliderect(о) for о in сър.свят.препятствия), "%s е в стена" % п.id

# 5) Ани излиза -> кръчмарят става NPC
s1.close()
time.sleep(0.5)
assert сър.свят.персони["krachmar"].контролер is None, "NPC не пое персоната"
s2.close()
сър.спри()

# 6) Клиентът (main.py): играй сам, избери, ходи, нарисувай
import main
прозорец = pygame.display.set_mode((main.ШИРИНА, main.ВИСОЧИНА))
ш = pygame.font.SysFont("arial", 20)
игра = main.Игра(ш, pygame.font.SysFont("arial", 14), pygame.font.SysFont("arial", 40))
игра.име = "Тест"
игра.нарисувай(прозорец, True, 60)               # менюто
игра.играй_сам()
край = time.time() + 3
while игра.екран_вид != "избор" and time.time() < край:
    игра.обработи_мрежата(); time.sleep(0.05)
assert игра.екран_вид == "избор"
time.sleep(0.2); игра.обработи_мрежата()
игра.нарисувай(прозорец, False, 60)              # екранът за избор
игра.избери("muzikant")
край = time.time() + 3
while игра.екран_вид != "игра" and time.time() < край:
    игра.обработи_мрежата(); time.sleep(0.05)
assert игра.мое_id == "muzikant"
x0 = игра.персони["muzikant"]["x"]
for _ in range(20):
    игра.изпрати_вход(-1, 0, time.perf_counter()); time.sleep(0.03); игра.обработи_мрежата()
игра.изпрати_вход(0, 0, time.perf_counter())
time.sleep(0.2); игра.обработи_мрежата()
assert игра.персони["muzikant"]["x"] < x0, "музикантът не тръгна наляво"
# 6а) Музикантът свири: E отваря минииграта, сървърът вижда "свири", после дава бакшиш
игра.клавиш(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e, mod=0))
assert игра.свирене is not None, "E не отвори минииграта"
игра.свирене.клавиш(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0))
св = игра.свирене
assert св.етап == "свири" and len(св.ноти) > 100
първа = св.ноти[0]
св.начало = time.perf_counter() * 0 + pygame.time.get_ticks() / 1000.0 - (първа.t - 0.02)
св._удари(първа.лента, първа.t - 0.02)
assert първа.оценка == "Перфектно", първа.оценка
втора = св.ноти[1]
св._удари(втора.лента, втора.t - 0.08)
assert втора.оценка == "Добре", втора.оценка
time.sleep(0.3); игра.обработи_мрежата()
assert игра.персони["muzikant"].get("play") is True, "сървърът не видя, че свири"
пари = игра.персони["muzikant"]["money"]
св._приключи(); св.резултат["percent"] = 100.0; св.край = True
игра.обнови_свирене()
time.sleep(0.4); игра.обработи_мрежата()
assert игра.персони["muzikant"]["money"] > пари, "няма бакшиш"
assert not игра.персони["muzikant"].get("play")
игра.нарисувай(прозорец, True, 60)
папка_снимки = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_to_delete")
os.makedirs(папка_снимки, exist_ok=True)   # папката не идва от GitHub, правим я, ако я няма
pygame.image.save(прозорец, os.path.join(папка_снимки, "test_igra.png"))
игра.прекъсни()

# 6б) Сядане: до стол F = седни, тръгне ли = става
с7 = world.Свят(семе=3)
с7.вземи("krachmar", 77, "тест")
п7 = с7.персони["krachmar"]
assert с7.места, "няма столове на картата"
м7 = с7.места[0]
п7.x, п7.y = м7["x"] + 30, м7["y"]
assert с7.сядане(77) and п7.седи == 0 and п7.състояние()["sit"] == м7["dir"]
с7.вход(77, 1, 0); с7.обнови(0.05)
assert п7.седи is None, "не стана, когато тръгна"

# 6г) Поръчка на песен: собственикът казва на NPC музиканта да свири, след малко започва хорото
с9 = world.Свят(семе=5)
с9.вземи("sobstvenik", 91, "учител")
соб, муз = с9.персони["sobstvenik"], с9.персони["muzikant"]
соб.x, соб.y = муз.x + 400, муз.y
assert not с9.поръчай_песен(91)[0], "поръча отдалеч"
соб.x, соб.y = муз.x + 60, муз.y
успех, текст = с9.поръчай_песен(91)
assert успех and муз.свири and муз.песен, текст
for п in с9.персони.values():                    # всички наблизо, за да има хоро
    if п is not муз and п is not соб:
        п.x, п.y = муз.x + 80, муз.y + 40
с9.обнови(1.0)
assert not any(п.хоро for п in с9.персони.values()), "хорото тръгна веднага"
for _ in range(60):
    с9.обнови(0.1)
assert any(п.хоро for п in с9.персони.values()), "никой не се хвана на хорото"
assert муз.състояние()["song"] and not муз.върви
assert с9.поръчай_песен(91)[0] and not муз.свири, "не спря"
с9.вземи("muzikant", 92, "ученик")
assert not с9.поръчай_песен(91)[0], "поръча на музикант-играч"

# 6д) Поръчки: гостът поръчва, кръчмарят приготвя, сервитьорът носи, касата расте
с10 = world.Свят(семе=6)
с10.вземи("krachmar", 101, "к"); с10.вземи("servitior", 102, "с"); с10.вземи("baba_stana", 103, "г")
кр, ср, гст = с10.персони["krachmar"], с10.персони["servitior"], с10.персони["baba_stana"]
бар = next(с for с in с10.станции_списък if с[3] == "rakia")
assert not с10.използвай(103)[0], "поръча прав"
и = min(range(len(с10.места)), key=lambda и: с10.места[и]["y"])
гст.x, гст.y = с10.места[и]["x"], с10.места[и]["y"] + 20
assert с10.сядане(103)
гст.иска = None; assert с10.използвай(103)[0] and гст.иска
гст.иска = "rakia"
кр.x, кр.y = с10.център((бар[0], бар[1] + 1))
ср.x, ср.y = кр.x, кр.y
assert not с10.използвай(102)[0], "сервитьорът приготви ракия"
assert с10.използвай(101)[0] and (бар[0], бар[1]) in с10.станции
for _ in range(60):
    с10.обнови(0.05)
assert с10.станции[(бар[0], бар[1])]["готово"]
assert с10.използвай(102)[0] and ср.носи == "rakia"
ср.x, ср.y = гст.x + 400, гст.y
assert not с10.използвай(102)[0], "сервира отдалеч"
каса = с10.персони["sobstvenik"].пари
ср.x, ср.y = гст.x, гст.y - 60
assert с10.използвай(102)[0] and гст.яде == "rakia" and not ср.носи
assert с10.персони["sobstvenik"].пари > каса, "касата не порасна"
# NPC персоналът сам обслужва гостите
с11 = world.Свят(семе=7)
каса = с11.персони["sobstvenik"].пари
for _ in range(20 * 150):
    с11.обнови(0.05)
assert с11.персони["sobstvenik"].пари > каса, "NPC персоналът не сервира нищо"

# 6ж) Мини игра при готвенето: изиграната ракия е готова веднага, с качеството от играта
с13 = world.Свят(семе=9)
с13.вземи("krachmar", 131, "к")
кр = с13.персони["krachmar"]
бар = next(с for с in с13.станции_списък if с[3] == "rakia")
кр.x, кр.y = с13.център((бар[0], бар[1] + 1))
assert not с13.сготви(131, "shopska", 1.0)[0], "кръчмарят направи салата"
assert с13.сготви(131, "rakia", 0.95)[0]
ст = next(в for в in с13.станции.values() if в["предмет"] == "rakia")
assert ст["готово"] and ст["качество"] == 0.95
assert с13.използвай(131)[0] and кр.носи == "rakia" and кр.качество == 0.95
import gotvene
г = gotvene.Готвене("bob", "Боб")
г.клавиш(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=0))
г.обнови(); г.нарисувай(pygame.Surface((960, 540)))
г.клавиш(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=0))
assert г.край and г.резултат is None
с = gotvene.Стъпка("lyutenitsa", "Лютеница", вид="лютеница")   # лютеницата: без бъркане загаря
с.клавиш(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=0))
for _ in range(16 * 20):
    с._обнови_лютеница(0.05)
    if с.етап != "игра":
        break
с.нарисувай(pygame.Surface((960, 540)))
assert с.етап == "резултат" and с.качество < 0.4 and с.загоряло > 3, (с.качество, с.загоряло)
# рецептите: всяка стъпка е позната мини игра; избор на ястие и минаване през всички стъпки
рец = gotvene.рецепти()
assert set(рец) >= {"rakia", "vino", "shopska", "bob", "hlyab", "lyutenitsa"}
for ключ, стъпки in рец.items():
    for ст in стъпки:
        assert hasattr(gotvene.Стъпка, "_начало_" + ст["игра"]), (ключ, ст)
екран = pygame.Surface((960, 540))
г = gotvene.Готвене([("shopska", "Шопска салата", True), ("hlyab", "Хляб", False)])
г.нарисувай(екран)
г.клавиш(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT, mod=0))
assert г.предмет == "hlyab"
г.клавиш(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT, mod=0))
г.клавиш(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=0))
for н in range(len(рец["shopska"])):                    # всяка стъпка: почни, изиграй, нарисувай, свърши
    ст = г.стъпка
    ст.клавиш(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=0))
    ст.нарисувай(екран)
    ст._готово(0.5 + 0.1 * н)
    ст.от -= 5
    г.обнови()
assert г.етап == "готово" and len(г.качества) == len(рец["shopska"])
г.нарисувай(екран)
г.клавиш(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=0))
assert г.край and г.резултат["item"] == "shopska" and 0.5 < г.резултат["quality"] < 0.9
г = gotvene.Готвене("bob")                              # целият боб по рецептата, без да натискаме нищо
for н, ст_данни in enumerate(рец["bob"]):
    ст = г.стъпка
    ст.клавиш(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=0))
    for _ in range(40 * 20):                            # без натискане: стъпката свършва сама
        getattr(ст, "_обнови_" + ст.вид)(0.05)
        ст.от -= 0.05
        ст.кадър_време += 0.05
        if ст.етап != "игра":
            break
    ст.нарисувай(екран)
    assert ст.етап == "резултат" and ст.качество < 0.45, (н, ст.вид, ст.качество)
    ст.от -= 5
    г.обнови()
assert г.етап == "готово" and len(г.качества) == len(рец["bob"])
имена = [н["име"] for н in г.съдържание["тенджера"]]
assert {"студена вода", "боб", "моркови", "джоджен", "запръжка"} <= set(имена), имена
assert not г.съдържание["тиган"], "запръжката остана в тигана"
assert any(в["предмет"] == "lyutenitsa" for в in с13.станции.values()) or any(с[3] == "lyutenitsa" for с in с13.станции_списък)

# 6е) NPC персоналът не сяда, гостите сядат
с12 = world.Свят(семе=8)
седнали = set()
for _ in range(20 * 60):
    с12.обнови(0.05)
    седнали |= {п.id for п in с12.персони.values() if п.седи is not None}
assert седнали and all(с12.гост(с12.персони[и]) for и in седнали), "седна персонал: %s" % седнали

# 6в) Режим за строене: собственикът купува, вдига и разширява; музикантът не може
с8 = world.Свят(семе=4)
с8.вземи("sobstvenik", 81, "учител"); с8.вземи("muzikant", 82, "ученик")
пари = с8.персони["sobstvenik"].пари
assert с8.строй(81, "place", "barrel", 21, 2)[0]
assert с8.персони["sobstvenik"].пари == пари - с8.цени["barrel"][1]
assert not с8.строй(81, "place", "barrel", 21, 2)[0], "сложи върху заето"
assert not с8.строй(82, "place", "barrel", 22, 2)[0], "музикантът строи"
assert с8.строй(81, "remove", x=21, y=2)[0] and с8.персони["sobstvenik"].пари == пари
ширина = с8.колони
assert с8.строй(81, "expand", страна="right")[0] and с8.колони > ширина

# 7) Редакторът още работи
import editor
р = editor.Редактор(world.ПЪТ_КАРТА)
р.избрана = "table"; р.сложи(5, 5)
assert р.обект_в(5, 5)["name"] == "table"
р.махни(5, 5)
pygame.display.set_mode((editor.ПРОЗОРЕЦ_Ш, editor.ПРОЗОРЕЦ_В))
р.нарисувай(pygame.display.get_surface(), ш)
print("OK: сървър, двама играчи, заета персона, ходене, NPC, сблъсъци, NPC поема при излизане, клиент, свирене, сядане, поръчка на песен, поръчки, мини игри при готвенето, строене, редактор.")
