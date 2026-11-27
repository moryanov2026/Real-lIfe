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
pygame.image.save(прозорец, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_to_delete", "test_igra.png"))
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

# 6в) Режим за строене: собственикът купува, вдига и разширява; музикантът не може
с8 = world.Свят(семе=4)
с8.вземи("sobstvenik", 81, "учител"); с8.вземи("muzikant", 82, "ученик")
пари = с8.персони["sobstvenik"].пари
assert с8.строй(81, "place", "barrel", 19, 2)[0]
assert с8.персони["sobstvenik"].пари == пари - с8.цени["barrel"][1]
assert not с8.строй(81, "place", "barrel", 19, 2)[0], "сложи върху заето"
assert not с8.строй(82, "place", "barrel", 20, 2)[0], "музикантът строи"
assert с8.строй(81, "remove", x=19, y=2)[0] and с8.персони["sobstvenik"].пари == пари
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
print("OK: сървър, двама играчи, заета персона, ходене, NPC, сблъсъци, NPC поема при излизане, клиент, свирене, сядане, строене, редактор.")
