// Customer account page: profile, quick actions and the customer's own reviews with replies.
import { configured, getFirebase } from './firebase.js';
import { T, errorText } from './i18n.js';
import { el, stars, avatar, formatDate, toast, siteData } from './ui.js';
import { onUser, openLogin, logout, updateDisplayName, resendVerification, refreshUser } from './auth-ui.js';
import { openReviewForm } from './review-form.js';

export function initAccount() {
  const root = document.querySelector('[data-app]');
  const data = siteData();
  onUser(user => (user ? renderAccount(user) : renderGate()));

  function renderGate() {
    root.replaceChildren(el('section', { class: 'gate panel' },
      el('img', { src: 'assets/brand/logo-mark.svg', width: 72, height: 72, alt: '' }),
      el('h1', {}, T.accountGateTitle),
      el('p', {}, configured ? T.accountGateText : T.comingSoon),
      el('button', { type: 'button', class: 'button primary', onclick: () => openLogin() }, T.login)));
  }

  async function renderAccount(user) {
    const name = user.displayName || user.email.split('@')[0];
    const method = user.providerData[0]?.providerId === 'google.com' ? 'Google' : T.email;
    const since = formatDate(user.metadata.creationTime ? new Date(user.metadata.creationTime) : null);
    const reviewsBox = el('div', { class: 'my-reviews', 'aria-live': 'polite' }, el('p', { class: 'review-empty' }, T.reviewsLoading));

    const nameInput = el('input', { name: 'name', maxlength: 60, required: true, autocomplete: 'name' });
    nameInput.value = user.displayName || '';
    const profileForm = el('form', { class: 'profile-form' },
      el('label', { class: 'field' }, el('span', {}, T.name), nameInput),
      el('dl', { class: 'facts' },
        el('dt', {}, T.email), el('dd', {}, user.email),
        el('dt', {}, T.loginMethod), el('dd', {}, method),
        el('dt', {}, T.verification), el('dd', {}, el('span', { class: `chip ${user.emailVerified ? 'approved' : 'pending'}` }, user.emailVerified ? T.emailVerified : T.emailNotVerified))),
      el('div', { class: 'button-row' },
        el('button', { class: 'button primary', type: 'submit' }, T.save),
        el('button', { class: 'button outline', type: 'button', onclick: logout }, T.logout)));
    profileForm.addEventListener('submit', async event => {
      event.preventDefault();
      const value = nameInput.value.trim();
      if (!value) return;
      try {
        await updateDisplayName(value);
        toast(T.profileSaved);
      } catch (err) {
        toast(errorText(err), 'error');
      }
    });

    const verifyBanner = !user.emailVerified && el('div', { class: 'banner' },
      el('p', {}, T.verifyNeeded),
      el('div', { class: 'button-row' },
        el('button', { type: 'button', class: 'button outline small', onclick: () => resendVerification().catch(err => toast(errorText(err), 'error')) }, T.resendVerify),
        el('button', { type: 'button', class: 'button primary small', onclick: () => refreshUser() }, T.iVerified)));

    const action = (href, label, external) => el('a', { class: 'action-link', href, target: external ? '_blank' : null, rel: external ? 'noopener noreferrer' : null }, el('span', {}, label), el('span', { 'aria-hidden': 'true' }, '↗'));

    root.replaceChildren(
      el('section', { class: 'account-hero' },
        avatar(name, user.photoURL, 'lg'),
        el('div', {}, el('p', { class: 'eyebrow' }, T.myAccount), el('h1', {}, T.hello(name)), since && el('p', {}, T.memberSince(since)))),
      verifyBanner || '',
      el('div', { class: 'account-grid' },
        el('section', { class: 'panel' }, el('h2', {}, T.profile), profileForm),
        el('section', { class: 'panel' }, el('h2', {}, T.quickActions),
          el('nav', { class: 'action-list' },
            data.formUrl && action(data.formUrl, T.bookConsult, true),
            data.instagramUrl && action(data.instagramUrl, T.messageInsta, true),
            action(`${data.homeUrl}#services`, T.viewServices),
            action(`${data.homeUrl}#payment`, T.paymentInfo)))),
      el('section', { class: 'panel' },
        el('div', { class: 'panel-head' }, el('h2', {}, T.myReviews),
          el('button', { type: 'button', class: 'button primary small', onclick: async () => { if (await openReviewForm()) loadMine(user); } }, T.writeNew)),
        reviewsBox));

    loadMine(user);

    async function loadMine(u) {
      try {
        const { db, F } = await getFirebase();
        const snap = await F.getDocs(F.query(F.collection(db, 'reviews'), F.where('uid', '==', u.uid)));
        const mine = snap.docs.map(d => ({ id: d.id, ...d.data() }))
          .sort((a, b) => (b.createdAt?.toMillis?.() || 0) - (a.createdAt?.toMillis?.() || 0));
        if (!mine.length) {
          reviewsBox.replaceChildren(el('p', { class: 'review-empty' }, T.noMyReviews));
          return;
        }
        const services = data.services || [];
        reviewsBox.replaceChildren(...mine.map(r => el('article', { class: 'review-card mine' },
          el('header', {},
            stars(r.rating),
            el('span', { class: `chip ${r.status}`, title: T.statusHelp[r.status] }, T.status[r.status] || r.status),
            el('small', {}, [formatDate(r.createdAt), services.find(s => s.id === r.service)?.title].filter(Boolean).join(' · '))),
          el('p', { class: 'review-text' }, r.text),
          el('p', { class: 'small-note' }, T.statusHelp[r.status] || ''),
          r.reply?.text && el('div', { class: 'review-reply' }, el('strong', {}, T.replyFrom), el('p', {}, r.reply.text)),
          el('div', { class: 'button-row' },
            el('button', { type: 'button', class: 'button outline small', onclick: async () => { if (await openReviewForm(r)) loadMine(u); } }, T.edit),
            el('button', {
              type: 'button', class: 'button danger small', onclick: async () => {
                if (!confirm(T.confirmDelete)) return;
                try {
                  await F.deleteDoc(F.doc(db, 'reviews', r.id));
                  toast(T.deleted);
                  loadMine(u);
                } catch (err) {
                  toast(errorText(err), 'error');
                }
              }
            }, T.delete)))));
      } catch (err) {
        reviewsBox.replaceChildren(el('p', { class: 'review-empty' }, errorText(err)));
      }
    }
  }
}
