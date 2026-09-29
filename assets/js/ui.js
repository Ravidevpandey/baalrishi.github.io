// Small DOM helpers shared by the login, review, account and admin screens.
import { lang, T } from './i18n.js';

// Build an element. User-supplied strings are always inserted as text, never as HTML.
export function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value == null || value === false) continue;
    if (key === 'class') node.className = value;
    else if (key.startsWith('on')) node.addEventListener(key.slice(2), value);
    else if (value === true) node.setAttribute(key, '');
    else node.setAttribute(key, value);
  }
  for (const child of children.flat()) {
    if (child == null || child === false) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
}

// Trusted, static SVG icons only.
const ICONS = {
  user: '<path d="M12 12a4.5 4.5 0 1 0 0-9 4.5 4.5 0 0 0 0 9Zm0 2c-4.4 0-8 2.3-8 5.2V21h16v-1.8c0-2.9-3.6-5.2-8-5.2Z"/>',
  star: '<path d="m12 2.8 2.8 5.9 6.4.8-4.7 4.4 1.2 6.4L12 17.2l-5.7 3.1 1.2-6.4-4.7-4.4 6.4-.8Z"/>',
  close: '<path d="M6 6l12 12M18 6 6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/>',
  google: '<path fill="#EA4335" d="M12 10.2v3.9h5.4c-.2 1.3-1.6 3.8-5.4 3.8-3.2 0-5.9-2.7-5.9-6s2.7-6 5.9-6c1.9 0 3.1.8 3.8 1.5l2.6-2.5C16.8 3.3 14.6 2.3 12 2.3 6.6 2.3 2.3 6.6 2.3 12s4.3 9.7 9.7 9.7c5.6 0 9.3-3.9 9.3-9.5 0-.6-.1-1.1-.2-1.6H12Z"/><path fill="#34A853" d="M3.4 7.5 6.6 9.8C7.4 7.8 9.5 6 12 6c1.9 0 3.1.8 3.8 1.5l2.6-2.5C16.8 3.3 14.6 2.3 12 2.3 8.3 2.3 5 4.4 3.4 7.5Z"/><path fill="#FBBC05" d="M12 21.7c2.5 0 4.7-.8 6.3-2.3l-2.9-2.4c-.8.6-1.9 1-3.4 1-3.7 0-5.2-2.5-5.5-3.8l-3.2 2.5c1.6 3.1 4.9 5 8.7 5Z"/><path fill="#4285F4" d="M21.3 12.2c0-.6-.1-1.1-.2-1.6H12v3.9h5.4c-.3 1.2-1 2.2-2 2.9l2.9 2.4c1.9-1.8 3-4.4 3-7.6Z"/>'
};
export function icon(name, cls = 'icon') {
  const span = document.createElement('span');
  span.className = cls;
  span.setAttribute('aria-hidden', 'true');
  span.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor">${ICONS[name]}</svg>`;
  return span;
}

export function stars(rating, label = true) {
  const wrap = el('span', { class: 'stars', role: label ? 'img' : null, 'aria-label': label ? `${rating} / 5` : null, 'aria-hidden': label ? null : 'true' });
  for (let i = 1; i <= 5; i++) wrap.append(icon('star', i <= Math.round(rating) ? 'star on' : 'star'));
  return wrap;
}

export function initials(name) {
  return (name || '?').trim().charAt(0).toUpperCase() || '?';
}

export function avatar(name, photoURL, size = 'md') {
  if (photoURL) return el('img', { class: `avatar ${size}`, src: photoURL, alt: '', referrerpolicy: 'no-referrer', width: 40, height: 40 });
  return el('span', { class: `avatar ${size}`, 'aria-hidden': 'true' }, initials(name));
}

const locale = lang === 'hi' ? 'hi-IN' : 'en-IN';
export function formatDate(value) {
  const date = value && typeof value.toDate === 'function' ? value.toDate() : value instanceof Date ? value : null;
  if (!date) return '';
  return new Intl.DateTimeFormat(locale, { day: 'numeric', month: 'short', year: 'numeric' }).format(date);
}
export const formatNumber = (n, digits = 1) => new Intl.NumberFormat(locale, { minimumFractionDigits: digits, maximumFractionDigits: digits }).format(n);

let toastTimer;
export function toast(message, kind = 'ok') {
  let box = document.querySelector('.toast');
  if (!box) {
    box = el('div', { class: 'toast', role: 'status', 'aria-live': 'polite' });
    document.body.append(box);
  }
  box.textContent = message;
  box.dataset.kind = kind;
  box.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => box.classList.remove('show'), 4200);
}

// A modal <dialog> with a title, close button and body. Removed from the DOM when closed.
export function modal(title, body, { wide = false } = {}) {
  const dialog = el('dialog', { class: `modal${wide ? ' wide' : ''}`, 'aria-labelledby': 'modal-title' },
    el('div', { class: 'modal-head' },
      el('h2', { id: 'modal-title' }, title),
      el('button', { type: 'button', class: 'icon-button', 'aria-label': T.close, onclick: () => dialog.close() }, icon('close'))),
    body);
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => dialog.remove());
  document.body.append(dialog);
  dialog.showModal();
  return dialog;
}

export function siteData() {
  try { return JSON.parse(document.getElementById('site-data').textContent); } catch { return {}; }
}
