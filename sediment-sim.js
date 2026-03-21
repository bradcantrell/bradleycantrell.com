/*
 * ═══════════════════════════════════════════════════════════════════════════
 *  SEDIMENT FLUME SIMULATION
 *
 *  Single source at left edge. Obstacle grid disrupts flow, forcing
 *  particles to deflect, slow, and deposit. Deposited sediment further
 *  deflects subsequent passes. Landscape builds and evolves over time.
 *
 *  Bradley Cantrell — UVA School of Architecture / Landscape Architecture
 *
 *  Usage:
 *    SedimentSim.start('canvas-id')               // full-window sizing
 *    SedimentSim.start('canvas-id', parentEl)     // size to parent element
 *    SedimentSim.addTextObstacles(['h1', '.foo'])  // seed text as obstacles
 * ═══════════════════════════════════════════════════════════════════════════
 */
'use strict';

const SedimentSim = (() => {

const CFG = {
  FLOW_DIR:         'right',
  GRID_SCALE:       4,        // px per terrain cell

  // Emitter — continuous streams that slowly drift their Y origin over time
  EMITTER_SPREAD:   0.08,     // perpendicular spread around the main vector
  EMITTER_COUNT:    4,        // number of simultaneous streams
  // Streams never expire — they drift smoothly so emission is uninterrupted
  DRIFT_SPEED:      0.0015,   // how fast the stream Y drifts toward its target (per frame)

  // Particles
  MAX_PARTICLES:    4000,     // soft ceiling — spawn probability tapers as pool fills
  LIFE_MIN:         3500,     // long life — slow particles need time to cross
  LIFE_MAX:         5000,

  // Viscous physics — terminal velocity = GRAVITY / (1 - BASE_DRAG)
  // 0.018 / (1 - 0.972) = 0.64 px/frame → ~38px/sec at 60fps — thick, slow
  SPEED_INIT:       0.5,      // gentle birth push — immediately feels viscous
  SPEED_SPREAD:     0.1,
  GRAVITY:          0.018,    // forward drive — just enough to win over drag
  LATERAL_NOISE:    0.015,    // slow lateral wander
  BASE_DRAG:        0.972,    // high friction — viscous medium
  TERRAIN_FRICTION: 0.060,    // extra drag per unit terrain height

  // Obstacle grid
  OBSTACLE_COUNT:   55,       // number of fixed obstacles
  OBSTACLE_RADIUS:  18,       // pixel radius — influence zone (larger = softer approach)
  OBSTACLE_STRENGTH:0.28,     // gentle lateral nudge — water finding its way around a rock
  OBSTACLE_FORWARD_KILL: 0.88,// retain most forward momentum — mud oozes around, doesn't stop
  OBSTACLE_DEPOSIT: 0.012,    // sediment deposited in obstacle wake per frame of contact
  // Obstacles placed in a staggered grid with noise, avoiding left 10% and right 5%

  // Sediment transport
  SEDIMENT_INIT:    0.80,     // particles start heavier — more to deposit
  DROP_RATE:        0.55,     // deposit aggressively on deceleration
  TERRAIN_DROP_MOD: 4.0,      // strong positive feedback — sediment begets sediment
  PICKUP_SPEED:     0.28,     // higher threshold — terrain harder to erode once built
  PICKUP_RATE:      0.006,    // slower erosion — net deposition wins
  MAX_SEDIMENT:     1.0,      // allow full saturation

  // Terrain relaxation — slower so deposits hold their shape longer
  RELAX_RATE:       0.0005,   // slower spread — terrain builds visibly
  RELAX_EVERY:      6,        // relax half as often

  // Cycle
  CYCLE_SECS:       240,
  FADE_SECS:        8,
  HOLD_SECS:        2,

  // Colours — synthetic pink palette, opacity builds with deposition depth
  BG:        [10,  7,  5],
  WATER:     [28, 50, 82],
  // Sediment: dark magenta at thin deposits → bright pink-white at thick
  SED_THIN:  [180, 40, 120],   // thin deposit — visible magenta
  SED_THICK: [255, 210, 240],  // thick deposit — near-white pink
  // Particle alpha — very transparent so they only show as hints
  PARTICLE_ALPHA_MAX: 0.22,

  // Sediment transport over distance — open water fading
  // Only ~5% of particles make it across at full brightness
  // As particles fade, deposit probability increases
  FADE_START:       0.12,    // fraction of canvas width before fade begins
  FADE_LENGTH:      0.65,    // fraction of canvas width over which full fade occurs (most gone by ~77%)
  FADE_DEPOSIT_BOOST: 8.0,   // multiplier on drop rate at full fade (dim = dropping load)
  BASE_DROP_CHANCE: 0.05,    // 5% base deposit chance per frame at full brightness
};

// ── State ─────────────────────────────────────────────────────────────────────
let canvas, ctx, sizeEl;
let W, H, GW, GH;
let terrain, terrainB, water;
let particles = [];
let obstacles = [];
let emitter   = [];
let frame = 0, cycleFrame = 0;
let phase = 'run', fadeAlpha = 0, rafId = null;

// ── Helpers ───────────────────────────────────────────────────────────────────
const lerp  = (a, b, t) => a + (b - a) * t;
const clamp = (x, lo, hi) => x < lo ? lo : x > hi ? hi : x;
const rand  = () => Math.random();
const randc = () => rand() - 0.5;

function gIdx(gx, gy) {
  return clamp(gy | 0, 0, GH - 1) * GW + clamp(gx | 0, 0, GW - 1);
}

function slopeAt(gx, gy) {
  const L = terrain[gIdx(gx-1, gy)], R = terrain[gIdx(gx+1, gy)];
  const U = terrain[gIdx(gx, gy-1)], D = terrain[gIdx(gx, gy+1)];
  return { dx: (L-R)*0.5, dy: (U-D)*0.5 };
}

// ── Stream Generation ─────────────────────────────────────────────────────────
function makeStream() {
  const oy  = H * (0.10 + rand() * 0.80);
  const driftTarget = H * (0.10 + rand() * 0.80);
  const slope = ((driftTarget - oy) / W) * 0.25;
  return {
    x:           -8,
    y:           oy,
    vx:          CFG.SPEED_INIT,
    vy:          CFG.SPEED_INIT * slope * 0.3,
    driftTarget: driftTarget,
  };
}

// ── Obstacle Generation ───────────────────────────────────────────────────────
function placeObstacles() {
  obstacles = [];
  const n    = CFG.OBSTACLE_COUNT;
  const cols = Math.ceil(Math.sqrt(n * (W / H)));
  const rows = Math.ceil(n / cols);

  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      if (obstacles.length >= n) break;

      const xFrac = 0.10 + (col + 0.5 + (row % 2) * 0.5) / cols * 0.85;
      const yFrac = (row + 0.5) / rows;

      const ox = xFrac * W + randc() * W * 0.06;
      const oy = yFrac * H + randc() * H * 0.06;

      if (ox > W * 0.95) continue;

      const sign = (row % 2 === 0) ? 1 : -1;
      obstacles.push({
        x:  ox,
        y:  oy,
        nx: 0,
        ny: sign * (0.5 + rand() * 0.5)
      });
    }
  }
}

// ── Text Obstacles ────────────────────────────────────────────────────────────
function addTextObstacles(selectors) {
  for (let si = 0; si < selectors.length; si++) {
    const el = document.querySelector(selectors[si]);
    if (!el) continue;
    const r = el.getBoundingClientRect();
    // Offset by canvas position for non-fullscreen canvases
    const cr = canvas.getBoundingClientRect();
    const x0 = r.left - cr.left, y0 = r.top - cr.top;
    const x1 = r.right - cr.left, y1 = r.bottom - cr.top;
    const pad = 40;
    const stepsX = Math.max(6, Math.ceil((x1 - x0 + pad*2) / 14));
    const stepsY = Math.max(4, Math.ceil((y1 - y0 + pad*2) / 14));
    for (let i = 0; i <= stepsX; i++) {
      const x = (x0 - pad) + (x1 - x0 + pad*2) * (i / stepsX);
      obstacles.push({ x, y: y0 - pad, nx: 0, ny: -1 });
      obstacles.push({ x, y: y1 + pad, nx: 0, ny:  1 });
    }
    for (let j = 0; j <= stepsY; j++) {
      const y = (y0 - pad) + (y1 - y0 + pad*2) * (j / stepsY);
      obstacles.push({ x: x0 - pad, y, nx: -1, ny: 0 });
      obstacles.push({ x: x1 + pad, y, nx:  1, ny: 0 });
    }
  }
}

// ── Particle Creation ─────────────────────────────────────────────────────────
function makeParticle(stream) {
  const life = CFG.LIFE_MIN + rand() * (CFG.LIFE_MAX - CFG.LIFE_MIN);
  const terminalV = CFG.GRAVITY / (1 - CFG.BASE_DRAG);
  const vx = terminalV + randc() * CFG.SPEED_SPREAD * 0.5;
  const vy = randc() * CFG.SPEED_SPREAD * 0.2;
  const spread = randc() * CFG.EMITTER_SPREAD * H;
  return {
    x:    20,
    y:    clamp(stream.y + spread, 2, H - 2),
    vx:   Math.max(terminalV * 0.8, vx),
    vy,
    load: CFG.SEDIMENT_INIT + randc() * 0.10,
    life, fullLife: life,
    tint: 0,
    size: 1.1 + rand() * 1.0,
    alpha: 0,
    distAlpha: 1.0,   // fades with distance traveled — open water transport
  };
}

// ── Particle Step ─────────────────────────────────────────────────────────────
function stepParticle(p) {
  p.life -= 1;
  if (p.alpha < 1) p.alpha = Math.min(1, p.alpha + 0.07);

  // Distance-based fade — open water sediment transport
  // Particles dim as they travel, with most gone before 65% of canvas width
  const fadeStart = W * CFG.FADE_START;
  const fadeEnd   = W * (CFG.FADE_START + CFG.FADE_LENGTH);
  if (p.x > fadeStart) {
    const fadeProgress = clamp((p.x - fadeStart) / (fadeEnd - fadeStart), 0, 1);
    // Exponential decay — rapid initial loss, long tail (only 5% survive to full)
    p.distAlpha = Math.pow(1 - fadeProgress, 2.8);
  }

  const gx = (p.x / CFG.GRID_SCALE) | 0;
  const gy = (p.y / CFG.GRID_SCALE) | 0;
  const gi = gIdx(gx, gy);
  const th = terrain[gi];

  const sl = slopeAt(gx, gy);
  p.vy += sl.dy * 1.20;
  p.vx += CFG.GRAVITY;
  p.vy += randc() * CFG.LATERAL_NOISE;

  const friction = CFG.BASE_DRAG - th * CFG.TERRAIN_FRICTION;
  const sb = Math.sqrt(p.vx*p.vx + p.vy*p.vy);
  p.vx *= friction;
  p.vy *= friction;

  for (let i = 0; i < obstacles.length; i++) {
    const o  = obstacles[i];
    const dx = p.x - o.x;
    const dy = p.y - o.y;
    const d2 = dx*dx + dy*dy;
    const r2 = CFG.OBSTACLE_RADIUS * CFG.OBSTACLE_RADIUS;
    if (d2 < r2) {
      const influence = 1 - Math.sqrt(d2) / CFG.OBSTACLE_RADIUS;
      p.vx *= lerp(1, CFG.OBSTACLE_FORWARD_KILL, influence);
      p.vy += o.ny * CFG.OBSTACLE_STRENGTH * influence;
      const ogx = (o.x / CFG.GRID_SCALE) | 0;
      const ogy = (o.y / CFG.GRID_SCALE) | 0;
      const ogi = gIdx(ogx, ogy);
      const drop = Math.min(p.load, CFG.OBSTACLE_DEPOSIT * influence);
      terrain[ogi] = Math.min(CFG.MAX_SEDIMENT, terrain[ogi] + drop);
      p.load = Math.max(0, p.load - drop);
      break;
    }
  }

  p.x += p.vx;
  p.y += p.vy;

  if (p.y < 2)      { p.y = 2;     p.vy =  Math.abs(p.vy) * 0.6; }
  if (p.y > H - 2)  { p.y = H - 2; p.vy = -Math.abs(p.vy) * 0.6; }
  if (p.x > W + 20) { p.life = 0; return; }
  // Kill particle when it has fully faded and deposited its load
  if ((p.distAlpha ?? 1) < 0.01 && p.load < 0.02) { p.life = 0; return; }

  const sa = Math.sqrt(p.vx*p.vx + p.vy*p.vy);
  const decel = Math.max(0, sb - sa);

  if (p.load > 0) {
    const mod  = 1 + th * CFG.TERRAIN_DROP_MOD;
    // Fade boost: as particle dims, deposit probability increases dramatically
    // At distAlpha=1.0 (bright): base rate. At distAlpha=0.0 (gone): FADE_DEPOSIT_BOOST * rate
    const fadeMod = 1 + (1 - p.distAlpha) * CFG.FADE_DEPOSIT_BOOST;
    const drop = Math.min(p.load, decel * CFG.DROP_RATE * mod * fadeMod + p.load * (0.0003 + (1 - p.distAlpha) * 0.004));
    terrain[gi] = Math.min(CFG.MAX_SEDIMENT, th + drop);
    p.load = Math.max(0, p.load - drop);
  }

  if (sa > CFG.PICKUP_SPEED && th > 0.01) {
    const pickup = Math.min(th * 0.5, CFG.PICKUP_RATE);
    terrain[gi] = Math.max(0, terrain[gi] - pickup);
    p.load = Math.min(1, p.load + pickup);
    water[gi] = Math.min(1, water[gi] + 0.18);
  }
}

// ── Terrain Relaxation ────────────────────────────────────────────────────────
function relaxTerrain() {
  const R = CFG.RELAX_RATE;
  terrainB.set(terrain);
  for (let gy = 1; gy < GH - 1; gy++) {
    for (let gx = 1; gx < GW - 1; gx++) {
      const i  = gy * GW + gx;
      const h  = terrain[i];
      if (h < 0.005) continue;
      const hL = terrain[i-1], hR = terrain[i+1];
      const hU = terrain[(gy-1)*GW+gx], hD = terrain[(gy+1)*GW+gx];
      let out = 0;
      if (h > hL) { const f=(h-hL)*R; terrainB[i-1]+=f; out+=f; }
      if (h > hR) { const f=(h-hR)*R; terrainB[i+1]+=f; out+=f; }
      if (h > hU) { const f=(h-hU)*R; terrainB[(gy-1)*GW+gx]+=f; out+=f; }
      if (h > hD) { const f=(h-hD)*R; terrainB[(gy+1)*GW+gx]+=f; out+=f; }
      terrainB[i] = Math.max(0, terrainB[i] - out);
    }
  }
  const tmp = terrain; terrain = terrainB; terrainB = tmp;
}

// ── Rendering ─────────────────────────────────────────────────────────────────
function render() {
  const [BR, BG_c, BB] = CFG.BG;
  const [WR, WG, WB]   = CFG.WATER;

  ctx.fillStyle = `rgb(${BR},${BG_c},${BB})`;
  ctx.fillRect(0, 0, W, H);

  const img = ctx.getImageData(0, 0, W, H);
  const px  = img.data;
  const GS  = CFG.GRID_SCALE;

  for (let gy = 0; gy < GH; gy++) {
    for (let gx = 0; gx < GW; gx++) {
      const gi = gy * GW + gx;
      const th = terrain[gi];
      const wt = water[gi];
      if (th < 0.001 && wt < 0.004) continue;

      const ht  = clamp(th / CFG.MAX_SEDIMENT, 0, 1);
      const ht2 = ht * ht;

      const [TR, TG, TB] = CFG.SED_THIN;
      const [KR, KG, KB] = CFG.SED_THICK;
      let sr = Math.round(lerp(TR, KR, ht2));
      let sg = Math.round(lerp(TG, KG, ht2));
      let sb = Math.round(lerp(TB, KB, ht2));

      if (wt > 0.01) {
        const wa = clamp(wt * 0.70, 0, 0.65);
        sr = Math.round(lerp(sr, WR, wa));
        sg = Math.round(lerp(sg, WG, wa));
        sb = Math.round(lerp(sb, WB, wa));
      }

      const alpha = clamp(ht * 1.6 + wt * 0.5, 0, 1);
      const fr = (lerp(BR,   sr, alpha) + 0.5) | 0;
      const fg = (lerp(BG_c, sg, alpha) + 0.5) | 0;
      const fb = (lerp(BB,   sb, alpha) + 0.5) | 0;

      const x0 = gx*GS, y0 = gy*GS;
      const x1 = Math.min(x0+GS, W), y1 = Math.min(y0+GS, H);
      for (let py = y0; py < y1; py++) {
        let idx = (py*W + x0)*4;
        for (let ppx = x0; ppx < x1; ppx++) {
          px[idx]=fr; px[idx+1]=fg; px[idx+2]=fb; px[idx+3]=255;
          idx += 4;
        }
      }
    }
  }
  ctx.putImageData(img, 0, 0);

  ctx.save();
  for (let i = 0; i < particles.length; i++) {
    const p     = particles[i];
    const lifeT = clamp(p.life / p.fullLife, 0, 1);
    // distAlpha: fades particle with distance — only ~5% survive to far bank
    const da = p.distAlpha ?? 1.0;
    const pa = p.alpha * CFG.PARTICLE_ALPHA_MAX * Math.min(1, lifeT * 6) * da;
    if (pa < 0.01) continue;
    const sp = Math.sqrt(p.vx*p.vx + p.vy*p.vy);
    const t  = clamp(1 - sp / 0.15, 0, 1);
    const pr = Math.round(lerp(220, 255, t));
    const pg = Math.round(lerp(220, 120, t));
    const pb = Math.round(lerp(240, 180, t));
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.size, 0, 6.2832);
    ctx.fillStyle = `rgba(${pr},${pg},${pb},${pa.toFixed(3)})`;
    ctx.fill();
  }
  ctx.restore();

  if (fadeAlpha > 0) {
    ctx.fillStyle = `rgba(${CFG.BG[0]},${CFG.BG[1]},${CFG.BG[2]},${fadeAlpha.toFixed(3)})`;
    ctx.fillRect(0, 0, W, H);
  }
}

// ── Cycle ─────────────────────────────────────────────────────────────────────
function updateCycle() {
  const elapsed = (frame - cycleFrame) / 60;
  if (phase === 'run') {
    if (elapsed >= CFG.CYCLE_SECS) phase = 'fade';
  } else if (phase === 'fade') {
    const t = clamp((elapsed - CFG.CYCLE_SECS) / CFG.FADE_SECS, 0, 1);
    fadeAlpha = t * t;
    if (fadeAlpha >= 0.999) phase = 'hold';
  } else if (phase === 'hold') {
    const t = clamp((elapsed - CFG.CYCLE_SECS - CFG.FADE_SECS) / CFG.HOLD_SECS, 0, 1);
    if (t >= 1) resetSim();
  }
}

function resetSim() {
  terrain.fill(0); terrainB.fill(0); water.fill(0);
  particles.length = 0;
  phase = 'run'; fadeAlpha = 0; cycleFrame = frame;
  placeObstacles();
  emitter = [];
  for (let i = 0; i < CFG.EMITTER_COUNT; i++) emitter.push(makeStream());
}

// ── Init ──────────────────────────────────────────────────────────────────────
function initSim() {
  const w = sizeEl ? sizeEl.offsetWidth  : window.innerWidth;
  const h = sizeEl ? sizeEl.offsetHeight : window.innerHeight;
  W = canvas.width  = w;
  H = canvas.height = h;
  GW = Math.ceil(W / CFG.GRID_SCALE);
  GH = Math.ceil(H / CFG.GRID_SCALE);
  terrain  = new Float32Array(GW * GH);
  terrainB = new Float32Array(GW * GH);
  water    = new Float32Array(GW * GH);
  particles.length = 0;

  emitter = [];
  for (let i = 0; i < CFG.EMITTER_COUNT; i++) emitter.push(makeStream());

  frame = 0; cycleFrame = 0; phase = 'run'; fadeAlpha = 0;
  placeObstacles();
}

// ── Main Loop ─────────────────────────────────────────────────────────────────
function loop() {
  rafId = requestAnimationFrame(loop);
  frame++;
  updateCycle();

  if (phase === 'run') {
    for (let s = 0; s < emitter.length; s++) {
      const st = emitter[s];
      const diff = st.driftTarget - st.y;
      const step = CFG.DRIFT_SPEED * H;
      if (Math.abs(diff) <= step) {
        st.y = st.driftTarget;
        st.driftTarget = H * (0.10 + rand() * 0.80);
      } else {
        st.y += Math.sign(diff) * step;
      }
      const slope = ((st.driftTarget - st.y) / W) * 0.25;
      st.vy = CFG.SPEED_INIT * slope;
    }

    const fillRatio = particles.length / CFG.MAX_PARTICLES;
    const spawnP = Math.max(0, 1 - (fillRatio * fillRatio));
    for (let s = 0; s < emitter.length; s++) {
      if (rand() < spawnP) particles.push(makeParticle(emitter[s]));
    }
  }

  for (let i = 0; i < particles.length; i++) stepParticle(particles[i]);

  let i = 0;
  while (i < particles.length) {
    if (particles[i].life <= 0) { particles[i] = particles[particles.length-1]; particles.pop(); }
    else i++;
  }

  if (frame & 1) {
    for (let j = 0; j < water.length; j++) {
      if (water[j] > 0.001) water[j] *= 0.952; else water[j] = 0;
    }
  }

  if (frame % CFG.RELAX_EVERY === 0) relaxTerrain();
  render();
}

// ── Public API ────────────────────────────────────────────────────────────────
function start(canvasId, parentElement) {
  canvas  = document.getElementById(canvasId);
  ctx     = canvas.getContext('2d', { alpha: false });
  sizeEl  = parentElement || null;

  initSim();

  window.addEventListener('resize', () => {
    clearTimeout(window._sedRt);
    window._sedRt = setTimeout(() => {
      if (rafId) cancelAnimationFrame(rafId);
      initSim();
      rafId = requestAnimationFrame(loop);
    }, 150);
  });

  rafId = requestAnimationFrame(loop);
}

return { start, addTextObstacles };

})();
