/**
 * work-bg.js — Scattered organic dot field (work.html)
 * Slow-moving clusters of particles that breathe and drift
 * Biological / computational aesthetic — fits "work" page
 * Deliberately sparse: never floods the screen
 */

(function() {
  const canvas = document.getElementById('rd-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H;

  // Minimal noise
  function hash(n) { n = Math.sin(n) * 43758.5453; return n - Math.floor(n); }
  function noise(x, y, t) {
    const ix = Math.floor(x), iy = Math.floor(y);
    const fx = x - ix, fy = y - iy;
    const ux = fx*fx*(3-2*fx), uy = fy*fy*(3-2*fy);
    const a = hash(ix + iy*57 + t*0.3);
    const b = hash(ix+1 + iy*57 + t*0.3);
    const c = hash(ix + (iy+1)*57 + t*0.3);
    const d = hash(ix+1 + (iy+1)*57 + t*0.3);
    return a+(b-a)*ux+(c-a)*uy+(d-b-c+a)*ux*uy;
  }

  // Particle clusters — each cluster has a center that drifts slowly
  const NUM_CLUSTERS = 12;
  const PER_CLUSTER = 18;
  const CLUSTER_RADIUS = 60;
  let clusters = [], t = 0;

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
    initClusters();
  }

  function initClusters() {
    clusters = [];
    for (let i = 0; i < NUM_CLUSTERS; i++) {
      const cx = 0.1 + Math.random() * 0.8;
      const cy = 0.1 + Math.random() * 0.8;
      clusters.push({
        ox: cx, oy: cy,        // base position (normalized)
        phase: Math.random() * Math.PI * 2,
        speed: 0.0002 + Math.random() * 0.0003,
        particles: Array.from({ length: PER_CLUSTER }, () => ({
          rx: (Math.random() - 0.5) * CLUSTER_RADIUS,
          ry: (Math.random() - 0.5) * CLUSTER_RADIUS,
          size: 1.2 + Math.random() * 2.8,
          alpha: 0.12 + Math.random() * 0.28,
          drift: Math.random() * Math.PI * 2,
          driftSpeed: 0.002 + Math.random() * 0.004,
        })),
      });
    }
  }

  resize();
  window.addEventListener('resize', resize);

  function loop() {
    requestAnimationFrame(loop);
    t += 0.008;

    // Slow fade — trails but clears
    ctx.fillStyle = 'rgba(8, 8, 8, 0.18)';
    ctx.fillRect(0, 0, W, H);

    for (const cl of clusters) {
      // Cluster center drifts on noise field
      const nx = cl.ox + 0.12 * (noise(cl.ox * 3, cl.oy * 3, t) - 0.5);
      const ny = cl.oy + 0.08 * (noise(cl.ox * 3 + 7, cl.oy * 3 + 7, t) - 0.5);
      const cx = nx * W;
      const cy = ny * H;

      for (const p of cl.particles) {
        // Each particle orbits its cluster center
        p.drift += p.driftSpeed;
        const px = cx + p.rx * Math.cos(p.drift) * 0.4 + p.rx;
        const py = cy + p.ry * Math.sin(p.drift) * 0.4 + p.ry;

        // Skip if off-screen
        if (px < 0 || px > W || py < 0 || py > H) continue;

        // Pulse alpha
        const pulse = 0.7 + 0.3 * Math.sin(t * 2 + p.drift);
        const a = p.alpha * pulse;

        ctx.beginPath();
        ctx.arc(px, py, p.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(190, 168, 122, ${a})`;
        ctx.fill();
      }
    }
  }

  // Wait for DOM ready since we reference an existing canvas element
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { resize(); loop(); });
  } else {
    loop();
  }
})();
