// Admin panel: moderate reviews, reply to customers and view registered users.
import { configured, getFirebase, isAdmin, isLive, RETENTION_MS } from './firebase.js';
import { T, errorText } from './i18n.js';
import { el, stars, avatar, formatDate, formatNumber, toast, siteData } from './ui.js';
import { onUser, openLogin } from './auth-ui.js';
import { formatSlot, slotId } from './booking.js';

export function initAdmin() {
  const root = document.querySelector('[data-app]');
  const services = siteData().services || [];
  let reviews = [];
  let users = [];
  let bookings = [];
  let tab = 'bookings';
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
      const [r, u, b] = await Promise.all([
        F.getDocs(F.collection(db, 'reviews')),
        F.getDocs(F.collection(db, 'users')),
        F.getDocs(F.collection(db, 'bookings'))
      ]);
      bookings = b.docs.map(d => ({ id: d.id, ...d.data() }));
      const byTime = (a, b) => (b.createdAt?.toMillis?.() || 0) - (a.createdAt?.toMillis?.() || 0);
      reviews = r.docs.map(d => ({ id: d.id, ...d.data() })).filter(isLive).sort(byTime);
      users = u.docs.map(d => ({ id: d.id, ...d.data() })).filter(isLive).sort(byTime);
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
    const upcoming = bookings.filter(bk => startOf(bk) > Date.now() - 3600000);
    const tabs = [['bookings', T.tabBookings, upcoming.length], ['pending', T.tabPending, count('pending')], ['approved', T.tabApproved, count('approved')], ['hidden', T.tabHidden, count('hidden')], ['all', T.tabAll, reviews.length], ['users', T.tabUsers, users.length]];
    const searchInput = el('input', { type: 'search', placeholder: T.search, 'aria-label': T.search, value: search });
    searchInput.addEventListener('input', () => { search = searchInput.value; drawList(); });
    const listBox = el('div', { class: 'admin-list', 'aria-live': 'polite' });

    root.replaceChildren(
      el('section', { class: 'account-hero' },
        el('img', { src: 'assets/brand/logo-mark.svg', width: 64, height: 64, alt: '' }),
        el('div', {}, el('p', { class: 'eyebrow' }, T.brand), el('h1', {}, T.adminTitle), el('p', {}, T.adminIntro), el('p', { class: 'small-note' }, T.retentionNote))),
      el('div', { class: 'stats' },
        stat(T.statUpcoming, upcoming.length, upcoming.some(bk => bk.status === 'requested')),
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
      if (tab === 'bookings') {
        const match = bk => !q || `${bk.name} ${bk.phone} ${bk.email} ${bk.note || ''}`.toLowerCase().includes(q);
        const soon = upcoming.filter(match).sort((a, b) => startOf(a) - startOf(b));
        const old = bookings.filter(bk => !upcoming.includes(bk)).filter(match).sort((a, b) => startOf(b) - startOf(a));
        listBox.replaceChildren(...(soon.length || old.length ? [
          soon.length && el('h3', { class: 'list-label' }, T.upcoming), ...soon.map(bookingCard),
          old.length && el('h3', { class: 'list-label' }, T.past), ...old.map(bookingCard)].filter(Boolean)
          : [el('p', { class: 'review-empty' }, T.noBookings)]));
        return;
      }
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

  function startOf(bk) {
    return Date.parse(`${bk.date}T${bk.time}:00+05:30`);
  }

  async function setBooking(bk, status) {
    try {
      const { db, F } = await getFirebase();
      await F.updateDoc(F.doc(db, 'bookings', bk.id), { status, updatedAt: F.serverTimestamp() });
      bk.status = status;
      toast(T.updated);
      render();
    } catch (err) {
      toast(errorText(err), 'error');
    }
  }

  async function cancelBooking(bk) {
    if (!confirm(T.confirmCancel)) return;
    try {
      const { db, F } = await getFirebase();
      const batch = F.writeBatch(db);
      batch.delete(F.doc(db, 'bookings', bk.id));
      batch.delete(F.doc(db, 'slots', slotId(bk.date, bk.time)));
      await batch.commit();
      bookings = bookings.filter(x => x.id !== bk.id);
      toast(T.bookingCancelled);
      render();
    } catch (err) {
      toast(errorText(err), 'error');
    }
  }

  function bookingCard(bk) {
    const service = services.find(s => s.id === bk.service);
    const digits = (bk.phone || '').replace(/[^0-9]/g, '');
    const wa = `https://wa.me/${digits.length === 10 ? '91' + digits : digits}?text=${encodeURIComponent(T.waMessage(bk.name, formatSlot(bk.date, bk.time)))}`;
    return el('article', { class: `review-card admin booking-card ${bk.status}` },
      el('header', {},
        el('div', {}, el('strong', { class: 'slot-time' }, formatSlot(bk.date, bk.time)), el('small', {}, `${bk.name} · ${bk.phone} · ${bk.email}`)),
        el('span', { class: `chip ${bk.status}` }, T.bookingStatus[bk.status] || bk.status)),
      el('p', {}, [service?.title, bk.option, T.modes[bk.mode]].filter(Boolean).join(' · ')),
      bk.note && el('p', { class: 'review-text' }, bk.note),
      el('div', { class: 'button-row' },
        el('a', { class: 'button success small', href: wa, target: '_blank', rel: 'noopener noreferrer' }, 'WhatsApp'),
        el('a', { class: 'button outline small', href: `tel:${bk.phone}` }, T.callBtn),
        el('span', { class: 'spacer' }),
        bk.status === 'requested' && el('button', { type: 'button', class: 'button primary small', onclick: () => setBooking(bk, 'confirmed') }, T.confirmBooking),
        bk.status === 'confirmed' && el('button', { type: 'button', class: 'button outline small', onclick: () => setBooking(bk, 'done') }, T.markDone),
        el('button', { type: 'button', class: 'button danger small', onclick: () => cancelBooking(bk) }, T.cancelBooking)));
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
    // Published reviews are kept; unpublished ones expire 30 days from now.
    const publish = async () => {
      const { F } = await getFirebase();
      change(r.id, { status: 'approved', expireAt: F.deleteField() }, { status: 'approved', expireAt: null });
    };
    const hide = async () => {
      const { F } = await getFirebase();
      const expireAt = F.Timestamp.fromMillis(Date.now() + RETENTION_MS);
      change(r.id, { status: 'hidden', featured: false, expireAt }, { status: 'hidden', featured: false, expireAt });
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
        el('div', { class: 'card-meta' }, stars(r.rating), r.featured && el('span', { class: 'chip featured' }, T.featured), el('span', { class: `chip ${r.status}` }, T.status[r.status] || r.status))),
      el('p', { class: 'review-text' }, r.text),
      el('div', { class: 'reply-editor' },
        el('label', {}, el('strong', {}, T.reply), replyBox),
        el('div', { class: 'templates' }, el('small', {}, `${T.templates}:`),
          T.replyTemplates.map((text, i) => el('button', { type: 'button', class: 'chip-button', title: text, onclick: () => { replyBox.value = text; replyBox.focus(); } }, `${i + 1}`)))),
      el('div', { class: 'button-row' },
        el('button', { type: 'button', class: 'button primary small', onclick: saveReply }, T.saveReply),
        r.reply?.text && el('button', { type: 'button', class: 'button outline small', onclick: removeReply }, T.removeReply),
        el('span', { class: 'spacer' }),
        r.status === 'approved' && el('button', { type: 'button', class: `button small ${r.featured ? 'gold' : 'outline'}`, 'aria-pressed': String(Boolean(r.featured)), onclick: () => change(r.id, { featured: !r.featured }) }, r.featured ? T.unfeature : T.feature),
        r.status !== 'approved' && el('button', { type: 'button', class: 'button success small', onclick: publish }, T.publish),
        r.status !== 'hidden' && el('button', { type: 'button', class: 'button outline small', onclick: hide }, T.hide),
        el('button', { type: 'button', class: 'button danger small', onclick: removeReview }, T.delete)));
  }
}
