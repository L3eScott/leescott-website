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
