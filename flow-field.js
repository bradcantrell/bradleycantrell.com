/**
 * flow-field.js — Sparse dashed flow lines (about.html)
 * Thin, dashed/dotted lines following a noise field — minimal, personal
 */

(function() {
  function hash(n) { n = Math.sin(n) * 43758.5453123; return n - Math.floor(n); }
  function noise2(x, y) {
    const ix = Math.floor(x), iy = Math.floor(y);
    const fx = x - ix, fy = y - iy;
    const ux = fx*fx*(3-2*fx), uy = fy*fy*(3-2*fy);
    const a = hash(ix + iy*57), b = hash(ix+1 + iy*57);
    const c = hash(ix + (iy+1)*57), d = hash(ix+1 + (iy+1)*57);
    return a+(b-a)*ux+(c-a)*uy+(d-b-c+a)*ux*uy;
  }

  const NUM_LINES = 120;   // fewer lines
  const STEP_LEN = 4;      // how far each segment draws
  const MAX_STEPS = 60;    // line length in segments
  const SPEED = 0.003;     // time evolution — very slow
  const SCALE = 0.0025;
  let canvas, ctx, lines, t = 0, W, H;

  // Create canvas immediately
  canvas = document.createElement('canvas');
  canvas.id = 'flow-canvas';
  canvas.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;opacity:0.22;';
  document.body.insertBefore(canvas, document.body.firstChild);
  ctx = canvas.getContext('2d');

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
    initLines();
  }

  function initLines() {
    lines = Array.from({ length: NUM_LINES }, () => spawnLine());
  }

  function spawnLine() {
    return {
      x: Math.random() * W,
      y: Math.random() * H,
      steps: 0,
      maxSteps: 20 + Math.floor(Math.random() * MAX_STEPS),
      alpha: 0.15 + Math.random() * 0.30,
      width: 0.4 + Math.random() * 0.6,
      delay: Math.floor(Math.random() * 200),  // staggered start
    };
  }

  resize();
  window.addEventListener('resize', resize);

  let frame = 0;
  function loop() {
    requestAnimationFrame(loop);
    frame++;
    t += SPEED;

    // Very slow fade — lines persist as thin traces
    ctx.fillStyle = 'rgba(14, 11, 9, 0.015)';
    ctx.fillRect(0, 0, W, H);

    ctx.setLineDash([2, 6]);   // dashed strokes
    ctx.lineWidth = 0.7;

    for (let i = 0; i < lines.length; i++) {
      const l = lines[i];
      if (frame < l.delay) continue;

      l.steps++;
      if (l.steps > l.maxSteps) {
        lines[i] = spawnLine();
        continue;
      }

      const angle = noise2(l.x * SCALE, l.y * SCALE + t) * Math.PI * 4;
      const nx = l.x + Math.cos(angle) * STEP_LEN;
      const ny = l.y + Math.sin(angle) * STEP_LEN;

      // Fade in/out over life
      const life = l.steps / l.maxSteps;
      const alpha = l.alpha * Math.sin(life * Math.PI);

      ctx.beginPath();
      ctx.moveTo(l.x, l.y);
      ctx.lineTo(nx, ny);
      ctx.strokeStyle = `rgba(196, 172, 128, ${alpha})`;
      ctx.stroke();

      l.x = nx; l.y = ny;

      // Wrap
      if (l.x < 0) l.x += W; if (l.x > W) l.x -= W;
      if (l.y < 0) l.y += H; if (l.y > H) l.y -= H;
    }

    ctx.setLineDash([]);  // reset dash
  }

  loop();
})();
