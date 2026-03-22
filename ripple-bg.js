/**
 * ripple-bg.js — Wave propagation / ripple interference (responsive-landscapes.html)
 * Concentric wave fronts emanating from multiple points, interfering
 * Direct reference to responsive systems, wave propagation, landscape as medium
 * Warm amber on dark
 */

(function() {
  const canvas = document.createElement('canvas');
  canvas.id = 'ripple-canvas';
  canvas.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;z-index:0;pointer-events:none;opacity:0.25;';
  document.body.insertBefore(canvas, document.body.firstChild);

  const ctx = canvas.getContext('2d');
  let W, H;
  let t = 0;
  let sources = [];

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
    sources = [
      { x: W * 0.22, y: H * 0.35, freq: 0.022, phase: 0,           amp: 1.0 },
      { x: W * 0.75, y: H * 0.45, freq: 0.019, phase: Math.PI,      amp: 0.85 },
      { x: W * 0.48, y: H * 0.78, freq: 0.017, phase: Math.PI * 1.5, amp: 0.7 },
      { x: W * 0.15, y: H * 0.70, freq: 0.024, phase: Math.PI * 0.4, amp: 0.6 },
    ];
  }
  resize();
  window.addEventListener('resize', resize);

  // Render at reduced resolution for performance
  const STEP = 3;

  function loop() {
    requestAnimationFrame(loop);
    t += 0.012;

    const imgData = ctx.createImageData(W, H);
    const data = imgData.data;

    for (let y = 0; y < H; y += STEP) {
      for (let x = 0; x < W; x += STEP) {
        let val = 0;
        for (const s of sources) {
          const dist = Math.sqrt((x - s.x) ** 2 + (y - s.y) ** 2);
          const decay = Math.exp(-dist * 0.0008);
          val += s.amp * decay * Math.sin(dist * s.freq - t + s.phase);
        }

        const norm = (val / sources.length + 1) / 2;
        const bright = Math.max(0, Math.min(1, norm));
        const ridge = Math.pow(bright, 0.6); // sharpen ridges slightly

        const r = Math.floor(20 + ridge * 188);
        const g = Math.floor(14 + ridge * 148);
        const b = Math.floor(8  + ridge * 100);
        const a = Math.floor(6  + ridge * 160);

        for (let dy = 0; dy < STEP && y + dy < H; dy++) {
          for (let dx = 0; dx < STEP && x + dx < W; dx++) {
            const i = ((y + dy) * W + (x + dx)) * 4;
            data[i] = r; data[i+1] = g; data[i+2] = b; data[i+3] = a;
          }
        }
      }
    }
    ctx.putImageData(imgData, 0, 0);
  }

  loop();
})();
