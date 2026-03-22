/**
 * work-bg.js — Gray-Scott Reaction-Diffusion
 * Turing pattern formation: biological + computational aesthetic
 * Two-chemical system (U/V) producing organic spotted/striped patterns
 * Warm amber palette matching site accent colors
 */

let uw, uh, cells, next;
let canvas, ctx;
const SCALE = 3; // pixel size — coarser = faster

// Gray-Scott parameters — "coral" / spotted pattern
const DA = 1.0, DB = 0.5;
const F = 0.055, K = 0.062;

// Auto-start
window.addEventListener('DOMContentLoaded', rdSetup);
if (document.readyState !== 'loading') rdSetup();

function rdSetup() {
  if (canvas) return; // guard against double-init
  canvas = document.getElementById('rd-canvas');
  ctx = canvas.getContext('2d');
  rdResize();
  window.addEventListener('resize', rdResize);
  rdLoop();
}

function rdResize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  uw = Math.floor(canvas.width / SCALE);
  uh = Math.floor(canvas.height / SCALE);
  cells = new Float32Array(uw * uh * 2); // [u0,v0, u1,v1, ...]
  next = new Float32Array(uw * uh * 2);
  // Initialize: U=1 everywhere, V=0 except seed patches
  for (let i = 0; i < uw * uh; i++) {
    cells[i * 2]     = 1.0; // U
    cells[i * 2 + 1] = 0.0; // V
  }
  // Seed just a few tiny patches — pattern grows in slowly from near-empty
  const numSeeds = 6;
  for (let s = 0; s < numSeeds; s++) {
    const cx = Math.floor(Math.random() * uw);
    const cy = Math.floor(Math.random() * uh);
    for (let dy = -2; dy <= 2; dy++) {
      for (let dx = -2; dx <= 2; dx++) {
        const x = (cx + dx + uw) % uw;
        const y = (cy + dy + uh) % uh;
        const idx = (y * uw + x) * 2;
        cells[idx]     = 0.5;
        cells[idx + 1] = 0.25;
      }
    }
  }
}

let frame = 0;
function rdLoop() {
  requestAnimationFrame(rdLoop);
  // Run multiple simulation steps per frame for speed
  for (let step = 0; step < 8; step++) {
    rdStep();
  }
  // Only redraw every 2 frames
  if (frame++ % 2 === 0) rdDraw();
}

function rdStep() {
  for (let y = 0; y < uh; y++) {
    for (let x = 0; x < uw; x++) {
      const idx = (y * uw + x) * 2;
      const u = cells[idx], v = cells[idx + 1];

      // Laplacian (5-point stencil with wrapping)
      const left  = cells[(y * uw + (x - 1 + uw) % uw) * 2];
      const right = cells[(y * uw + (x + 1) % uw) * 2];
      const up    = cells[((y - 1 + uh) % uh * uw + x) * 2];
      const down  = cells[((y + 1) % uh * uw + x) * 2];
      const lv_l  = cells[(y * uw + (x - 1 + uw) % uw) * 2 + 1];
      const lv_r  = cells[(y * uw + (x + 1) % uw) * 2 + 1];
      const lv_u  = cells[((y - 1 + uh) % uh * uw + x) * 2 + 1];
      const lv_d  = cells[((y + 1) % uh * uw + x) * 2 + 1];

      const lapU = (left + right + up + down - 4 * u);
      const lapV = (lv_l + lv_r + lv_u + lv_d - 4 * v);

      const uvv = u * v * v;
      next[idx]     = Math.max(0, Math.min(1, u + DA * lapU - uvv + F * (1 - u)));
      next[idx + 1] = Math.max(0, Math.min(1, v + DB * lapV + uvv - (K + F) * v));
    }
  }
  [cells, next] = [next, cells];
}

function rdDraw() {
  const imgData = ctx.createImageData(canvas.width, canvas.height);
  const data = imgData.data;

  for (let cy = 0; cy < uh; cy++) {
    for (let cx = 0; cx < uw; cx++) {
      const idx = (cy * uw + cx) * 2;
      const v = cells[idx + 1]; // V concentration drives color
      const t = Math.min(1, v * 4); // amplify for visibility

      // Warm palette: dark background → amber highlight
      // bg: #1a1614  accent: #c8b090  highlight: #e8e0d0
      const r = Math.floor(26  + t * (232 - 26));
      const g = Math.floor(22  + t * (176 - 22));
      const b = Math.floor(20  + t * (144 - 20));
      const a = Math.floor(30  + t * (180 - 30)); // semi-transparent

      for (let py = 0; py < SCALE; py++) {
        for (let px = 0; px < SCALE; px++) {
          const pIdx = ((cy * SCALE + py) * canvas.width + (cx * SCALE + px)) * 4;
          data[pIdx]     = r;
          data[pIdx + 1] = g;
          data[pIdx + 2] = b;
          data[pIdx + 3] = a;
        }
      }
    }
  }
  ctx.putImageData(imgData, 0, 0);
}
