/**
 * constellation-bg.js — Slow star field + connection lines (awards.html)
 * Quiet, dignified — subtle dot field with occasional connection threads
 * Very low opacity, minimal motion — doesn't compete with content
 */

(function() {
  const canvas = document.createElement('canvas');
  canvas.id = 'constellation-canvas';
  canvas.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;z-index:0;pointer-events:none;opacity:0.20;';
  document.body.insertBefore(canvas, document.body.firstChild);

  const ctx = canvas.getContext('2d');
  let W, H;
  const NUM_STARS = 220;
  let stars = [];
  let t = 0;
  const CONNECT_DIST = 120;

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
    stars = Array.from({ length: NUM_STARS }, () => ({
      x: Math.random() * W,
      y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.08,
      vy: (Math.random() - 0.5) * 0.08,
      r: 0.6 + Math.random() * 1.6,
      alpha: 0.2 + Math.random() * 0.6,
      twinkle: Math.random() * Math.PI * 2,
      twinkleSpeed: 0.005 + Math.random() * 0.015,
    }));
  }
  resize();
  window.addEventListener('resize', resize);

  function loop() {
    requestAnimationFrame(loop);
    t += 0.01;

    ctx.clearRect(0, 0, W, H);

    // Move stars
    for (const s of stars) {
      s.x += s.vx;
      s.y += s.vy;
      s.twinkle += s.twinkleSpeed;
      if (s.x < 0) s.x += W;
      if (s.x > W) s.x -= W;
      if (s.y < 0) s.y += H;
      if (s.y > H) s.y -= H;
    }

    // Draw connections
    for (let i = 0; i < stars.length; i++) {
      for (let j = i + 1; j < stars.length; j++) {
        const dx = stars[i].x - stars[j].x;
        const dy = stars[i].y - stars[j].y;
        const d = Math.sqrt(dx * dx + dy * dy);
        if (d < CONNECT_DIST) {
          const a = (1 - d / CONNECT_DIST) * 0.15;
          ctx.beginPath();
          ctx.moveTo(stars[i].x, stars[i].y);
          ctx.lineTo(stars[j].x, stars[j].y);
          ctx.strokeStyle = `rgba(200, 180, 140, ${a})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }

    // Draw stars
    for (const s of stars) {
      const twinkle = 0.6 + 0.4 * Math.sin(s.twinkle);
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(220, 200, 160, ${s.alpha * twinkle})`;
      ctx.fill();
    }
  }

  loop();
})();
