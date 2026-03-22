/**
 * work-bg.js — Sparse drifting particle clusters (work.html)
 * Slow, contemplative — never floods
 */

(function() {
  const canvas = document.getElementById('rd-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H;

  function hash(n) { n = Math.sin(n) * 43758.5453; return n - Math.floor(n); }
  function noise(x, y, t) {
    const ix = Math.floor(x), iy = Math.floor(y);
    const fx = x - ix, fy = y - iy;
    const ux = fx*fx*(3-2*fx), uy = fy*fy*(3-2*fy);
    const a = hash(ix + iy*57 + t*0.3), b = hash(ix+1 + iy*57 + t*0.3);
    const c = hash(ix + (iy+1)*57 + t*0.3), d = hash(ix+1 + (iy+1)*57 + t*0.3);
    return a+(b-a)*ux+(c-a)*uy+(d-b-c+a)*ux*uy;
  }

  const NUM_CLUSTERS = 7;
  const PER_CLUSTER = 10;
  const CLUSTER_RADIUS = 50;
  let clusters = [], t = 0;

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
    clusters = [];
    for (let i = 0; i < NUM_CLUSTERS; i++) {
      clusters.push({
        ox: 0.1 + Math.random() * 0.8,
        oy: 0.1 + Math.random() * 0.8,
        phase: Math.random() * Math.PI * 2,
        particles: Array.from({ length: PER_CLUSTER }, () => ({
          rx: (Math.random() - 0.5) * CLUSTER_RADIUS,
          ry: (Math.random() - 0.5) * CLUSTER_RADIUS,
          size: 1.0 + Math.random() * 2.2,
          alpha: 0.08 + Math.random() * 0.20,
          drift: Math.random() * Math.PI * 2,
          driftSpeed: 0.001 + Math.random() * 0.002,  // slower orbit
        })),
      });
    }
  }

  resize();
  window.addEventListener('resize', resize);

  function loop() {
    requestAnimationFrame(loop);
    t += 0.003;  // much slower time step

    ctx.fillStyle = 'rgba(8, 8, 8, 0.12)';
    ctx.fillRect(0, 0, W, H);

    for (const cl of clusters) {
      const nx = cl.ox + 0.10 * (noise(cl.ox * 3, cl.oy * 3, t) - 0.5);
      const ny = cl.oy + 0.07 * (noise(cl.ox * 3 + 7, cl.oy * 3 + 7, t) - 0.5);
      const cx = nx * W, cy = ny * H;

      for (const p of cl.particles) {
        p.drift += p.driftSpeed;
        const px = cx + p.rx * Math.cos(p.drift) * 0.35 + p.rx;
        const py = cy + p.ry * Math.sin(p.drift) * 0.35 + p.ry;
        if (px < 0 || px > W || py < 0 || py > H) continue;
        const pulse = 0.75 + 0.25 * Math.sin(t * 1.2 + p.drift);
        ctx.beginPath();
        ctx.arc(px, py, p.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(190, 168, 122, ${p.alpha * pulse})`;
        ctx.fill();
      }
    }
  }

  loop();
})();
