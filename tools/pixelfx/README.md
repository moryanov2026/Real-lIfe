# Ефекти от PixelFX (огън, пара...)

Ефектите са от библиотеката PixelFX (https://github.com/patch-gg/pixelfx, MIT License,
Copyright (c) 2026 Patch and Hugo Duprez). Огънят е техният `fire/campfire`.
Парата `pot-steam.js` е нов ефект, направен за Real Life (сложи го в `src/fx/nature/` на PixelFX).

Как се правят лентите в assets/fx (трябва Node 18+):

    git clone --depth 1 https://github.com/patch-gg/pixelfx
    cd pixelfx
    node tools/render.mjs fire/campfire --sheet --fps 15 --bg none --opts '{"height":10}'   # малък огън
    node tools/render.mjs fire/campfire --sheet --fps 15 --bg none --opts '{"height":16}'   # среден
    node tools/render.mjs fire/campfire --sheet --fps 15 --bg none --opts '{"height":24}'   # голям
    node tools/render.mjs nature/pot-steam --sheet --fps 15 --bg none --opts '{"strength":3,"count":30,"palette":["#e4eaf2","#f4f7fb","#ffffff","#ffffff"]}'   # пара

Всеки дава .png (кадрите в мрежа) и .json (размер, колони, fps, pivot = точката, която стои на мястото).
Копирайте ги в assets/fx/ с имената ogan_malak, ogan_sreden, ogan_golyam, para. Играта ги чете в gotvene.py.
