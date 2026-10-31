/* Smart sticky header — desktop only.
   Scroll down  -> header slides up out of view (.hdr--hidden).
   Scroll up    -> header slides back into view.
   At/near top  -> always shown.
   Mobile (<=768px) -> never hidden (normal sticky).
   Added 2026-10-30. */
(function () {
  var hdr = document.querySelector('.hdr');
  if (!hdr) return;

  var desktop = window.matchMedia('(min-width: 769px)');
  var lastY = window.pageYOffset || document.documentElement.scrollTop || 0;
  var ticking = false;
  var TOP = 10;     // px from top where header is always shown
  var DELTA = 5;    // min scroll distance before reacting (anti-jitter)

  function update() {
    var y = window.pageYOffset || document.documentElement.scrollTop || 0;

    if (!desktop.matches) {                 // mobile: always visible
      hdr.classList.remove('hdr--hidden');
      lastY = y; ticking = false; return;
    }

    if (y <= TOP) {
      hdr.classList.remove('hdr--hidden');  // near top -> show
    } else if (Math.abs(y - lastY) > DELTA) {
      if (y > lastY) hdr.classList.add('hdr--hidden');     // down -> hide
      else           hdr.classList.remove('hdr--hidden');  // up   -> show
    }

    lastY = y;
    ticking = false;
  }

  window.addEventListener('scroll', function () {
    if (!ticking) { window.requestAnimationFrame(update); ticking = true; }
  }, { passive: true });

  // If the window is resized down to mobile, make sure the header is visible.
  if (desktop.addEventListener) {
    desktop.addEventListener('change', function () {
      if (!desktop.matches) hdr.classList.remove('hdr--hidden');
    });
  }
})();
