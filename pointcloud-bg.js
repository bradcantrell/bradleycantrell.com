/**
 * pointcloud-bg.js — Slow drift point cloud (dissertation.html)
 * Academic, contemplative — echoes the B3 territory diagram aesthetic
 * Points drift in a slow 3D-like flow, warm amber on dark
 */

(function() {
  const canvas = document.createElement('canvas');
  canvas.id = 'pointcloud-canvas';
  canvas.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;z-index:0;pointer-events:none;opacity:0.30;';
  document.body.insertBefore(canvas, document.body.firstChild);

  const ctx = canvas.getContext('2d');
  let W, H;
  const NUM_POINTS = 1200;
  let points = [];
  let t = 0;

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
    initPoints();
  }

  function initPoints() {
    points = [];
    for (let i = 0; i < NUM_POINTS; i++) {
      points.push({
        // 3D position
        ox: (Math.random() - 0.5) * 2,  // -1..1
        oy: (Math.random() - 0.5) * 2,
        oz: (Math.random() - 0.5) * 2,
        phase: Math.random() * Math.PI * 2,
        speed: 0.0003 + Math.random() * 0.0004,
        alpha: 0.15 + Math.random() * 0.55,
        size: 0.8 + Math.random() * 1.8,
      });
    }
  }

  resize();
  window.addEventListener('resize', resize);

  function hash(n) {
    const s = Math.sin(n) * 43758.5453;
    return s - Math.floor(s);
  }

  function loop() {
    requestAnimationFrame(loop);
    t += 0.004;

    ctx.fillStyle = 'rgba(14, 11, 8, 0.18)';
    ctx.fillRect(0, 0, W, H);

    // Sort by Z (painter's algorithm — distant points first)
    const rendered = points.map(p => {
      // Slow rotation around Y axis
      const cosT = Math.cos(t * 0.15 + p.phase * 0.1);
      const sinT = Math.sin(t * 0.15 + p.phase * 0.1);
      const rx = p.ox * cosT - p.oz * sinT;
      const ry = p.oy;
      const rz = p.ox * sinT + p.oz * cosT;

      // Gentle vertical drift
      const drift = Math.sin(t * p.speed * 200 + p.phase) * 0.08;
      const fy = ry + drift;

      // Perspective projection
      const perspective = 2.8;
      const z = rz + perspective;
      if (z <= 0.1) return null;
      const sx = (rx / z) * (W * 0.42) + W / 2;
      const sy = (fy / z) * (H * 0.42) + H / 2;

      // Depth-based opacity (near = brighter)
      const depthFade = Math.max(0, Math.min(1, (z - 0.1) / (perspective + 1.2)));
      const alpha = p.alpha * (0.2 + 0.8 * (1 - depthFade));

      return { sx, sy, z: rz, alpha, size: p.size };
    }).filter(Boolean).sort((a, b) => a.z - b.z);

    for (const pt of rendered) {
      ctx.beginPath();
      ctx.arc(pt.sx, pt.sy, pt.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(196, 172, 128, ${pt.alpha})`;
      ctx.fill();
    }
  }

  loop();
})();
