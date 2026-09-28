'use strict';
// Core content, navigation, service details and language links work without JavaScript.
const year = document.getElementById('year');
if (year) year.textContent = String(new Date().getFullYear());
// Preserve the current section when switching between the two local translations.
document.querySelectorAll('.native-languages a').forEach(link => {
  link.addEventListener('click', () => {
    const hash = window.location.hash;
    if (hash && hash !== '#languages') link.hash = hash;
  });
});
