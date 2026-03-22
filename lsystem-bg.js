/**
 * lsystem-bg.js — L-system branching growth (teaching.html)
 * Plant growth algorithm — generative, pedagogical, organic
 * Trees grow from the bottom, slowly, repeatedly
 * Warm amber on dark — matches site palette
 */

(function() {
  const canvas = document.createElement('canvas');
  canvas.id = 'lsystem-canvas';
  canvas.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;z-index:0;pointer-events:none;opacity:0.28;';
  document.body.insertBefore(canvas, document.body.firstChild);

  const ctx = canvas.getContext('2d');
  let W, H;

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  // L-system rules — simple plant
  const RULES = {
    'F': 'FF',
    'X': 'F+[[X]-X]-F[-FX]+X',
  };
  const ANGLE = 25 * Math.PI / 180;

  function expand(axiom, n) {
    let s = axiom;
    for (let i = 0; i < n; i++) {
      s = s.split('').map(c => RULES[c] || c).join('');
    }
    return s;
  }

  // Generate a list of trees to draw, positioned across the canvas
  function makeTrees() {
    const trees = [];
    const count = Math.max(3, Math.floor(W / 280));
    for (let i = 0; i < count; i++) {
      const iters = 3 + Math.floor(Math.random() * 2); // 3 or 4
      trees.push({
        x: (i + 0.5 + (Math.random() - 0.5) * 0.6) * (W / count),
        y: H,
        str: expand('X', iters),
        len: H * (0.05 + Math.random() * 0.04),
        angle: -Math.PI / 2 + (Math.random() - 0.5) * 0.3,
        alpha: 0.3 + Math.random() * 0.4,
        progress: 0,         // 0..1 — how far through drawing
        phase: Math.random() * 200 | 0, // staggered start
      });
    }
    return trees;
  }

  let trees = makeTrees();
  let frame = 0;

  function drawTree(tree, fraction) {
    // Draw the fraction of the L-system string
    const len = tree.str.length;
    const upTo = Math.floor(len * fraction);

    ctx.save();
    ctx.translate(tree.x, tree.y);

    const stack = [];
    let x = 0, y = 0, angle = tree.angle;
    let segLen = tree.len;

    for (let i = 0; i < upTo; i++) {
      const c = tree.str[i];
      if (c === 'F') {
        const nx = x + Math.cos(angle) * segLen;
        const ny = y + Math.sin(angle) * segLen;
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(nx, ny);
        ctx.strokeStyle = `rgba(200, 172, 120, ${tree.alpha * 0.7})`;
        ctx.lineWidth = 0.6;
        ctx.stroke();
        x = nx; y = ny;
      } else if (c === '+') {
        angle += ANGLE + (Math.random() - 0.5) * 0.08;
      } else if (c === '-') {
        angle -= ANGLE + (Math.random() - 0.5) * 0.08;
      } else if (c === '[') {
        stack.push({ x, y, angle, segLen });
        segLen *= 0.72;
      } else if (c === ']') {
        if (stack.length > 0) {
          ({ x, y, angle, segLen } = stack.pop());
        }
      }
    }
    ctx.restore();
  }

  function loop() {
    requestAnimationFrame(loop);
    frame++;

    // Slow fade
    ctx.fillStyle = 'rgba(18, 14, 10, 0.04)';
    ctx.fillRect(0, 0, W, H);

    for (let t of trees) {
      if (frame < t.phase) continue;
      // Grow slowly
      t.progress = Math.min(1, t.progress + 0.0018);
      drawTree(t, t.progress);
    }

    // When all trees are done, reset after a pause
    if (trees.every(t => t.progress >= 1)) {
      if (frame % 400 === 0) {
        ctx.fillStyle = 'rgba(18, 14, 10, 0.8)';
        ctx.fillRect(0, 0, W, H);
        trees = makeTrees();
        frame = 0;
      }
    }
  }

  loop();
})();
