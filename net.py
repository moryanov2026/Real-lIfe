# Мрежа: как сървърът и клиентите си говорят.
# Всяко съобщение е един ред JSON (речник), завършващ с "\n". Само стандартната библиотека.
import json
import socket

ПОРТ = 5555                 # порт по подразбиране (GAME_RULES, раздел 3а)


def изпрати(сокет, съобщение):
    сокет.sendall((json.dumps(съобщение, ensure_ascii=False) + "\n").encode("utf-8"))


class Четец:
    """Събира парчетата от мрежата и ги реже на цели редове (съобщения)."""

    def __init__(self, сокет):
        self.сокет = сокет
        self.буфер = b""

    def чети(self):
        """Чака данни. Връща списък със съобщения или None, ако връзката е затворена."""
        данни = self.сокет.recv(65536)
        if not данни:
            return None
        self.буфер += данни
        съобщения = []
        while b"\n" in self.буфер:
            ред, self.буфер = self.буфер.split(b"\n", 1)
            if ред.strip():
                съобщения.append(json.loads(ред.decode("utf-8")))
        return съобщения


def мой_ip():
    """Адресът на този компютър в мрежата (него въвеждат учениците). Не праща нищо навън."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return "127.0.0.1"
