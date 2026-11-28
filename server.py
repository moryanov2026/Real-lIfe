# СЪРВЪР на Real Life. Държи целия свят и решава какво става (GAME_RULES, раздел 3а).
# Самостоятелно пускане (за класа):  python server.py      или  server.bat
# Играта (main.py) може да пусне сървър и сама: "Играй сам" и "Създай игра за класа".
import json
import os
import queue
import socket
import sys
import threading
import time

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import net
import tiles
import world

ТИКОВЕ_В_СЕКУНДА = 20            # колко пъти в секунда се смята светът и се праща на клиентите
ТАЙМАУТ_ИЗПРАЩАНЕ = 10           # секунди: ако клиент не приема данни толкова дълго, го изключваме


class Пощальон:
    """Всеки клиент има свой пощальон (отделна нишка), който му праща съобщенията.
    Така, ако един компютър увисне, само неговият пощальон чака, а играта продължава за всички.
    Състоянието на света се пази само най-новото: ако клиентът изостава, старите се прескачат."""

    def __init__(self, сокет, при_грешка):
        self.сокет = сокет
        self.при_грешка = при_грешка
        self.сокет.settimeout(ТАЙМАУТ_ИЗПРАЩАНЕ)
        self.важни = []                 # welcome, picked, error: не се губят
        self.състояние = None           # само последното
        self.условие = threading.Condition()
        self.работи = True
        threading.Thread(target=self._работи, daemon=True).start()

    def прати(self, данни, важно):
        with self.условие:
            if важно:
                self.важни.append(данни)
            else:
                self.състояние = данни
            self.условие.notify()

    def спри(self):
        with self.условие:
            self.работи = False
            self.условие.notify()

    def _работи(self):
        while True:
            with self.условие:
                while self.работи and not self.важни and self.състояние is None:
                    self.условие.wait()
                if not self.работи:
                    return
                за_пращане = self.важни + ([self.състояние] if self.състояние else [])
                self.важни, self.състояние = [], None
            try:
                for данни in за_пращане:
                    self.сокет.sendall(данни)
            except OSError:              # прекъсната връзка или увиснал повече от 10 секунди
                self.при_грешка()
                return


ЗАПИС = os.path.normpath(os.path.join(os.path.dirname(world.ПЪТ_КАРТА), "..", "saves", "krachma.json"))   # построеното в режим B


class Сървър:
    def __init__(self, хост="0.0.0.0", порт=net.ПОРТ, път_карта=world.ПЪТ_КАРТА,
                 папка_персони=world.ПАПКА_ПЕРСОНИ, запис=None):
        # запис = файл, в който се пази построеното (режим B); ако го има, кръчмата се зарежда от него
        self.запис = запис
        if запис and os.path.exists(запис):
            път_карта = запис
        self.свят = world.Свят(път_карта, папка_персони)
        self.слушател = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.слушател.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.слушател.bind((хост, порт))          # порт 0 = избери свободен (за "Играй сам")
        self.слушател.listen()
        self.порт = self.слушател.getsockname()[1]
        self.опашка = queue.Queue()                # всичко от мрежата минава оттук, по ред
        self.клиенти = {}                          # номер -> {"сокет", "име"}
        self.работи = False
        self._следващ_номер = 1

    def старт(self):
        self.работи = True
        threading.Thread(target=self._приемай, daemon=True).start()
        threading.Thread(target=self._цикъл, daemon=True).start()
        return self

    def спри(self):
        self.работи = False
        try:
            self.слушател.close()
        except OSError:
            pass
        for к in list(self.клиенти.values()):
            try:
                к["сокет"].close()
            except OSError:
                pass

    # ---------- нишки за мрежата ----------
    def _приемай(self):
        while self.работи:
            try:
                сокет, _ = self.слушател.accept()
            except OSError:
                break
            сокет.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)   # без забавяне на малките съобщения
            номер = self._следващ_номер
            self._следващ_номер += 1
            self.опашка.put(("ново", номер, сокет))
            threading.Thread(target=self._чети, args=(номер, сокет), daemon=True).start()

    def _чети(self, номер, сокет):
        четец = net.Четец(сокет)
        try:
            while True:
                съобщения = четец.чети()
                if съобщения is None:
                    break
                for с in съобщения:
                    self.опашка.put(("съобщение", номер, с))
        except (OSError, ValueError):
            pass
        self.опашка.put(("край", номер, None))

    # ---------- главният цикъл: само тук се пипа светът ----------
    def _цикъл(self):
        стъпка = 1.0 / ТИКОВЕ_В_СЕКУНДА
        следващ = time.perf_counter()
        while self.работи:
            self._обработи_опашката()
            self.свят.обнови(стъпка)
            съобщение = {"t": "state"}
            съобщение.update(self.свят.състояние())
            self._до_всички(съобщение)
            следващ += стъпка
            пауза = следващ - time.perf_counter()
            if пауза > 0:
                time.sleep(пауза)
            else:
                следващ = time.perf_counter()     # изоставаме: не гоним, продължаваме

    def _обработи_опашката(self):
        while True:
            try:
                вид, номер, данни = self.опашка.get_nowait()
            except queue.Empty:
                return
            if вид == "ново":
                self.клиенти[номер] = {"сокет": данни, "име": "?",
                                       "пощальон": Пощальон(данни, lambda н=номер: self.опашка.put(("край", н, None)))}
            elif вид == "край":
                self._махни(номер)
            else:
                self._съобщение(номер, данни)

    def _съобщение(self, номер, с):
        к = self.клиенти.get(номер)
        if not к or not isinstance(с, dict):
            return
        т = с.get("t")
        if т == "hello":
            к["име"] = (str(с.get("name", "")).strip() or "Играч")[:20]
            self._прати(номер, {"t": "welcome", "id": номер, "map": self.свят.карта,
                                "persons": self.свят.описания()})
        elif т == "pick":
            if self.свят.вземи(с.get("person"), номер, к["име"]):
                self._прати(номер, {"t": "picked", "person": с.get("person")})
            else:
                self._прати(номер, {"t": "error", "text": "Тази персона вече е заета."})
        elif т == "input":
            self.свят.вход(номер, с.get("dx", 0), с.get("dy", 0))
        elif т == "leave_person":
            self.свят.освободи(номер)
        elif т == "build":                      # режим за строене: сложи / вдигни / разшири
            успех, текст = self.свят.строй(номер, с.get("op"), с.get("name"), с.get("x", 0), с.get("y", 0), с.get("side"))
            self._прати(номер, {"t": "build_result", "ok": успех, "text": текст})
            if успех:
                self._до_всички_важно({"t": "map", "map": self.свят.карта})
                if self.запис:
                    os.makedirs(os.path.dirname(self.запис), exist_ok=True)
                    tiles.запиши_карта(self.свят.карта, self.запис)
        elif т == "use":                        # E: гостът поръчва; персоналът приготвя / взима / сервира
            успех, текст = self.свят.използвай(номер)
            if текст:
                self._прати(номер, {"t": "use_result", "ok": успех, "text": текст})
        elif т == "cook":                       # ученик изигра мини играта при готвенето
            успех, текст = self.свят.сготви(номер, с.get("item"), с.get("quality", 0.6))
            if текст:
                self._прати(номер, {"t": "use_result", "ok": успех, "text": текст})
        elif т == "order_song":                 # E до музиканта: собственикът поръчва песен
            успех, текст = self.свят.поръчай_песен(номер)
            self._прати(номер, {"t": "order_result", "ok": успех, "text": текст})
        elif т == "sit":                        # F: седни / стани
            self.свят.сядане(номер)
        elif т == "mood":                       # миниигра "Свирене": колко добре свири (за хорото)
            self.свят.ново_настроение(номер, с.get("mood", 0))
        elif т == "play":                       # миниигра "Свирене": начало / край на песен
            бакшиш = self.свят.свирене(номер, с.get("on"), с.get("result"))
            if not с.get("on") and isinstance(с.get("result"), dict):
                self._прати(номер, {"t": "tip", "amount": бакшиш, "percent": с["result"].get("percent", 0)})

    def _прати(self, номер, с):
        к = self.клиенти.get(номер)
        if к:
            к["пощальон"].прати((json.dumps(с, ensure_ascii=False) + "\n").encode("utf-8"), важно=True)

    def _до_всички(self, с):
        данни = (json.dumps(с, ensure_ascii=False) + "\n").encode("utf-8")   # кодираме веднъж
        for к in list(self.клиенти.values()):
            к["пощальон"].прати(данни, важно=False)

    def _до_всички_важно(self, с):
        for номер in list(self.клиенти):
            self._прати(номер, с)

    def _махни(self, номер):
        к = self.клиенти.pop(номер, None)
        if к:
            к["пощальон"].спри()
            self.свят.освободи(номер)
            try:
                к["сокет"].close()
            except OSError:
                pass


def главна():
    порт = int(sys.argv[1]) if len(sys.argv) > 1 else net.ПОРТ
    сървър = Сървър(порт=порт, запис=ЗАПИС).старт()
    print("=" * 50)
    print("  Real Life - сървърът работи")
    print("  Учениците въвеждат адрес:  %s" % net.мой_ip())
    print("  (порт %d)   Спиране: Ctrl+C" % сървър.порт)
    print("=" * 50)
    try:
        while True:
            time.sleep(5)
            хора = [п for п in сървър.свят.персони.values() if п.контролер is not None]
            print("Играчи: %d  |  %s" % (len(хора), ", ".join("%s=%s" % (п.играч, п.име) for п in хора)))
    except KeyboardInterrupt:
        сървър.спри()


if __name__ == "__main__":
    главна()
