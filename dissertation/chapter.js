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

    function closeModal() {
      modal.classList.remove('is-open');
      modal.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('ch-modal-open');
      modalImg.removeAttribute('src');
      modalCaption.innerHTML = '';
      clearSvgFrame();
      svgFrame.setAttribute('hidden', '');
      panel.classList.remove('ch-image-modal__panel--svg');
      if (lastTrigger) lastTrigger.focus();
    }

    function openAsImage(image, figure) {
      panel.classList.remove('ch-image-modal__panel--svg');
      svgFrame.setAttribute('hidden', '');
      modalImg.removeAttribute('hidden');
      modalImg.src = image.currentSrc || image.src;
      modalImg.alt = image.alt || '';
      modalCaption.innerHTML = buildCaptionText(figure);
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

    function openModal(image) {
      var figure = image.closest('figure');
      lastTrigger = image;
      var src = image.currentSrc || image.src;
      if (isSvgSrc(src)) {
        openAsSvg(image, figure);
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
