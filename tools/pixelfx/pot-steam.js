// Steam rising off a pot of soup (made for Real Life, Nikolay's student game).
import { cycle, hex, mix, WHITE } from "../../core/index.js";

export const meta = {
  name: "Pot steam",
  desc: "Soft white steam rising off a wide pot: thin wisps leave the surface, curl and swell as they climb, lit on their top-left side, and thin out until they are gone.",
  tags: ["steam", "vapour", "cooking", "soup", "pot", "ambient", "loop"],
  size: [112, 80],
  origin: [56, 76],
  duration: 3,
  loop: true,
  fps: 30,
  bg: "dark",
  options: { palette: ["#a9b2c4", "#d3d9e4", "#eef2f6", "#ffffff"], width: 36, count: 22, strength: 1, seed: 4 },
};

export function draw(p, t, o) {
  const C = o.palette.map(hex), W = o.width, S = o.strength;
  // each wisp is a short trail of soft discs following one rising, swaying path, so it reads as a ribbon, not balls
  cycle(t, meta.duration, o.count, o.seed, (g) => g.range(1.8, 2.8), (age, L, r) => {
    const x0 = r.range(-W, W), drift = r.range(-8, 8), ph = r.next() * 6.283, swell = r.range(0.8, 1.2), rise = r.range(13, 18);
    const path = (a) => {
      const k = a / L;
      return [x0 * (1 - k * 0.3) + drift * k + Math.sin(ph + a * 2.4) * (1 + k * 6), -a * rise - k * k * 8];
    };
    for (let s = 0; s < 6; s++) {
      const a = age - s * 0.09;
      if (a < 0) break;
      const k = a / L, [x, y] = path(a);
      const rad = (1.2 + k * 6.5) * swell * (1 - s * 0.06);
      const alpha = Math.min(1, k / 0.1) * Math.pow(1 - k, 1.5) * 0.42 * S * (1 - s * 0.12);
      if (alpha <= 0.01) continue;
      p.disc(x, y, rad, C[1], alpha * 0.8);
      p.disc(x - rad * 0.35, y - rad * 0.35, rad * 0.55, C[2], alpha * 0.8);
      if (k < 0.35 && s === 0) p.disc(x - rad * 0.4, y - rad * 0.45, Math.max(0.8, rad * 0.28), C[3], alpha);
    }
  });
}
