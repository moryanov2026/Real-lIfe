# Прави проект за Piskel (.piskel) от готова PNG картинка, за да може всеки да продължи рисунката.
# Отваря се в Piskel: панел "Open" (папката) -> "Browse .piskel files".
# Пускане:  python tools/to_piskel.py assets/table.png      -> art_src/table.piskel
import base64
import json
import os
import struct
import sys

ПАПКА = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def размер_png(данни):
    w, h = struct.unpack(">II", данни[16:24])
    return w, h


def направи(път_png, папка_изход=os.path.join(ПАПКА, "art_src")):
    with open(път_png, "rb") as f:
        данни = f.read()
    w, h = размер_png(данни)
    име = os.path.splitext(os.path.basename(път_png))[0]
    слой = {"name": "Layer 1", "opacity": 1, "frameCount": 1,
            "chunks": [{"layout": [[0]],
                        "base64PNG": "data:image/png;base64," + base64.b64encode(данни).decode()}]}
    проект = {"modelVersion": 2,
              "piskel": {"name": име, "description": "Real Life - " + име, "fps": 12,
                         "height": h, "width": w, "layers": [json.dumps(слой)], "hiddenFrames": []}}
    os.makedirs(папка_изход, exist_ok=True)
    изход = os.path.join(папка_изход, име + ".piskel")
    with open(изход, "w", encoding="utf-8") as f:
        json.dump(проект, f)
    return изход


if __name__ == "__main__":
    for п in sys.argv[1:]:
        print("OK ", направи(п))
