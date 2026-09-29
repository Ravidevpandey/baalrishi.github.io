'use strict';
// Refuse to run inside another site's frame (clickjacking protection; Pages cannot send X-Frame-Options).
if (window.top !== window.self) {
  document.documentElement.style.display = 'none';
  window.top.location = window.self.location.href;
}
// Core content, navigation, service details and language links work without JavaScript.
const year = document.getElementById('year');
if (year) year.textContent = String(new Date().getFullYear());
// Preserve the current section when switching between the Hindi and English pages.
document.querySelectorAll('.lang-switch a').forEach(link => {
  link.addEventListener('click', () => {
    if (window.location.hash) link.hash = window.location.hash;
  });
});
// Close header popovers (brand meaning, more languages) when clicking elsewhere.
document.addEventListener('click', event => {
  document.querySelectorAll('details.more-langs[open], details.brand-meaning[open]').forEach(d => {
    if (!d.contains(event.target)) d.open = false;
  });
});
