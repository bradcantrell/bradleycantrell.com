(function() {
  function extractBackgroundUrl(value) {
    if (!value) return '';
    var match = value.match(/url\((['"]?)(.*?)\1\)/);
    return match ? match[2] : '';
  }

  function addPrintImage(container, bgSelector, className, altText) {
    var bg = container.querySelector(bgSelector);
    if (!bg || container.querySelector('.' + className)) return;

    var imageUrl = extractBackgroundUrl(bg.style.backgroundImage);
    if (!imageUrl) return;

    var img = document.createElement('img');
    img.className = className;
    img.src = imageUrl;
    img.alt = altText || '';
    bg.insertAdjacentElement('afterend', img);
  }

  function getCaptionText(node, selector, fallback) {
    var el = node.querySelector(selector);
    return el ? el.textContent.trim() : fallback;
  }

  function initPrintImages() {
    var hero = document.querySelector('.ch-hero');
    if (hero) {
      var title = document.querySelector('.ch-hero__title');
      addPrintImage(hero, '.ch-hero__bg', 'ch-hero__print-img', title ? title.textContent.trim() : 'Chapter hero image');
    }

    document.querySelectorAll('.ch-backdrop').forEach(function(backdrop) {
      var title = backdrop.querySelector('.ch-backdrop__caption-title');
      addPrintImage(
        backdrop,
        '.ch-backdrop__img',
        'ch-backdrop__print-img',
        title ? title.textContent.trim() : 'Chapter figure'
      );
    });

    document.querySelectorAll('.ch-quote-panel').forEach(function(panel) {
      var title = getCaptionText(panel, '.ch-quote-panel__caption-title', 'Chapter figure');
      addPrintImage(
        panel,
        '.ch-quote-panel__img',
        'ch-quote-panel__print-img',
        title
      );
    });
  }

  function initPrintButton() {
    var main = document.querySelector('.ch-main');
    if (!main || document.querySelector('.ch-tools')) return;

    var tools = document.createElement('div');
    tools.className = 'ch-tools';

    var printButton = document.createElement('button');
    printButton.type = 'button';
    printButton.className = 'ch-tool-button';
    printButton.textContent = 'Print Chapter';
    printButton.setAttribute('aria-label', 'Print this chapter');
    printButton.addEventListener('click', function() {
      window.print();
    });

    tools.appendChild(printButton);
    main.appendChild(tools);
  }

  function buildCaptionText(figure) {
    if (!figure) return '';
    var number = figure.querySelector('.ch-inline-figure__num, .fig-num');
    var caption = figure.querySelector('.ch-inline-figure__caption');
    var figcaption = figure.querySelector('figcaption');

    if (number || caption) {
      return (
        '<strong>' + (number ? number.textContent.trim() : 'Figure') + '</strong>' +
        '<span>' + (caption ? caption.textContent.trim() : '') + '</span>'
      );
    }

    if (figcaption) {
      return '<span>' + figcaption.textContent.trim() + '</span>';
    }

    return '';
  }

  function isSvgSrc(src) {
    if (!src) return false;
    return /\.svg(\?|#|$)/i.test(src);
  }

  var svgPanZoomPromise = null;
  function loadSvgPanZoom() {
    if (window.svgPanZoom) return Promise.resolve(window.svgPanZoom);
    if (svgPanZoomPromise) return svgPanZoomPromise;
    svgPanZoomPromise = new Promise(function(resolve, reject) {
      var s = document.createElement('script');
      s.src = 'svg-pan-zoom.min.js';
      s.async = true;
      s.onload = function() { resolve(window.svgPanZoom); };
      s.onerror = function() { reject(new Error('failed to load svg-pan-zoom')); };
      document.head.appendChild(s);
    });
    return svgPanZoomPromise;
  }

  function initImageModal() {
    var images = document.querySelectorAll('.ch-inline-figure img, .ch-figure-item img');
    if (!images.length) return;

    var modal = document.createElement('div');
    modal.className = 'ch-image-modal';
    modal.setAttribute('aria-hidden', 'true');
    modal.innerHTML = [
      '<div class="ch-image-modal__panel" role="dialog" aria-modal="true" aria-label="Expanded figure view">',
      '<button type="button" class="ch-image-modal__close" aria-label="Close expanded figure view">×</button>',
      '<div class="ch-image-modal__svg-frame" hidden>',
      '<div class="ch-image-modal__zoom-controls">',
      '<button type="button" class="ch-image-modal__zoom-btn" data-zoom="in"  aria-label="Zoom in">+</button>',
      '<button type="button" class="ch-image-modal__zoom-btn" data-zoom="out" aria-label="Zoom out">−</button>',
      '<button type="button" class="ch-image-modal__zoom-btn" data-zoom="reset" aria-label="Reset zoom">⤾</button>',
      '</div>',
      '<button type="button" class="ch-image-modal__svg-close" aria-label="Close expanded figure view">×</button>',
      '<div class="ch-image-modal__zoom-hint">Scroll to zoom · drag to pan · esc to close</div>',
      '</div>',
      '<div class="ch-image-modal__raster-frame" hidden>',
      '<div class="ch-image-modal__raster-stage"><img class="ch-image-modal__raster-img" alt=""></div>',
      '<div class="ch-image-modal__zoom-controls">',
      '<button type="button" class="ch-image-modal__zoom-btn" data-rzoom="in"  aria-label="Zoom in">+</button>',
      '<button type="button" class="ch-image-modal__zoom-btn" data-rzoom="out" aria-label="Zoom out">−</button>',
      '<button type="button" class="ch-image-modal__zoom-btn" data-rzoom="reset" aria-label="Reset zoom">⤾</button>',
      '</div>',
      '<button type="button" class="ch-image-modal__svg-close" data-raster-close="1" aria-label="Close expanded figure view">×</button>',
      '<div class="ch-image-modal__zoom-hint">Scroll to zoom · drag to pan · esc to close</div>',
      '</div>',
      '<img class="ch-image-modal__img" alt="">',
      '<div class="ch-image-modal__caption"></div>',
      '</div>'
    ].join('');
    document.body.appendChild(modal);

    var panel = modal.querySelector('.ch-image-modal__panel');
    var modalImg = modal.querySelector('.ch-image-modal__img');
    var modalCaption = modal.querySelector('.ch-image-modal__caption');
    var closeButton = modal.querySelector('.ch-image-modal__close');
    var svgFrame = modal.querySelector('.ch-image-modal__svg-frame');
    var lastTrigger = null;
    var activePanZoom = null;
    var activeRasterZoom = null;

    function destroyPanZoom() {
      if (activePanZoom && typeof activePanZoom.destroy === 'function') {
        try { activePanZoom.destroy(); } catch (e) { /* noop */ }
      }
      activePanZoom = null;
    }

    function clearSvgFrame() {
      destroyPanZoom();
      // Remove any injected <svg> while preserving controls + hint.
      Array.prototype.slice.call(svgFrame.querySelectorAll('svg')).forEach(function(node) {
        node.parentNode.removeChild(node);
      });
    }

    function destroyRasterZoom() {
      if (activeRasterZoom && typeof activeRasterZoom.destroy === 'function') {
        try { activeRasterZoom.destroy(); } catch (e) { /* noop */ }
      }
      activeRasterZoom = null;
    }

    function attachRasterPanZoom(stageEl, frameEl) {
      // CSS transform pan/zoom for raster images. Mouse wheel zooms toward
      // the cursor; click-and-drag pans. Double-click toggles between fit
      // and 2x zoom. Touch is supported via simple drag (no pinch).
      var state = { scale: 1, tx: 0, ty: 0, min: 1, max: 12 };
      function apply() {
        stageEl.style.transform =
          'translate(' + state.tx + 'px,' + state.ty + 'px) scale(' + state.scale + ')';
      }
      function clamp(v, lo, hi) { return Math.min(hi, Math.max(lo, v)); }
      function zoomAt(clientX, clientY, factor) {
        var rect = frameEl.getBoundingClientRect();
        var cx = clientX - rect.left - rect.width / 2;
        var cy = clientY - rect.top - rect.height / 2;
        var next = clamp(state.scale * factor, state.min, state.max);
        var k = next / state.scale;
        state.tx = cx - (cx - state.tx) * k;
        state.ty = cy - (cy - state.ty) * k;
        state.scale = next;
        apply();
      }
      function reset() { state.scale = 1; state.tx = 0; state.ty = 0; apply(); }

      function onWheel(e) {
        e.preventDefault();
        var factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
        zoomAt(e.clientX, e.clientY, factor);
      }
      var dragging = false;
      var lastX = 0, lastY = 0;
      function onPointerDown(e) {
        if (e.button !== undefined && e.button !== 0) return;
        dragging = true;
        lastX = e.clientX; lastY = e.clientY;
        frameEl.classList.add('is-grabbing');
        frameEl.setPointerCapture && frameEl.setPointerCapture(e.pointerId || 0);
      }
      function onPointerMove(e) {
        if (!dragging) return;
        var dx = e.clientX - lastX;
        var dy = e.clientY - lastY;
        lastX = e.clientX; lastY = e.clientY;
        state.tx += dx; state.ty += dy;
        apply();
      }
      function onPointerUp() {
        dragging = false;
        frameEl.classList.remove('is-grabbing');
      }
      function onDblClick(e) {
        if (state.scale > 1.05) reset();
        else zoomAt(e.clientX, e.clientY, 2);
      }

      frameEl.addEventListener('wheel', onWheel, { passive: false });
      frameEl.addEventListener('pointerdown', onPointerDown);
      window.addEventListener('pointermove', onPointerMove);
      window.addEventListener('pointerup', onPointerUp);
      frameEl.addEventListener('dblclick', onDblClick);

      reset();

      function centerZoom(factor) {
        var rect = frameEl.getBoundingClientRect();
        zoomAt(rect.left + rect.width/2, rect.top + rect.height/2, factor);
      }

      return {
        zoomIn: function() { centerZoom(1.4); },
        zoomOut: function() { centerZoom(1/1.4); },
        reset: reset,
        destroy: function() {
          frameEl.removeEventListener('wheel', onWheel);
          frameEl.removeEventListener('pointerdown', onPointerDown);
          window.removeEventListener('pointermove', onPointerMove);
          window.removeEventListener('pointerup', onPointerUp);
          frameEl.removeEventListener('dblclick', onDblClick);
          stageEl.style.transform = '';
        }
      };
    }

    var rasterFrame = modal.querySelector('.ch-image-modal__raster-frame');
    var rasterStage = modal.querySelector('.ch-image-modal__raster-stage');
    var rasterImg = modal.querySelector('.ch-image-modal__raster-img');

    function closeModal() {
      modal.classList.remove('is-open');
      modal.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('ch-modal-open');
      modalImg.removeAttribute('src');
      modalCaption.innerHTML = '';
      clearSvgFrame();
      destroyRasterZoom();
      rasterImg.removeAttribute('src');
      rasterFrame.setAttribute('hidden', '');
      svgFrame.setAttribute('hidden', '');
      panel.classList.remove('ch-image-modal__panel--svg');
      panel.classList.remove('ch-image-modal__panel--raster-zoom');
      if (lastTrigger) lastTrigger.focus();
    }

    function openAsImage(image, figure) {
      panel.classList.remove('ch-image-modal__panel--svg');
      panel.classList.remove('ch-image-modal__panel--raster-zoom');
      svgFrame.setAttribute('hidden', '');
      rasterFrame.setAttribute('hidden', '');
      modalImg.removeAttribute('hidden');
      modalImg.src = image.currentSrc || image.src;
      modalImg.alt = image.alt || '';
      modalCaption.innerHTML = buildCaptionText(figure);
    }

    function openAsZoomImage(image, figure) {
      panel.classList.add('ch-image-modal__panel--raster-zoom');
      svgFrame.setAttribute('hidden', '');
      modalImg.removeAttribute('src');
      rasterFrame.removeAttribute('hidden');
      destroyRasterZoom();
      rasterImg.src = image.currentSrc || image.src;
      rasterImg.alt = image.alt || '';
      modalCaption.innerHTML = buildCaptionText(figure);
      // Wait until the image loads so layout is stable, then attach pan/zoom.
      var attach = function() {
        activeRasterZoom = attachRasterPanZoom(rasterStage, rasterFrame);
      };
      if (rasterImg.complete && rasterImg.naturalWidth) {
        requestAnimationFrame(attach);
      } else {
        rasterImg.addEventListener('load', attach, { once: true });
      }
    }

    function openAsSvg(image, figure) {
      panel.classList.add('ch-image-modal__panel--svg');
      modalImg.removeAttribute('src');
      svgFrame.removeAttribute('hidden');
      modalCaption.innerHTML = buildCaptionText(figure);

      var src = image.currentSrc || image.src;
      clearSvgFrame();

      Promise.all([
        fetch(src).then(function(r) { return r.ok ? r.text() : Promise.reject(r.status); }),
        loadSvgPanZoom()
      ]).then(function(results) {
        var markup = results[0];
        var holder = document.createElement('div');
        holder.innerHTML = markup;
        var svgEl = holder.querySelector('svg');
        if (!svgEl) throw new Error('no <svg> root');
        svgEl.removeAttribute('width');
        svgEl.removeAttribute('height');
        svgEl.setAttribute('preserveAspectRatio', 'xMidYMid meet');
        svgFrame.appendChild(svgEl);
        if (window.svgPanZoom) {
          activePanZoom = window.svgPanZoom(svgEl, {
            zoomEnabled: true,
            controlIconsEnabled: false,
            fit: true,
            center: true,
            minZoom: 0.5,
            maxZoom: 20,
            dblClickZoomEnabled: true,
            mouseWheelZoomEnabled: true
          });
        }
      }).catch(function() {
        // Fallback: just show the SVG as an <img> with no zoom.
        panel.classList.remove('ch-image-modal__panel--svg');
        svgFrame.setAttribute('hidden', '');
        modalImg.src = src;
      });
    }

    function shouldZoomRaster(figure) {
      if (!figure) return false;
      if (figure.classList.contains('ch-inline-figure--map')) return true;
      if (figure.dataset && figure.dataset.zoomable === 'true') return true;
      return false;
    }

    function openModal(image) {
      var figure = image.closest('figure');
      lastTrigger = image;
      var src = image.currentSrc || image.src;
      if (isSvgSrc(src)) {
        openAsSvg(image, figure);
      } else if (shouldZoomRaster(figure)) {
        openAsZoomImage(image, figure);
      } else {
        openAsImage(image, figure);
      }
      modal.classList.add('is-open');
      modal.setAttribute('aria-hidden', 'false');
      document.body.classList.add('ch-modal-open');
      closeButton.focus();
    }

    svgFrame.addEventListener('click', function(event) {
      if (event.target.closest('.ch-image-modal__svg-close')) {
        closeModal();
        return;
      }
      var btn = event.target.closest('[data-zoom]');
      if (!btn || !activePanZoom) return;
      var mode = btn.getAttribute('data-zoom');
      if (mode === 'in') activePanZoom.zoomIn();
      else if (mode === 'out') activePanZoom.zoomOut();
      else if (mode === 'reset') { activePanZoom.resetZoom(); activePanZoom.resetPan(); }
    });

    rasterFrame.addEventListener('click', function(event) {
      if (event.target.closest('[data-raster-close]')) {
        closeModal();
        return;
      }
      var btn = event.target.closest('[data-rzoom]');
      if (!btn || !activeRasterZoom) return;
      var mode = btn.getAttribute('data-rzoom');
      if (mode === 'in') activeRasterZoom.zoomIn();
      else if (mode === 'out') activeRasterZoom.zoomOut();
      else if (mode === 'reset') activeRasterZoom.reset();
    });

    images.forEach(function(image) {
      image.tabIndex = 0;
      image.setAttribute('role', 'button');
      image.setAttribute('aria-haspopup', 'dialog');
      image.setAttribute('aria-label', (image.alt || 'Figure image') + '. Activate to enlarge.');

      image.addEventListener('click', function() {
        openModal(image);
      });

      image.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          openModal(image);
        }
      });
    });

    closeButton.addEventListener('click', closeModal);

    modal.addEventListener('click', function(event) {
      if (event.target === modal) closeModal();
    });

    document.addEventListener('keydown', function(event) {
      if (event.key === 'Escape' && modal.classList.contains('is-open')) {
        closeModal();
      }
    });
  }

  function initParallax() {
    var backgrounds = document.querySelectorAll('.ch-hero__bg, .ch-backdrop__img, .ch-quote-panel__img');
    if (!backgrounds.length) return;

    var media = window.matchMedia('(prefers-reduced-motion: no-preference)');
    if (!media.matches) return;

    var ticking = false;

    function updateParallax() {
      backgrounds.forEach(function(bg) {
        var parent = bg.parentElement;
        if (!parent) return;

        var rect = parent.getBoundingClientRect();
        var centerOffset = rect.top + rect.height / 2 - window.innerHeight / 2;
        bg.style.transform = 'translateY(' + (centerOffset * 0.22) + 'px)';
      });

      ticking = false;
    }

    function onScroll() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(updateParallax);
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    updateParallax();
  }

  initPrintImages();
  initPrintButton();
  initImageModal();
  initParallax();
})();
