// Public "experiences" section on the home page: rating summary and published reviews.
import { configured, getFirebase } from './firebase.js';
import { T } from './i18n.js';
import { el, stars, avatar, formatDate, formatNumber, siteData } from './ui.js';
import { openReviewForm } from './review-form.js';

const PAGE = 6;

export function reviewCard(review, services) {
  const service = services.find(s => s.id === review.service);
  return el('article', { class: 'review-card' },
    el('header', {},
      avatar(review.name),
      el('div', {}, el('strong', {}, review.name), el('small', {}, [formatDate(review.createdAt), service && ` · ${service.title}`].filter(Boolean).join(''))),
      stars(review.rating)),
    el('p', { class: 'review-text' }, review.text),
    review.reply?.text && el('div', { class: 'review-reply' },
      el('strong', {}, T.replyFrom), el('p', {}, review.reply.text)));
}

export async function initReviews() {
  const section = document.getElementById('reviews');
  if (!section) return;
  const list = section.querySelector('[data-review-list]');
  const summary = section.querySelector('[data-rating-summary]');
  const services = siteData().services || [];
  section.querySelector('[data-write-review]').addEventListener('click', async () => {
    if (await openReviewForm()) load();
  });

  async function load() {
    if (!configured) {
      list.replaceChildren(el('p', { class: 'review-empty' }, T.reviewsUnavailable));
      return;
    }
    try {
      const { db, F } = await getFirebase();
      const snap = await F.getDocs(F.query(F.collection(db, 'reviews'), F.where('status', '==', 'approved')));
      const reviews = snap.docs.map(d => ({ id: d.id, ...d.data() }))
        .sort((a, b) => (b.createdAt?.toMillis?.() || 0) - (a.createdAt?.toMillis?.() || 0));
      renderSummary(reviews);
      renderList(reviews);
    } catch {
      list.replaceChildren(el('p', { class: 'review-empty' }, T.err.default));
    }
  }

  function renderSummary(reviews) {
    const n = reviews.length;
    const avg = n ? reviews.reduce((sum, r) => sum + r.rating, 0) / n : 0;
    summary.querySelector('[data-avg]').textContent = n ? formatNumber(avg) : '—';
    summary.querySelector('[data-avg-stars]').replaceChildren(stars(avg, false));
    summary.querySelector('[data-count]').textContent = n === 1 ? T.basedOnOne : n ? T.basedOn(n) : T.noReviews;
    summary.querySelectorAll('[data-bar]').forEach(row => {
      const value = Number(row.dataset.bar);
      const count = reviews.filter(r => r.rating === value).length;
      row.querySelector('i').style.width = n ? `${(count / n) * 100}%` : '0';
      row.querySelector('output').textContent = count;
    });
  }

  function renderList(reviews) {
    if (!reviews.length) {
      list.replaceChildren(el('p', { class: 'review-empty' }, T.noReviews));
      return;
    }
    let shown = PAGE;
    const draw = () => {
      const more = shown < reviews.length && el('button', { type: 'button', class: 'button outline', onclick: () => { shown += PAGE; draw(); } }, T.showMore);
      list.replaceChildren(...reviews.slice(0, shown).map(r => reviewCard(r, services)), ...(more ? [more] : []));
    };
    draw();
  }

  load();
}
