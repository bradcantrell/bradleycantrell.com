/**
 * flow-field.js — Perlin-style flow field (about.html)
 * Organic particle streams following a slowly-evolving noise field
 * Personal, contemplative — matches "about" page tone
 * Pure JS (no p5.js dependency) — uses simplex-like noise
 */

(function() {
  // Minimal value noise (no external deps)
  function hash(n) {
    n = Math.sin(n) * 43758.5453123;
    return n - Math.floor(n);
  }
  function noise2(x, y) {
    const ix = Math.floor(x), iy = Math.floor(y);
    const fx = x - ix, fy = y - iy;
    const ux = fx * fx * (3 - 2 * fx);
    const uy = fy * fy * (3 - 2 * fy);
    const a = hash(ix + iy * 57);
    const b = hash(ix + 1 + iy * 57);
    const c = hash(ix + (iy + 1) * 57);
    const d = hash(ix + 1 + (iy + 1) * 57);
    return a + (b - a) * ux + (c - a) * uy + (d - b - c + a) * ux * uy;
  }

  const NUM_PARTICLES = 600;
  const SPEED = 0.9;
  const SCALE = 0.003;
  const FADE = 0.012;  // trail opacity per frame
  let canvas, ctx, particles, t = 0;

  function init() {
    canvas = document.getElementById('flow-canvas');
    ctx = canvas.getContext('2d');
    resize();
    window.addEventListener('resize', resize);
    particles = Array.from({ length: NUM_PARTICLES }, () => spawnParticle());
    loop();
  }

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  function spawnParticle() {
    return {
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      age: 0,
      maxAge: 200 + Math.random() * 400,
      alpha: 0.08 + Math.random() * 0.18,
      size: 0.8 + Math.random() * 1.4,
    };
  }

  function loop() {
    requestAnimationFrame(loop);
    t += 0.002;

    // Fade trail
    ctx.fillStyle = `rgba(22, 18, 14, ${FADE})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.age++;
      if (p.age > p.maxAge) {
        particles[i] = spawnParticle();
        continue;
      }

      // Flow angle from noise field
      const angle = noise2(p.x * SCALE, p.y * SCALE + t) * Math.PI * 4;
      p.x += Math.cos(angle) * SPEED;
      p.y += Math.sin(angle) * SPEED;

      // Wrap
      if (p.x < 0) p.x += canvas.width;
      if (p.x > canvas.width) p.x -= canvas.width;
      if (p.y < 0) p.y += canvas.height;
      if (p.y > canvas.height) p.y -= canvas.height;

      // Age-based fade in/out
      const lifeFrac = p.age / p.maxAge;
      const alpha = p.alpha * Math.sin(lifeFrac * Math.PI);

      // Warm amber particle
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(200, 176, 130, ${alpha})`;
      ctx.fill();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
