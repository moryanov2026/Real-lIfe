const P = require("./codixel/core/pixel.js");
const ref = P.load("ref.png");
const bez = P.trim(P.removeBg(ref, { tol: 70, erode: 2, flood: false }), 0);
const malak = P.resize(bez, 120);
const ramp = P.hueRamp(6, { hue: 215, sat: 0.12, shift: 40, light: [0.06, 0.48] });
// яркост на всеки пиксел -> стъпка от рампата: плоски ивици, смесени само в тънка ивица на границата (P.band)
const L = (c) => { const [r, g, b] = P.unpack(c); return 0.3 * r + 0.59 * g + 0.11 * b; };
const vse = []; for (const c of malak.px) if (c >>> 24) vse.push(L(c)); vse.sort((a, b) => a - b);
const ранг = (l) => { let a = 0, b = vse.length; while (a < b) { const m = (a + b) >> 1; if (vse[m] < l) a = m + 1; else b = m; } return a / vse.length; };
// изглаждане 3x3 на яркостта: махаме зърното на чугуна, остават обръчите и светлината
const W = malak.w, H = malak.h, ярк = new Float32Array(W * H).fill(-1);
for (let i = 0; i < W * H; i++) if (malak.px[i] >>> 24) ярк[i] = L(malak.px[i]);
const глад = (x, y) => { let s = 0, n = 0; for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
  const X = x + dx, Y = y + dy; if (X < 0 || Y < 0 || X >= W || Y >= H) continue; const v = ярк[Y * W + X]; if (v >= 0) { s += v; n++; } } return s / n; };
const out = new P.Buf(malak.w, malak.h);
for (let y = 0; y < malak.h; y++) for (let x = 0; x < malak.w; x++) {
  const c = malak.px[y * malak.w + x];
  if (!(c >>> 24)) continue;
  const v = Math.min(0.999, 0.15 + ранг(глад(x, y)) * 0.85);   // по процентил: всички стъпки се ползват
  out.px[y * malak.w + x] = ramp[P.band(v, ramp.length, x, y, 0.12)];
}
const chist = P.smoothEdge(P.cleanup(out, { tol: 20 }));
P.save(chist, "2_pikseli.png");
console.log(chist.w, chist.h, P.colorCount(chist).map(e => e.share.toFixed(2)).join(" "));
P.save(P.ruler(chist, 5, { step: 8 }), "ruler.png");
P.save(P.sheet([{ buf: ref, label: "SNIMKA" }, { buf: chist, label: "PIKSELI", scale: 3 }], { fit: 270 }), "sheet.png");
