/**
 * wave-bg.js — Animated topographic contour lines (lectures.html)
 * Isolines drawn from a slowly-evolving noise field — thin, precise, contemplative
 * No gradients — just lines at threshold values, like a topo map in motion
 */

(function() {
  const canvas = document.createElement('canvas');
  canvas.id = 'wave-canvas';
  canvas.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;opacity:0.28;';
  document.body.insertBefore(canvas, document.body.firstChild);

  const ctx = canvas.getContext('2d');
  let W, H, t = 0;

  // Low-res grid for marching squares
  const CELL = 18;   // grid cell size in px — fine enough for smooth lines
  let cols, rows, field;

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
    cols = Math.ceil(W / CELL) + 2;
    rows = Math.ceil(H / CELL) + 2;
    field = new Float32Array(cols * rows);
  }
  resize();
  window.addEventListener('resize', resize);

  // Smooth noise
  function hash(n) { n = Math.sin(n) * 43758.5453; return n - Math.floor(n); }
  function noise(x, y) {
    const ix = Math.floor(x), iy = Math.floor(y);
    const fx = x - ix, fy = y - iy;
    const ux = fx*fx*(3-2*fx), uy = fy*fy*(3-2*fy);
    return hash(ix + iy*131) * (1-ux)*(1-uy)
         + hash(ix+1 + iy*131) * ux*(1-uy)
         + hash(ix + (iy+1)*131) * (1-ux)*uy
         + hash(ix+1 + (iy+1)*131) * ux*uy;
  }

  // Octave noise for more organic terrain feel
  function fbm(x, y) {
    let v = 0, amp = 0.5, freq = 1;
    for (let i = 0; i < 4; i++) {
      v += amp * noise(x * freq, y * freq);
      amp *= 0.5; freq *= 2.1;
    }
    return v;
  }

  // Marching squares — linear interpolation along edge
  function lerp(a, b, v) { return (v - a) / (b - a); }

  // Draw a single isoline at threshold `iso` across the field
  function drawContour(iso, alpha) {
    ctx.beginPath();
    for (let r = 0; r < rows - 1; r++) {
      for (let c = 0; c < cols - 1; c++) {
        const x0 = (c - 1) * CELL, y0 = (r - 1) * CELL;

        const v00 = field[r * cols + c];
        const v10 = field[r * cols + c + 1];
        const v01 = field[(r+1) * cols + c];
        const v11 = field[(r+1) * cols + c + 1];

        // Which corners are above the threshold?
        const b = ((v00 > iso) ? 8 : 0)
                | ((v10 > iso) ? 4 : 0)
                | ((v11 > iso) ? 2 : 0)
                | ((v01 > iso) ? 1 : 0);

        if (b === 0 || b === 15) continue; // all same side

        // Interpolated edge points
        const top    = { x: x0 + lerp(v00, v10, iso) * CELL, y: y0 };
        const right  = { x: x0 + CELL, y: y0 + lerp(v10, v11, iso) * CELL };
        const bottom = { x: x0 + lerp(v01, v11, iso) * CELL, y: y0 + CELL };
        const left   = { x: x0, y: y0 + lerp(v00, v01, iso) * CELL };

        // Draw line segment for this cell
        let p1, p2;
        switch (b) {
          case 1:  case 14: p1=left;   p2=bottom; break;
          case 2:  case 13: p1=bottom; p2=right;  break;
          case 3:  case 12: p1=left;   p2=right;  break;
          case 4:  case 11: p1=top;    p2=right;  break;
          case 5:           p1=top;    p2=left;
            ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y);
            p1=bottom; p2=right; break;
          case 6:  case 9:  p1=top;    p2=bottom; break;
          case 7:  case 8:  p1=top;    p2=left;   break;
          case 10:          p1=top;    p2=right;
            ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y);
            p1=left; p2=bottom; break;
          default: continue;
        }
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
      }
    }
    ctx.strokeStyle = `rgba(196, 172, 128, ${alpha})`;
    ctx.stroke();
  }

  // Contour levels — 8 isolines at even intervals
  const NUM_CONTOURS = 8;
  const contours = Array.from({ length: NUM_CONTOURS }, (_, i) => ({
    iso: 0.15 + (i / NUM_CONTOURS) * 0.7,
    alpha: 0.12 + (i / NUM_CONTOURS) * 0.18,  // deeper = slightly brighter
    width: 0.4 + (i / NUM_CONTOURS) * 0.4,
  }));

  function loop() {
    requestAnimationFrame(loop);
    t += 0.0018;  // very slow evolution

    // Recompute noise field
    const FREQ = 0.0018;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        field[r * cols + c] = fbm((c - 1) * CELL * FREQ, (r - 1) * CELL * FREQ + t * 0.4);
      }
    }

    ctx.clearRect(0, 0, W, H);

    // Draw each contour level
    for (const ct of contours) {
      ctx.lineWidth = ct.width;
      ctx.setLineDash([]);
      drawContour(ct.iso, ct.alpha);
    }
  }

  loop();
})();
