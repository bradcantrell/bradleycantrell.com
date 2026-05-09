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

  function initImageModal() {
    var images = document.querySelectorAll('.ch-inline-figure img, .ch-figure-item img');
    if (!images.length) return;

    var modal = document.createElement('div');
    modal.className = 'ch-image-modal';
    modal.setAttribute('aria-hidden', 'true');
    modal.innerHTML = [
      '<div class="ch-image-modal__panel" role="dialog" aria-modal="true" aria-label="Expanded figure view">',
      '<button type="button" class="ch-image-modal__close" aria-label="Close expanded figure view">×</button>',
      '<img class="ch-image-modal__img" alt="">',
      '<div class="ch-image-modal__caption"></div>',
      '</div>'
    ].join('');
    document.body.appendChild(modal);

    var modalImg = modal.querySelector('.ch-image-modal__img');
    var modalCaption = modal.querySelector('.ch-image-modal__caption');
    var closeButton = modal.querySelector('.ch-image-modal__close');
    var lastTrigger = null;

    function closeModal() {
      modal.classList.remove('is-open');
      modal.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('ch-modal-open');
      modalImg.removeAttribute('src');
      modalCaption.innerHTML = '';
      if (lastTrigger) lastTrigger.focus();
    }

    function openModal(image) {
      var figure = image.closest('figure');
      lastTrigger = image;
      modalImg.src = image.currentSrc || image.src;
      modalImg.alt = image.alt || '';
      modalCaption.innerHTML = buildCaptionText(figure);
      modal.classList.add('is-open');
      modal.setAttribute('aria-hidden', 'false');
      document.body.classList.add('ch-modal-open');
      closeButton.focus();
    }

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

  initPrintImages();
  initPrintButton();
  initImageModal();
})();
