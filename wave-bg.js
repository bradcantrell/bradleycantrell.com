/**
 * wave-bg.js — Standing wave / interference pattern (lectures.html)
 * Multiple sinusoidal waves interfering — acoustic, spatial, contemplative
 * Warm amber on dark, very subtle — matches site palette
 */

(function() {
  const canvas = document.createElement('canvas');
  canvas.id = 'wave-canvas';
  canvas.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;z-index:0;pointer-events:none;opacity:0.22;';
  document.body.insertBefore(canvas, document.body.firstChild);

  const ctx = canvas.getContext('2d');
  let W, H;
  let t = 0;

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  // Wave sources — a few point sources creating interference
  function getSources() {
    return [
      { x: W * 0.2, y: H * 0.3, freq: 0.018, phase: 0 },
      { x: W * 0.8, y: H * 0.6, freq: 0.016, phase: Math.PI * 0.7 },
      { x: W * 0.5, y: H * 0.85, freq: 0.014, phase: Math.PI * 1.3 },
    ];
  }

  function loop() {
    requestAnimationFrame(loop);
    t += 0.015;

    const sources = getSources();
    const imgData = ctx.createImageData(W, H);
    const data = imgData.data;

    // Subsample for performance — compute every 4th pixel, scale up
    const STEP = 4;
    for (let y = 0; y < H; y += STEP) {
      for (let x = 0; x < W; x += STEP) {
        // Sum wave contributions from all sources
        let sum = 0;
        for (const s of sources) {
          const dist = Math.sqrt((x - s.x) ** 2 + (y - s.y) ** 2);
          sum += Math.sin(dist * s.freq - t + s.phase);
        }
        // Normalize -3..3 → 0..1
        const val = (sum / sources.length + 1) / 2;
        const bright = Math.max(0, Math.min(1, val));

        const r = Math.floor(30 + bright * 200);
        const g = Math.floor(22 + bright * 158);
        const b = Math.floor(14 + bright * 100);
        const a = Math.floor(8 + bright * 140);

        // Fill block
        for (let dy = 0; dy < STEP && y + dy < H; dy++) {
          for (let dx = 0; dx < STEP && x + dx < W; dx++) {
            const i = ((y + dy) * W + (x + dx)) * 4;
            data[i]     = r;
            data[i + 1] = g;
            data[i + 2] = b;
            data[i + 3] = a;
          }
        }
      }
    }
    ctx.putImageData(imgData, 0, 0);
  }

  loop();
})();
