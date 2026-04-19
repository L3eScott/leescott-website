// Mobile navigation toggle
var navToggle = document.querySelector('.nav-toggle');
var navMenu = document.querySelector('nav ul');

if (navToggle && navMenu) {
  navToggle.addEventListener('click', function () {
    var isOpen = navMenu.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', isOpen);
  });

  navMenu.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
      navMenu.classList.remove('open');
      navToggle.setAttribute('aria-expanded', 'false');
    });
  });
}

// Active navigation link
(function () {
  var page = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('nav ul li a').forEach(function (link) {
    if (link.getAttribute('href') === page) {
      link.classList.add('active');
    }
  });
})();

// Button click tracking (GA4)
document.querySelectorAll('.btn').forEach(function (button) {
  button.addEventListener('click', function () {
    if (typeof gtag === 'function') {
      gtag('event', 'button_click', {
        event_category: 'engagement',
        event_label: this.innerText
      });
    }
  });
});

// Lead form submission tracking (GA4)
var leadForm = document.getElementById('lead-form');
if (leadForm) {
  leadForm.addEventListener('submit', function () {
    if (typeof gtag === 'function') {
      gtag('event', 'form_submit', {
        event_category: 'lead',
        event_label: 'Contact Form'
      });
    }
  });
}

// Floating founding client banner
(function () {
  var STORAGE_KEY = 'founding_banner_closed';
  var RESHOW_MS = 5 * 60 * 1000; // 5 minutes
  var banner = null;
  var shown = false;

  function shouldShow() {
    var closed = localStorage.getItem(STORAGE_KEY);
    if (!closed) return true;
    return (Date.now() - parseInt(closed, 10)) >= RESHOW_MS;
  }

  function showBanner() {
    if (shown || !banner) return;
    shown = true;
    banner.classList.add('visible');
  }

  function hideBanner(save) {
    if (!banner) return;
    banner.classList.remove('visible');
    if (save) localStorage.setItem(STORAGE_KEY, Date.now().toString());
  }

  function buildBanner() {
    banner = document.createElement('div');
    banner.id = 'founding-banner';
    banner.setAttribute('role', 'complementary');
    banner.setAttribute('aria-label', 'Founding Client Offer');

    var isContactPage = window.location.pathname.indexOf('contact') !== -1;
    var applyHref = isContactPage ? '#lead-form' : 'contact.html#lead-form';

    banner.innerHTML =
      '<div class="banner-text">' +
        '<strong>Now Accepting Founding Clients</strong>' +
        '<p>A website that works like an employee &mdash; captures leads, follows up automatically. Apply to be considered.</p>' +
      '</div>' +
      '<div class="banner-actions">' +
        '<a href="' + applyHref + '" class="btn-banner" id="banner-apply">Apply Now</a>' +
        '<button class="btn-close" id="banner-close" aria-label="Close banner">&times;</button>' +
      '</div>';

    document.body.appendChild(banner);

    // Slide in after 10 seconds
    setTimeout(showBanner, 10000);

    // Exit intent: mouse leaves viewport toward browser chrome (back/close buttons)
    document.addEventListener('mouseleave', function (e) {
      if (e.clientY <= 0 && shouldShow()) {
        shown = false; // allow re-trigger if dismissed and cooldown expired
        showBanner();
      }
    });

    // Tab close / page hide attempt
    window.addEventListener('pagehide', function () {
      if (shouldShow()) showBanner();
    });

    // Smooth scroll on contact page
    if (isContactPage) {
      document.getElementById('banner-apply').addEventListener('click', function (e) {
        var target = document.getElementById('lead-form');
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth' });
        }
        hideBanner(true);
      });
    }

    // Close button
    document.getElementById('banner-close').addEventListener('click', function () {
      hideBanner(true);
    });
  }

  if (shouldShow()) {
    buildBanner();
  }
})();
