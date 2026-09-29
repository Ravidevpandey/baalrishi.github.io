// Admin panel: moderate reviews, reply to customers and view registered users.
import { configured, getFirebase, isAdmin } from './firebase.js';
import { T, errorText } from './i18n.js';
import { el, stars, avatar, formatDate, formatNumber, toast, siteData } from './ui.js';
import { onUser, openLogin } from './auth-ui.js';

export function initAdmin() {
  const root = document.querySelector('[data-app]');
  const services = siteData().services || [];
  let reviews = [];
  let users = [];
  let tab = 'pending';
  let search = '';

  onUser(user => {
    if (!user) return gate(configured ? T.notAdmin : T.comingSoon, true);
    if (!isAdmin(user)) return gate(T.notAdmin, false);
    load();
  });

  function gate(message, showLogin) {
    root.replaceChildren(el('section', { class: 'gate panel' },
      el('img', { src: 'assets/brand/logo-mark.svg', width: 72, height: 72, alt: '' }),
      el('h1', {}, T.adminTitle), el('p', {}, message),
      showLogin && configured && el('button', { type: 'button', class: 'button primary', onclick: () => openLogin() }, T.login)));
  }

  async function load() {
    root.replaceChildren(el('p', { class: 'review-empty' }, T.reviewsLoading));
    try {
      const { db, F } = await getFirebase();
      const [r, u] = await Promise.all([
        F.getDocs(F.collection(db, 'reviews')),
        F.getDocs(F.collection(db, 'users'))
      ]);
      const byTime = (a, b) => (b.createdAt?.toMillis?.() || 0) - (a.createdAt?.toMillis?.() || 0);
      reviews = r.docs.map(d => ({ id: d.id, ...d.data() })).sort(byTime);
      users = u.docs.map(d => ({ id: d.id, ...d.data() })).sort(byTime);
      render();
    } catch (err) {
      root.replaceChildren(el('p', { class: 'review-empty' }, errorText(err)));
    }
  }

  // fields go to Firestore; local mirrors them in memory (without server-side sentinels).
  async function change(id, fields, local = fields, message = T.updated) {
    try {
      const { db, F } = await getFirebase();
      await F.updateDoc(F.doc(db, 'reviews', id), fields);
      Object.assign(reviews.find(r => r.id === id), local);
      toast(message);
      render();
    } catch (err) {
      toast(errorText(err), 'error');
    }
  }

  function render() {
    const approved = reviews.filter(r => r.status === 'approved');
    const avg = approved.length ? approved.reduce((s, r) => s + r.rating, 0) / approved.length : 0;
    const count = s => reviews.filter(r => r.status === s).length;
    const stat = (label, value, accent) => el('div', { class: `stat${accent ? ' accent' : ''}` }, el('strong', {}, value), el('span', {}, label));
    const tabs = [['pending', T.tabPending, count('pending')], ['approved', T.tabApproved, count('approved')], ['hidden', T.tabHidden, count('hidden')], ['all', T.tabAll, reviews.length], ['users', T.tabUsers, users.length]];
    const searchInput = el('input', { type: 'search', placeholder: T.search, 'aria-label': T.search, value: search });
    searchInput.addEventListener('input', () => { search = searchInput.value; drawList(); });
    const listBox = el('div', { class: 'admin-list', 'aria-live': 'polite' });

    root.replaceChildren(
      el('section', { class: 'account-hero' },
        el('img', { src: 'assets/brand/logo-mark.svg', width: 64, height: 64, alt: '' }),
        el('div', {}, el('p', { class: 'eyebrow' }, T.brand), el('h1', {}, T.adminTitle), el('p', {}, T.adminIntro))),
      el('div', { class: 'stats' },
        stat(T.statTotal, reviews.length),
        stat(T.statPending, count('pending'), count('pending') > 0),
        stat(T.statAvg, approved.length ? `${formatNumber(avg)} ★` : '—'),
        stat(T.statUsers, users.length)),
      el('div', { class: 'admin-toolbar' },
        el('div', { class: 'tabs', role: 'tablist' }, tabs.map(([id, label, n]) =>
          el('button', { type: 'button', role: 'tab', 'aria-selected': String(tab === id), class: tab === id ? 'active' : '', onclick: () => { tab = id; render(); } }, label, el('span', { class: 'count' }, n)))),
        searchInput),
      listBox);
    drawList();

    function drawList() {
      const q = search.trim().toLowerCase();
      const userOf = r => users.find(u => u.id === r.uid);
      if (tab === 'users') {
        const rows = users.filter(u => !q || `${u.name} ${u.email}`.toLowerCase().includes(q));
        listBox.replaceChildren(rows.length ? el('div', { class: 'table-wrap' }, el('table', { class: 'users-table' },
          el('thead', {}, el('tr', {}, [T.colName, T.colEmail, T.colMethod, T.colJoined, T.colLast].map(h => el('th', { scope: 'col' }, h)))),
          el('tbody', {}, rows.map(u => el('tr', {},
            el('td', {}, el('span', { class: 'user-cell' }, avatar(u.name, u.photoURL, 'sm'), u.name)),
            el('td', {}, el('a', { href: `mailto:${u.email}` }, u.email)),
            el('td', {}, u.provider === 'google.com' ? 'Google' : 'Email'),
            el('td', {}, formatDate(u.createdAt)),
            el('td', {}, formatDate(u.lastLoginAt))))))) : el('p', { class: 'review-empty' }, T.nothingHere));
        return;
      }
      const rows = reviews.filter(r => (tab === 'all' || r.status === tab)
        && (!q || `${r.name} ${r.text} ${userOf(r)?.email || ''}`.toLowerCase().includes(q)));
      listBox.replaceChildren(...(rows.length ? rows.map(r => adminCard(r, userOf(r))) : [el('p', { class: 'review-empty' }, T.nothingHere)]));
    }
  }

  function adminCard(r, user) {
    const service = services.find(s => s.id === r.service);
    const replyBox = el('textarea', { rows: 3, maxlength: 1000, placeholder: T.replyPlaceholder, 'aria-label': T.reply });
    replyBox.value = r.reply?.text || '';
    const saveReply = async () => {
      const text = replyBox.value.trim();
      if (!text) return;
      const { F } = await getFirebase();
      change(r.id, { reply: { text, updatedAt: F.serverTimestamp() } }, { reply: { text } }, T.replySaved);
    };
    const removeReply = async () => {
      const { F } = await getFirebase();
      change(r.id, { reply: F.deleteField() }, { reply: null });
    };
    const removeReview = async () => {
      if (!confirm(T.confirmDelete)) return;
      try {
        const { db, F } = await getFirebase();
        await F.deleteDoc(F.doc(db, 'reviews', r.id));
        reviews = reviews.filter(x => x.id !== r.id);
        toast(T.deleted);
        render();
      } catch (err) {
        toast(errorText(err), 'error');
      }
    };
    return el('article', { class: `review-card admin ${r.status}` },
      el('header', {},
        avatar(r.name, user?.photoURL),
        el('div', {},
          el('strong', {}, r.name),
          el('small', {}, [user?.email, formatDate(r.createdAt), service?.title, r.updatedAt && T.edited].filter(Boolean).join(' · '))),
        el('div', { class: 'card-meta' }, stars(r.rating), el('span', { class: `chip ${r.status}` }, T.status[r.status] || r.status))),
      el('p', { class: 'review-text' }, r.text),
      el('div', { class: 'reply-editor' },
        el('label', {}, el('strong', {}, T.reply), replyBox),
        el('div', { class: 'templates' }, el('small', {}, `${T.templates}:`),
          T.replyTemplates.map((text, i) => el('button', { type: 'button', class: 'chip-button', title: text, onclick: () => { replyBox.value = text; replyBox.focus(); } }, `${i + 1}`)))),
      el('div', { class: 'button-row' },
        el('button', { type: 'button', class: 'button primary small', onclick: saveReply }, T.saveReply),
        r.reply?.text && el('button', { type: 'button', class: 'button outline small', onclick: removeReply }, T.removeReply),
        el('span', { class: 'spacer' }),
        r.status !== 'approved' && el('button', { type: 'button', class: 'button success small', onclick: () => change(r.id, { status: 'approved' }) }, T.publish),
        r.status !== 'hidden' && el('button', { type: 'button', class: 'button outline small', onclick: () => change(r.id, { status: 'hidden' }) }, T.hide),
        el('button', { type: 'button', class: 'button danger small', onclick: removeReview }, T.delete)));
  }
}
