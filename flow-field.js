/**
 * flow-field.js — Perlin-style flow field (about.html)
 * Organic particle streams following a slowly-evolving noise field
 * Personal, contemplative — matches "about" page tone
 */

(function() {
  // Minimal value noise (no external deps)
  function hash(n) { n = Math.sin(n) * 43758.5453123; return n - Math.floor(n); }
  function noise2(x, y) {
    const ix = Math.floor(x), iy = Math.floor(y);
    const fx = x - ix, fy = y - iy;
    const ux = fx * fx * (3 - 2 * fx), uy = fy * fy * (3 - 2 * fy);
    const a = hash(ix + iy * 57), b = hash(ix + 1 + iy * 57);
    const c = hash(ix + (iy + 1) * 57), d = hash(ix + 1 + (iy + 1) * 57);
    return a + (b - a) * ux + (c - a) * uy + (d - b - c + a) * ux * uy;
  }

  const NUM_PARTICLES = 600, SPEED = 0.9, SCALE = 0.003, FADE = 0.012;
  let canvas, ctx, particles, t = 0, W, H;

  // Create and inject canvas immediately
  canvas = document.createElement('canvas');
  canvas.id = 'flow-canvas';
  canvas.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;opacity:0.28;';
  document.body.insertBefore(canvas, document.body.firstChild);
  ctx = canvas.getContext('2d');

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  function spawnParticle() {
    return { x: Math.random() * W, y: Math.random() * H, age: 0,
      maxAge: 200 + Math.random() * 400, alpha: 0.08 + Math.random() * 0.18,
      size: 0.8 + Math.random() * 1.4 };
  }

  particles = Array.from({ length: NUM_PARTICLES }, spawnParticle);

  function loop() {
    requestAnimationFrame(loop);
    t += 0.002;
    ctx.fillStyle = `rgba(22, 18, 14, ${FADE})`;
    ctx.fillRect(0, 0, W, H);
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.age++;
      if (p.age > p.maxAge) { particles[i] = spawnParticle(); continue; }
      const angle = noise2(p.x * SCALE, p.y * SCALE + t) * Math.PI * 4;
      p.x += Math.cos(angle) * SPEED;
      p.y += Math.sin(angle) * SPEED;
      if (p.x < 0) p.x += W; if (p.x > W) p.x -= W;
      if (p.y < 0) p.y += H; if (p.y > H) p.y -= H;
      const alpha = p.alpha * Math.sin((p.age / p.maxAge) * Math.PI);
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(200, 176, 130, ${alpha})`;
      ctx.fill();
    }
  }
  loop();
})();
