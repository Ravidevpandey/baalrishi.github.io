// Customer account page: profile, quick actions and the customer's own reviews with replies.
import { configured, getFirebase, isLive } from './firebase.js';
import { T, errorText } from './i18n.js';
import { el, stars, avatar, formatDate, toast, siteData } from './ui.js';
import { onUser, openLogin, logout, updateDisplayName, resendVerification, refreshUser } from './auth-ui.js';
import { openReviewForm } from './review-form.js';
import { formatSlot, slotId } from './booking.js';
import { offerPrice } from './offer.js';
import { rupees } from './offer-ui.js';

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
    const bookingsBox = el('div', { class: 'my-bookings', 'aria-live': 'polite' }, el('p', { class: 'review-empty' }, T.reviewsLoading));

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
        el('button', { class: 'button outline', type: 'button', onclick: logout }, T.logout)),
      el('div', { class: 'danger-zone' },
        el('p', { class: 'small-note' }, T.deleteAccountHelp, ' ', el('a', { href: data.privacyUrl }, T.privacyPolicy)),
        el('button', { class: 'button danger small', type: 'button', onclick: deleteAccount }, T.deleteAccount)));
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

    // Erases the customer's reviews, profile and login account (right to erasure).
    async function deleteAccount() {
      if (!confirm(T.confirmDeleteAccount)) return;
      try {
        const { auth, db, A, F } = await getFirebase();
        const snap = await F.getDocs(F.query(F.collection(db, 'reviews'), F.where('uid', '==', user.uid)));
        await Promise.all(snap.docs.map(d => F.deleteDoc(d.ref)));
        const bookings = await F.getDocs(F.query(F.collection(db, 'bookings'), F.where('uid', '==', user.uid)));
        for (const d of bookings.docs) {
          const batch = F.writeBatch(db);
          batch.delete(d.ref);
          batch.delete(F.doc(db, 'slots', d.id));
          await batch.commit();
        }
        await F.deleteDoc(F.doc(db, 'users', user.uid));
        await A.deleteUser(auth.currentUser);
        toast(T.accountDeleted);
      } catch (err) {
        if (err.code === 'auth/requires-recent-login') {
          toast(T.reloginToDelete, 'error');
          await logout();
          openLogin();
        } else {
          toast(errorText(err), 'error');
        }
      }
    }

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
      el('section', { class: 'panel', id: 'bookings' },
        el('div', { class: 'panel-head' }, el('h2', {}, T.myBookings),
          el('a', { class: 'button primary small', href: `${data.homeUrl}#booking` }, T.newBooking)),
        bookingsBox),
      el('section', { class: 'panel' },
        el('div', { class: 'panel-head' }, el('h2', {}, T.myReviews),
          el('button', { type: 'button', class: 'button primary small', onclick: async () => { if (await openReviewForm()) loadMine(user); } }, T.writeNew)),
        reviewsBox));

    loadMine(user);
    loadBookings();

    async function loadBookings() {
      try {
        const { db, F } = await getFirebase();
        const snap = await F.getDocs(F.query(F.collection(db, 'bookings'), F.where('uid', '==', user.uid)));
        const mine = snap.docs.map(d => ({ id: d.id, ...d.data() })).sort((a, b) => b.id.localeCompare(a.id));
        if (!mine.length) {
          bookingsBox.replaceChildren(el('p', { class: 'review-empty' }, T.noBookings));
          return;
        }
        const services = data.services || [];
        bookingsBox.replaceChildren(...mine.map(b => {
          const upcoming = Date.parse(`${b.date}T${b.time}:00+05:30`) > Date.now();
          const fee = data.fees?.[b.service]?.[b.option] || 0;
          const price = b.price || (b.offer ? offerPrice(fee) : fee);
          return el('article', { class: 'review-card mine booking-card' },
            el('header', {},
              el('strong', {}, formatSlot(b.date, b.time)),
              el('span', { class: `chip ${b.status}` }, T.bookingStatus[b.status] || b.status)),
            el('p', {}, [services.find(s => s.id === b.service)?.title, b.option, T.modes[b.mode]].filter(Boolean).join(' · ')),
            price > 0 && el('p', { class: 'book-fee' }, T.feeLabel, ': ', el('strong', {}, rupees(price)), b.offer && [' ', el('span', { class: 'chip offer' }, T.offerTitle)]),
            upcoming && b.status !== 'done' && el('div', { class: 'button-row' },
              el('button', { type: 'button', class: 'button danger small', onclick: () => cancel(b) }, T.cancelBooking)));
        }));
      } catch (err) {
        bookingsBox.replaceChildren(el('p', { class: 'review-empty' }, errorText(err)));
      }
    }

    async function cancel(b) {
      if (!confirm(T.confirmCancel)) return;
      try {
        const { db, F } = await getFirebase();
        const batch = F.writeBatch(db);
        batch.delete(F.doc(db, 'bookings', b.id));
        batch.delete(F.doc(db, 'slots', slotId(b.date, b.time)));
        await batch.commit();
        toast(T.bookingCancelled);
        loadBookings();
      } catch (err) {
        toast(errorText(err), 'error');
      }
    }

    async function loadMine(u) {
      try {
        const { db, F } = await getFirebase();
        const snap = await F.getDocs(F.query(F.collection(db, 'reviews'), F.where('uid', '==', u.uid)));
        const mine = snap.docs.map(d => ({ id: d.id, ...d.data() })).filter(isLive)
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
          el('p', { class: 'small-note' }, T.statusHelp[r.status] || '', r.status !== 'approved' && r.expireAt ? ` ${T.expiresOn(formatDate(r.expireAt))}` : ''),
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
