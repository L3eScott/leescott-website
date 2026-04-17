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

// Contact form handler
var form = document.getElementById('contact-form');
if (form) {
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var btn = form.querySelector('button[type="submit"]');
    var original = btn.textContent;
    btn.textContent = 'Message Sent!';
    btn.style.background = '#27ae60';
    btn.style.borderColor = '#27ae60';
    btn.disabled = true;
    setTimeout(function () {
      btn.textContent = original;
      btn.style.background = '';
      btn.style.borderColor = '';
      btn.disabled = false;
      form.reset();
    }, 4000);
  });
}
