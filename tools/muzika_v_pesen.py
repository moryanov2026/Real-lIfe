# Превръща запис (mp3, wav, ogg, m4a) в песен за минииграта "Свирене".
# НАЙ-ЛЕСНО: влачи mp3 файла върху pesen.bat (или пусни pesen.bat и избери файла), напиши име - готово.
# Или от папката "Real Life":
#     python tools/muzika_v_pesen.py "път\до\песен.mp3" "Име на песента" kaval
# Резултат:
#     data/songs/<име>.json         нотите: кога започва всеки тон на мелодията и в коя лента е
#     assets/music/<име>.ogg        самата музика (с 3 секунди тишина отпред за броенето 3-2-1)
#     assets/music/<име>_melodiya.ogg  само мелодията (кавалът) - заглъхва в играта, когато пропуснеш
#     assets/music/<име>_fon.ogg       всичко без мелодията (съпровод) - свири винаги
# Как работи:
#   1. Отделя мелодията от ударите (librosa HPSS) и намира височината на тона във всеки момент (pYIN).
#   2. Нота = нов удар в мелодията или смяна на тона, която трае поне 60 мс.
#   3. Нотите се прилепват към ритъма (1/4 от удара), ако са на по-малко от 45 мс от него.
#   4. Лентата е според височината: ниските вляво, високите вдясно, с почти еднакво много ноти във всяка.
#   5. Мелодията се отделя от съпровода: знаем височината на тона във всеки момент, затова изрязваме
#      от записа точно тази честота и нейните хармоници (маска върху спектъра).
# Трябват: librosa и imageio-ffmpeg (install.bat ги слага). Не трябват на самата игра.
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

try:
    import librosa
    import numpy as np
except ImportError:
    print("Липсва библиотеката librosa. Пусни install.bat още веднъж (или: py -m pip install librosa imageio-ffmpeg).")
    input("Enter = изход ")
    sys.exit(1)

ПАПКА = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ТИШИНА = 3.0                  # секунди тишина отпред (броене 3-2-1)
НАЙ_МАЛКО = 0.15              # най-малко секунди между две ноти (по-близките са украшения)
ЛЕНТИ = {"kaval": 3, "gaida": 3, "gadulka": 4, "tambura": 4, "akordeon": 5}

ЛАТИНИЦА = dict(zip("абвгдежзийклмнопрстуфхцчшщъьюя",
                    ["a", "b", "v", "g", "d", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s",
                     "t", "u", "f", "h", "ts", "ch", "sh", "sht", "a", "y", "yu", "ya"]))


def файлово_име(име):
    име = "".join(ЛАТИНИЦА.get(б, б) for б in име.lower())
    return re.sub(r"[^a-z0-9]+", "_", име).strip("_") or "pesen"


def ffmpeg():
    """ffmpeg от компютъра, а ако го няма - готовият от пакета imageio-ffmpeg."""
    път = shutil.which("ffmpeg")
    if път:
        return път
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        print("Липсва ffmpeg. Пусни install.bat още веднъж (или: py -m pip install imageio-ffmpeg).")
        input("Enter = изход ")
        sys.exit(1)


def избери_файл():
    """Прозорец за избор на файл (когато не е даден)."""
    try:
        import tkinter
        from tkinter import filedialog
        корен = tkinter.Tk()
        корен.withdraw()
        път = filedialog.askopenfilename(title="Избери песен (mp3, wav, ogg, m4a)",
                                         filetypes=[("Музика", "*.mp3 *.wav *.ogg *.m4a *.flac"), ("Всички", "*.*")])
        корен.destroy()
        return път
    except Exception:
        return input("Път до песента: ").strip().strip('"')


def раздели(път_wav44, tf, f0, папка, ffmpeg_път, ogg_мелодия, ogg_фон):
    """Мелодия = честотите на тона (основен + хармоници); фон = всичко останало."""
    import soundfile
    y, sr = librosa.load(път_wav44, sr=44100, mono=False)
    if y.ndim == 1:
        y = y[None, :]
    n_fft, hop = 4096, 1024
    честоти = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    мелодия, фон = [], []
    маска = None
    for канал in y:
        X = librosa.stft(канал, n_fft=n_fft, hop_length=hop)
        if маска is None:
            времена = librosa.frames_to_time(np.arange(X.shape[1]), sr=sr, hop_length=hop)
            f = np.interp(времена, tf, f0)
            гласно = np.interp(времена, tf, (f0 > 0).astype(float)) > 0.5
            маска = np.zeros(X.shape, dtype=np.float32)
            for j in np.nonzero(гласно)[0]:
                for к in range(1, 16):
                    h = f[j] * к
                    if h > 11000:
                        break
                    ширина = max(25.0, h * 0.035)
                    маска[:, j] = np.maximum(маска[:, j], np.clip(1 - np.abs(честоти - h) / ширина, 0, 1))
            маска = np.clip(маска * 1.6, 0, 1)
        мелодия.append(librosa.istft(X * маска, hop_length=hop, length=len(канал)))
        фон.append(librosa.istft(X * (1 - маска), hop_length=hop, length=len(канал)))
    for сигнал, изход in ((мелодия, ogg_мелодия), (фон, ogg_фон)):
        wav = os.path.join(папка, "част.wav")
        soundfile.write(wav, np.array(сигнал).T, sr)
        subprocess.run([ffmpeg_път, "-loglevel", "error", "-y", "-i", wav, "-af",
                        "adelay=%d:all=1" % int(ТИШИНА * 1000), "-ac", "2", "-ar", "44100",
                        "-c:a", "libvorbis", "-q:a", "4", изход], check=True)


def анализирай(път_wav):
    y, sr = librosa.load(път_wav, sr=22050)
    дължина = len(y) / sr
    h, _ = librosa.effects.hpss(y)
    hop = 256
    f0, _, _ = librosa.pyin(h, fmin=180, fmax=1600, sr=sr, frame_length=2048, hop_length=hop)
    tf = librosa.times_like(f0, sr=sr, hop_length=hop)
    f0 = np.nan_to_num(f0)
    # удари в мелодията
    env = librosa.onset.onset_strength(y=h, sr=sr, hop_length=hop)
    on = librosa.onset.onset_detect(onset_envelope=env, sr=sr, hop_length=hop, delta=0.07, wait=4)
    кандидати = list(librosa.frames_to_time(on, sr=sr, hop_length=hop))
    # смени на тона без нов удар
    midi = np.where(f0 > 0, librosa.hz_to_midi(np.where(f0 > 0, f0, 1)), np.nan)
    текуща = None
    стабилно = int(0.06 * sr / hop)
    for i in range(len(midi)):
        if np.isnan(midi[i]):
            текуща = None
            continue
        r = round(midi[i])
        if текуща is None or abs(r - текуща) >= 1:
            парче = midi[i:i + стабилно]
            if len(парче) == стабилно and not np.isnan(парче).any() and np.all(np.abs(парче - r) < 0.6):
                if текуща is not None:
                    кандидати.append(tf[i])
                текуща = r
    кандидати.sort()
    ноти = []
    for t in кандидати:
        if not ноти or t - ноти[-1] >= 0.09:
            ноти.append(t)
    # височина на всяка нота
    висоти = []
    for t in ноти:
        sel = (tf >= t + 0.01) & (tf < t + 0.13) & (f0 > 0)
        висоти.append(float(np.median(librosa.hz_to_midi(f0[sel]))) if sel.sum() >= 3 else None)
    ноти = [(t, в) for t, в in zip(ноти, висоти) if в is not None]
    # ритъм и прилепяне
    темпо, удари = librosa.beat.beat_track(y=y, sr=sr, hop_length=512)
    удари = librosa.frames_to_time(удари, sr=sr, hop_length=512)
    решетка = np.array([a + (b - a) * k / 4 for a, b in zip(удари[:-1], удари[1:]) for k in range(4)])
    прилепени = []
    for t, в in ноти:
        if len(решетка):
            i = int(np.argmin(np.abs(решетка - t)))
            if abs(решетка[i] - t) < 0.045:
                t = float(решетка[i])
        if not прилепени or t - прилепени[-1][0] >= НАЙ_МАЛКО:
            прилепени.append((t, в))
    return прилепени, float(np.atleast_1d(темпо)[0]), дължина, tf, f0


def главна():
    print("=== Песен за минииграта Свирене ===")
    вход = sys.argv[1] if len(sys.argv) > 1 else избери_файл()
    if not вход or not os.path.exists(вход):
        print("Няма такъв файл:", вход)
        return
    print("Файл:", os.path.basename(вход))
    if len(sys.argv) > 2:
        име = sys.argv[2]
    else:
        предложение = os.path.splitext(os.path.basename(вход))[0]
        име = input("Име на песента [%s]: " % предложение).strip() or предложение
    if len(sys.argv) > 3:
        инструмент = sys.argv[3]
    else:
        инструмент = input("Инструмент (kaval, gaida, gadulka, tambura, akordeon) [kaval]: ").strip() or "kaval"
    if инструмент not in ЛЕНТИ:
        print("Непознат инструмент, ползвам kaval")
        инструмент = "kaval"
    ленти = ЛЕНТИ.get(инструмент, 3)
    файл = файлово_име(име)
    os.makedirs(os.path.join(ПАПКА, "data", "songs"), exist_ok=True)
    os.makedirs(os.path.join(ПАПКА, "assets", "music"), exist_ok=True)
    with tempfile.TemporaryDirectory() as папка:
        wav = os.path.join(папка, "песен.wav")
        subprocess.run([ffmpeg(), "-loglevel", "error", "-y", "-i", вход, "-vn", "-ac", "1", "-ar", "22050", wav], check=True)
        print("Слушам песента и търся нотите... (около минута)")
        ноти, темпо, дължина, tf, f0 = анализирай(wav)
        if len(ноти) < 10:
            print("Не намерих мелодия в тази песен. Опитай с песен, в която инструментът или гласът се чуват ясно.")
            return
        print("Отделям мелодията от съпровода...")
        wav44 = os.path.join(папка, "песен44.wav")
        subprocess.run([ffmpeg(), "-loglevel", "error", "-y", "-i", вход, "-vn", "-ar", "44100", wav44], check=True)
        раздели(wav44, tf, f0, папка, ffmpeg(),
                os.path.join(ПАПКА, "assets", "music", файл + "_melodiya.ogg"),
                os.path.join(ПАПКА, "assets", "music", файл + "_fon.ogg"))
    # музиката: 3 секунди тишина отпред, ogg
    ogg = os.path.join(ПАПКА, "assets", "music", файл + ".ogg")
    subprocess.run([ffmpeg(), "-loglevel", "error", "-y", "-i", вход, "-vn", "-af",
                    "adelay=%d:all=1" % int(ТИШИНА * 1000), "-ac", "2", "-ar", "44100",
                    "-c:a", "libvorbis", "-q:a", "4", ogg], check=True)
    # ленти по височина: почти еднакво много ноти във всяка
    лад = sorted({round(в) for _, в in ноти})
    основа = лад[0]
    брой_тон = {м: sum(1 for _, в in ноти if round(в) == м) for м in лад}
    към_лента, натрупано = {}, 0
    for м in лад:                                  # всеки тон отива в една лента, редом по височина
        към_лента[м] = min(ленти - 1, int(ленти * (натрупано + брой_тон[м] / 2) / len(ноти)))
        натрупано += брой_тон[м]

    def лента(в):
        return към_лента[round(в)]

    песен = {"name": име, "kind": "запис", "meter": "%d уд./мин" % round(темпо),
             "groups": [2, 2], "eighth_ms": int(round(30000 / темпо)),
             "instrument": инструмент, "lanes": ленти, "length_s": round(дължина + ТИШИНА, 1),
             "base_hz": round(float(librosa.midi_to_hz(основа)), 2), "scale": [м - основа for м in лад],
             "recording": True,
             "notes": [[round(t + ТИШИНА, 3), лента(в), лад.index(round(в))] for t, в in ноти],
             "made_by": "tools/muzika_v_pesen.py от " + os.path.basename(вход)}
    with open(os.path.join(ПАПКА, "data", "songs", файл + ".json"), "w", encoding="utf-8") as f:
        json.dump(песен, f, ensure_ascii=False, indent=0)
    брой = [sum(1 for н in песен["notes"] if н[1] == л) for л in range(ленти)]
    print("Готово: %s - %d ноти (по ленти %s), темпо %d, %d:%02d мин" % (
        име, len(песен["notes"]), брой, round(темпо), int(песен["length_s"]) // 60, int(песен["length_s"]) % 60))
    print("  data/songs/%s.json, assets/music/%s.ogg (+ _melodiya.ogg и _fon.ogg)" % (файл, файл))
    print("Пусни играта, избери музиканта и натисни E - песента е в списъка.")


if __name__ == "__main__":
    главна()
