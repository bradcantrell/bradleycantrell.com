/**
 * work-bg.js - Contour Field + Flow Particles (work.html)
 */
(function() {
  var canvas = document.getElementById('rd-canvas');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var W, H;

  // Noise
  function hash(n) { n = Math.sin(n) * 43758.5453; return n - Math.floor(n); }
  function noise(x, y) {
    var ix = Math.floor(x), iy = Math.floor(y);
    var fx = x - ix, fy = y - iy;
    var ux = fx*fx*(3-2*fx), uy = fy*fy*(3-2*fy);
    return hash(ix + iy*131) * (1-ux)*(1-uy)
         + hash(ix+1 + iy*131) * ux*(1-uy)
         + hash(ix + (iy+1)*131) * (1-ux)*uy
         + hash(ix+1 + (iy+1)*131) * ux*uy;
  }
  function fbm(x, y) {
    var v = 0, amp = 0.5, freq = 1;
    for (var i = 0; i < 4; i++) {
      v += amp * noise(x * freq, y * freq);
      amp *= 0.5; freq *= 2.1;
    }
    return v;
  }

  // ── Contours ──────────────────────────────────────────────
  var CELL = 20, cols, rows, field;
  var NUM_CONTOURS = 12;
  var contourLevels = [];
  for (var ci = 0; ci < NUM_CONTOURS; ci++) {
    var t = ci / NUM_CONTOURS;
    contourLevels.push({
      iso: 0.1 + t * 0.80,
      alpha: 0.12 + t * 0.24,
      width: 0.5 + t * 0.4
    });
  }

  function lerp(a, b, v) { return (v - a) / (b - a); }

  function drawContour(iso, alpha, colorStr) {
    ctx.beginPath();
    for (var r = 0; r < rows - 1; r++) {
      for (var c = 0; c < cols - 1; c++) {
        var x0 = (c - 1) * CELL, y0 = (r - 1) * CELL;
        var i00 = r * cols + c;
        var v00 = field[i00];
        var v10 = field[i00 + 1];
        var v01 = field[i00 + cols];
        var v11 = field[i00 + cols + 1];

        var b = ((v00 > iso) ? 8 : 0) | ((v10 > iso) ? 4 : 0)
              | ((v11 > iso) ? 2 : 0) | ((v01 > iso) ? 1 : 0);
        if (b === 0 || b === 15) continue;

        var topPt    = { x: x0 + lerp(v00, v10, iso) * CELL, y: y0 };
        var rightPt  = { x: x0 + CELL, y: y0 + lerp(v10, v11, iso) * CELL };
        var bottomPt = { x: x0 + lerp(v01, v11, iso) * CELL, y: y0 + CELL };
        var leftPt   = { x: x0, y: y0 + lerp(v00, v01, iso) * CELL };

        var p1, p2;
        switch (b) {
          case 1: case 14: p1=leftPt; p2=bottomPt; break;
          case 2: case 13: p1=bottomPt; p2=rightPt; break;
          case 3: case 12: p1=leftPt; p2=rightPt; break;
          case 4: case 11: p1=topPt; p2=rightPt; break;
          case 5: p1=topPt; p2=leftPt;
            ctx.moveTo(p1.x,p1.y); ctx.lineTo(p2.x,p2.y);
            p1=bottomPt; p2=rightPt; break;
          case 6: case 9: p1=topPt; p2=bottomPt; break;
          case 7: case 8: p1=topPt; p2=leftPt; break;
          case 10: p1=topPt; p2=rightPt;
            ctx.moveTo(p1.x,p1.y); ctx.lineTo(p2.x,p2.y);
            p1=leftPt; p2=bottomPt; break;
          default: continue;
        }
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
      }
    }
    ctx.strokeStyle = colorStr;
    ctx.globalAlpha = alpha;
    ctx.stroke();
    ctx.globalAlpha = 1;
  }

  // ── Particles ──────────────────────────────────────────────
  var NUM_PARTICLES = 40;
  var particles = [];

  function makeParticle() {
    return {
      x: Math.random() * W,
      y: Math.random() * H,
      trail: [],
      maxTrail: 180 + Math.floor(Math.random() * 200),
      speed: 0.4 + Math.random() * 0.9,
      alpha: 0.35 + Math.random() * 0.50,
      width: 0.6 + Math.random() * 0.7,
      vx: 0, vy: 0
    };
  }

  function initParticles() {
    particles = [];
    for (var i = 0; i < NUM_PARTICLES; i++) {
      particles.push(makeParticle());
    }
  }

  function sampleGradient(x, y) {
    var ep = 0.0005;
    var v0 = fbm(x * 0.0015, y * 0.0015);
    var vx = fbm((x + ep) * 0.0015, y * 0.0015);
    var vy = fbm(x * 0.0015, (y + ep) * 0.0015);
    return { dx: (vx - v0) / ep, dy: (vy - v0) / ep };
  }

  // ── Resize ──────────────────────────────────────────────────
  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
    cols = Math.ceil(W / CELL) + 2;
    rows = Math.ceil(H / CELL) + 2;
    field = new Float32Array(cols * rows);
    initParticles();
  }
  resize();
  window.addEventListener('resize', resize);

  // ── Loop ────────────────────────────────────────────────────
  var t = 0;
  var FREQ = 0.0015;

  function loop() {
    requestAnimationFrame(loop);
    t += 0.0015;

    // Fill noise field
    for (var rr = 0; rr < rows; rr++) {
      for (var cc = 0; cc < cols; cc++) {
        field[rr * cols + cc] = fbm((cc - 1) * CELL * FREQ, (rr - 1) * CELL * FREQ + t * 0.35);
      }
    }

    ctx.clearRect(0, 0, W, H);

    // Draw contours
    for (var di = 0; di < contourLevels.length; di++) {
      var ct = contourLevels[di];
      ctx.lineWidth = ct.width;
      ctx.setLineDash([]);
      var rr = Math.floor(60 + ct.iso * 20);
      var gg = Math.floor(78 + ct.iso * 15);
      var bb = Math.floor(92 + ct.iso * 12);
      drawContour(ct.iso, ct.alpha, 'rgb(' + rr + ',' + gg + ',' + bb + ')');
    }

    // Draw particles
    for (var pi = 0; pi < particles.length; pi++) {
      var p = particles[pi];
      var grad = sampleGradient(p.x, p.y);
      var mag = Math.sqrt(grad.dx * grad.dx + grad.dy * grad.dy);
      if (mag < 0.00001) mag = 0.00001;
      p.vx = (grad.dx / mag) * p.speed;
      p.vy = (grad.dy / mag) * p.speed;
      p.x += p.vx;
      p.y += p.vy;

      // Bounce at edges
      if (p.x < 0)      { p.x = 0;      p.vx *= -1; }
      if (p.x > W)      { p.x = W;      p.vx *= -1; }
      if (p.y < 0)      { p.y = 0;      p.vy *= -1; }
      if (p.y > H)      { p.y = H;      p.vy *= -1; }

      p.trail.push({ x: p.x, y: p.y });
      if (p.trail.length > p.maxTrail) { p.trail.shift(); }

      // Regenerate when trail is fully faded
      if (p.trail.length >= p.maxTrail) {
        particles[pi] = makeParticle();
        continue;
      }

      if (p.trail.length > 1) {
        ctx.beginPath();
        ctx.moveTo(p.trail[0].x, p.trail[0].y);
        for (var ti = 1; ti < p.trail.length; ti++) {
          ctx.lineTo(p.trail[ti].x, p.trail[ti].y);
        }
        ctx.strokeStyle = 'rgba(190,168,122,' + p.alpha + ')';
        ctx.lineWidth = p.width;
        ctx.lineCap = 'round';
        ctx.stroke();
      }
    }
  }

  loop();
})();
