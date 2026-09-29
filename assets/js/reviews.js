// Public "experiences" section on the home page: rating summary and published reviews.
import { configured, getFirebase, isLive } from './firebase.js';
import { T } from './i18n.js';
import { el, stars, avatar, formatDate, formatNumber, siteData } from './ui.js';
import { openReviewForm } from './review-form.js';

const PAGE = 6;

// Best first: featured, then more stars, then newest.
export const bestFirst = (a, b) => (Number(Boolean(b.featured)) - Number(Boolean(a.featured)))
  || (b.rating - a.rating)
  || ((b.createdAt?.toMillis?.() || 0) - (a.createdAt?.toMillis?.() || 0));

export function reviewCard(review, services) {
  const service = services.find(s => s.id === review.service);
  return el('article', { class: `review-card${review.featured ? ' featured' : ''}` },
    review.featured && el('span', { class: 'featured-badge' }, `★ ${T.featured}`),
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
  let reviews = [];
  let filter = 0;
  const write = async () => {
    if (await openReviewForm()) load();
  };
  section.querySelector('[data-write-review]').addEventListener('click', write);
  summary.querySelectorAll('[data-bar] button').forEach(button => {
    button.addEventListener('click', () => {
      const value = Number(button.closest('[data-bar]').dataset.bar);
      filter = filter === value ? 0 : value;
      renderList();
    });
  });

  async function load() {
    if (!configured) {
      list.replaceChildren(el('p', { class: 'review-empty' }, T.reviewsUnavailable));
      return;
    }
    try {
      const { db, F } = await getFirebase();
      const snap = await F.getDocs(F.query(F.collection(db, 'reviews'), F.where('status', '==', 'approved')));
      reviews = snap.docs.map(d => ({ id: d.id, ...d.data() })).filter(isLive).sort(bestFirst);
      renderSummary();
      renderList();
    } catch {
      list.replaceChildren(el('p', { class: 'review-empty' }, T.err.default));
    }
  }

  function renderSummary() {
    const n = reviews.length;
    const avg = n ? reviews.reduce((sum, r) => sum + r.rating, 0) / n : 0;
    summary.querySelector('[data-avg]').textContent = n ? formatNumber(avg) : '—';
    summary.querySelector('[data-avg-stars]').replaceChildren(stars(avg, false));
    summary.querySelector('[data-count]').textContent = n === 1 ? T.basedOnOne : n ? T.basedOn(n) : T.noRatings;
    summary.querySelectorAll('[data-bar]').forEach(row => {
      const value = Number(row.dataset.bar);
      const count = reviews.filter(r => r.rating === value).length;
      row.querySelector('i').style.width = n ? `${(count / n) * 100}%` : '0';
      row.querySelector('output').textContent = count;
      row.querySelector('button').disabled = count === 0;
    });
  }

  function renderList() {
    summary.querySelectorAll('[data-bar]').forEach(row => {
      row.querySelector('button').setAttribute('aria-pressed', String(Number(row.dataset.bar) === filter));
    });
    if (!reviews.length) {
      list.replaceChildren(el('div', { class: 'review-empty first' },
        stars(5, false),
        el('strong', {}, T.firstTitle),
        el('p', {}, T.noReviews),
        el('button', { type: 'button', class: 'button primary', onclick: write }, T.firstReview)));
      return;
    }
    const shownReviews = filter ? reviews.filter(r => r.rating === filter) : reviews;
    const bar = filter && el('div', { class: 'filter-bar' },
      el('span', {}, T.filtered(filter)),
      el('button', { type: 'button', class: 'link-button strong', onclick: () => { filter = 0; renderList(); } }, T.showAll));
    if (!shownReviews.length) {
      list.replaceChildren(...[bar, el('p', { class: 'review-empty' }, T.noneForFilter)].filter(Boolean));
      return;
    }
    let shown = PAGE;
    const draw = () => {
      const more = shown < shownReviews.length && el('button', { type: 'button', class: 'button outline', onclick: () => { shown += PAGE; draw(); } }, T.showMore);
      list.replaceChildren(...[bar, ...shownReviews.slice(0, shown).map(r => reviewCard(r, services)), more].filter(Boolean));
    };
    draw();
  }

  load();
}
