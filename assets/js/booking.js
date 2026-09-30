// Consultation booking: pick a service, a weekend date and a 30-minute slot (IST), then send a request.
import { configured, getFirebase } from './firebase.js';
import { lang, T, errorText } from './i18n.js';
import { el, toast, siteData } from './ui.js';
import { requireUser, onUser } from './auth-ui.js';
import { offerExpiry, offerPrice, claimId } from './offer.js';
import { loadOffer, showOffer, offerApplies, rupees } from './offer-ui.js';

// Consultation hours (IST), Saturday and Sunday. Must match slotTimes() in firestore.rules.
export const SESSIONS = [
  ['morning', ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30']],
  ['afternoon', ['14:00', '14:30', '15:00', '15:30', '16:00', '16:30']],
  ['night', ['20:00', '20:30', '21:00', '21:30', '22:00', '22:30']]
];
const DAYS_AHEAD = 60;
const LEAD_MS = 60 * 60 * 1000; // a slot must start at least an hour from now
const RETENTION_MS = 30 * 24 * 60 * 60 * 1000;
const locale = lang === 'hi' ? 'hi-IN' : 'en-IN';

export const slotId = (date, time) => `${date}_${time.replace(':', '')}`;
const slotStart = (date, time) => Date.parse(`${date}T${time}:00+05:30`);

// Saturdays and Sundays in IST for the next DAYS_AHEAD days, as YYYY-MM-DD.
function weekendDates() {
  const dates = [];
  const istNow = new Date(Date.now() + 5.5 * 3600 * 1000);
  for (let i = 0; i <= DAYS_AHEAD; i++) {
    const d = new Date(Date.UTC(istNow.getUTCFullYear(), istNow.getUTCMonth(), istNow.getUTCDate() + i));
    if (d.getUTCDay() === 0 || d.getUTCDay() === 6) dates.push(d.toISOString().slice(0, 10));
  }
  return dates.filter(date => SESSIONS.some(([, times]) => times.some(t => slotStart(date, t) > Date.now() + LEAD_MS)));
}

export function formatSlot(date, time, withWeekday = true) {
  const at = new Date(slotStart(date, time || '00:00'));
  const day = new Intl.DateTimeFormat(locale, { timeZone: 'Asia/Kolkata', weekday: withWeekday ? 'short' : undefined, day: 'numeric', month: 'short' }).format(at);
  if (!time) return day;
  const clock = new Intl.DateTimeFormat(locale, { timeZone: 'Asia/Kolkata', hour: 'numeric', minute: '2-digit' }).format(at);
  return `${day}, ${clock}`;
}
const formatTime = (date, time) => new Intl.DateTimeFormat(locale, { timeZone: 'Asia/Kolkata', hour: 'numeric', minute: '2-digit' }).format(new Date(slotStart(date, time)));

export function initBooking() {
  const root = document.querySelector('[data-booking]');
  if (!root) return;
  const data = siteData();
  const services = data.services || [];
  const state = { service: '', option: '', date: '', time: '', taken: new Set(), loadingTimes: false, done: null, offer: { active: false } };
  const dates = weekendDates();

  if (!configured) {
    root.replaceChildren(el('p', { class: 'review-empty' }, T.comingSoon));
    return;
  }

  async function refreshOffer(user) {
    state.offer = { ...(await loadOffer(user)), checkedFor: user?.uid };
    showOffer(state.offer);
    render();
  }
  onUser(user => refreshOffer(user));

  const feeOf = () => services.find(s => s.id === state.service)?.options.find(o => o.name === state.option)?.fee;

  async function loadTaken(date) {
    state.loadingTimes = true;
    render();
    try {
      const { db, F } = await getFirebase();
      const snap = await F.getDocs(F.query(F.collection(db, 'slots'), F.where('date', '==', date)));
      state.taken = new Set(snap.docs.map(d => d.data().time));
    } catch {
      state.taken = new Set();
    }
    state.loadingTimes = false;
    if (state.taken.has(state.time)) state.time = '';
    render();
  }

  const chip = (label, selected, onclick, extra = {}) =>
    el('button', { type: 'button', class: `slot-chip${selected ? ' selected' : ''}`, 'aria-pressed': String(selected), onclick, ...extra }, label);

  function render() {
    if (state.done) return renderDone();
    const service = services.find(s => s.id === state.service);
    const serviceSelect = el('select', { id: 'book-service', required: true },
      el('option', { value: '' }, T.chooseService),
      services.map(s => el('option', { value: s.id, selected: s.id === state.service }, s.title)));
    serviceSelect.addEventListener('change', () => { state.service = serviceSelect.value; state.option = ''; render(); });
    const optionSelect = el('select', { id: 'book-option', disabled: !service },
      el('option', { value: '' }, T.chooseOption),
      (service?.options || []).map(o => el('option', { value: o.name, selected: o.name === state.option },
        offerApplies(state.offer, o.fee) ? `${o.name} · ${rupees(offerPrice(o.fee))} (${T.insteadOf(rupees(o.fee))})` : `${o.name} · ${rupees(o.fee)}`)));
    optionSelect.addEventListener('change', () => { state.option = optionSelect.value; render(); });
    const fee = feeOf();

    const dateRow = el('div', { class: 'chip-row scroll', role: 'group', 'aria-label': T.stepDate },
      dates.map(d => chip(formatSlot(d), d === state.date, () => { state.date = d; state.time = ''; loadTaken(d); })));

    let timeBlock;
    if (!state.date) timeBlock = el('p', { class: 'small-note' }, T.pickDateFirst);
    else if (state.loadingTimes) timeBlock = el('p', { class: 'small-note' }, T.loadingTimes);
    else {
      const groups = SESSIONS.map(([key, times]) => {
        const free = times.filter(t => slotStart(state.date, t) > Date.now() + LEAD_MS && !state.taken.has(t));
        return free.length && el('div', { class: 'time-group' },
          el('span', { class: 'time-label' }, T.sessions[key]),
          el('div', { class: 'chip-row' }, free.map(t => chip(formatTime(state.date, t), t === state.time, () => { state.time = t; render(); }))));
      }).filter(Boolean);
      timeBlock = groups.length ? el('div', { class: 'time-groups' }, groups) : el('p', { class: 'small-note' }, T.noTimes);
    }

    const form = el('form', { class: 'booking-form', novalidate: true },
      el('div', { class: 'book-step' }, el('h3', {}, el('span', { class: 'step-no' }, '1'), T.stepService),
        el('div', { class: 'field-pair' },
          el('label', { class: 'field' }, el('span', {}, T.service), serviceSelect),
          el('label', { class: 'field' }, el('span', {}, T.optionLabel), optionSelect))),
      el('div', { class: 'book-step' }, el('h3', {}, el('span', { class: 'step-no' }, '2'), T.stepDate), dateRow),
      el('div', { class: 'book-step' }, el('h3', {}, el('span', { class: 'step-no' }, '3'), T.stepTime), timeBlock),
      el('div', { class: 'book-step' }, el('h3', {}, el('span', { class: 'step-no' }, '4'), T.stepDetails),
        el('div', { class: 'field-pair' },
          el('label', { class: 'field' }, el('span', {}, T.name), el('input', { id: 'book-name', name: 'name', maxlength: 60, autocomplete: 'name', required: true })),
          el('label', { class: 'field' }, el('span', {}, T.phoneLabel), el('input', { id: 'book-phone', name: 'phone', type: 'tel', inputmode: 'tel', maxlength: 20, autocomplete: 'tel', placeholder: '+91 98765 43210', required: true }), el('small', {}, T.phoneHint))),
        el('fieldset', { class: 'field' }, el('legend', {}, T.modeLabel),
          el('div', { class: 'chip-row' }, Object.entries(T.modes).map(([value, label], i) =>
            el('label', { class: 'mode-option' }, el('input', { type: 'radio', name: 'mode', value, checked: i === 0 }), el('span', {}, label))))),
        el('label', { class: 'field' }, el('span', {}, T.noteLabel), el('textarea', { id: 'book-note', name: 'note', rows: 3, maxlength: 500, placeholder: T.notePlaceholder }))),
      el('div', { class: 'book-summary' },
        el('p', {}, state.date && state.time ? T.youChose(formatSlot(state.date, state.time)) : T.pickAll),
        fee && el('p', { class: 'book-fee' }, T.feeLabel, ': ', offerApplies(state.offer, fee)
          ? [el('s', { class: 'regular-fee' }, rupees(fee)), ' ', el('strong', { class: 'offer-fee' }, rupees(offerPrice(fee))), ' ', el('span', { class: 'chip offer' }, T.offerTitle)]
          : el('strong', {}, rupees(fee))),
        el('p', { class: 'small-note' }, T.payNote)),
      el('p', { class: 'form-error', role: 'alert', hidden: true }),
      el('button', { class: 'button primary', type: 'submit' }, T.requestBooking));

    // Keep what the visitor typed when the form re-renders.
    const previous = root.querySelector('form.booking-form');
    if (previous) {
      for (const name of ['name', 'phone', 'note']) form[name].value = previous[name].value;
      const mode = previous.querySelector('input[name=mode]:checked')?.value;
      if (mode) form.querySelector(`input[name=mode][value=${mode}]`).checked = true;
    } else {
      onUser(user => { if (user && !form.name.value) form.name.value = user.displayName || ''; });
    }
    form.addEventListener('submit', event => submit(event, form));
    root.replaceChildren(form);
  }

  async function submit(event, form) {
    event.preventDefault();
    const error = form.querySelector('.form-error');
    const fail = message => { error.textContent = message; error.hidden = false; };
    const name = form.name.value.trim();
    const phone = form.phone.value.trim();
    if (!state.service || !state.date || !state.time) return fail(T.pickAll);
    if (!name) return fail(T.enterName);
    if (!/^[+]?[0-9 ()-]{8,20}$/.test(phone)) return fail(T.badPhone);
    error.hidden = true;

    const user = await requireUser();
    if (!user) return;
    if (!user.emailVerified) return fail(T.verifyToBook);
    const button = form.querySelector('[type=submit]');
    button.disabled = true;
    button.textContent = T.submitting;
    const id = slotId(state.date, state.time);
    // The offer is checked again after login: this customer may already have used it this month.
    if (state.offer.active && state.offer.checkedFor !== user.uid) state.offer = { ...(await loadOffer(user)), checkedFor: user.uid };
    const withOffer = offerApplies(state.offer, feeOf());
    try {
      const { db, F } = await getFirebase();
      const expireAt = F.Timestamp.fromMillis(slotStart(state.date, state.time) + RETENTION_MS);
      const batch = F.writeBatch(db);
      batch.set(F.doc(db, 'bookings', id), {
        uid: user.uid, name, phone, email: user.email, service: state.service, option: state.option,
        mode: form.querySelector('input[name=mode]:checked').value, note: form.note.value.trim(),
        date: state.date, time: state.time, lang, status: 'requested', createdAt: F.serverTimestamp(), expireAt,
        ...(withOffer && { offer: state.offer.month })
      });
      batch.set(F.doc(db, 'slots', id), { date: state.date, time: state.time, expireAt });
      if (withOffer) {
        const offerExpireAt = F.Timestamp.fromMillis(offerExpiry(state.offer));
        batch.set(F.doc(db, 'offerClaims', claimId(state.offer.month, user.uid)), { uid: user.uid, booking: id, expireAt: offerExpireAt });
        batch.set(F.doc(db, 'offers', state.offer.month), { claimed: F.increment(1), expireAt: offerExpireAt }, { merge: true });
      }
      await batch.commit();
      notifyOwner(user, id);
      state.done = { date: state.date, time: state.time, fee: feeOf(), withOffer };
      if (withOffer) refreshOffer(user);
      render();
      toast(T.bookedTitle);
    } catch (err) {
      if (err.code === 'permission-denied') {
        await loadTaken(state.date);
        if (state.taken.has(state.time)) toast(T.slotTaken, 'error');
        else if (withOffer) {
          // The last seat went to someone else, or the offer just ended: show regular fees and let them resubmit.
          state.offer = { ...(await loadOffer(user)), checkedFor: user.uid };
          showOffer(state.offer);
          toast(T.offerGone, 'error');
          render();
          return;
        } else toast(errorText(err), 'error');
      } else {
        fail(errorText(err));
      }
      button.disabled = false;
      button.textContent = T.requestBooking;
    }
  }

  // Tells the owner's Google Sheet script about the booking; it re-reads the booking from Firestore
  // with the customer's ID token, so it cannot be fed fake bookings.
  async function notifyOwner(user, id) {
    if (!data.bookingNotifyUrl) return;
    try {
      const idToken = await user.getIdToken();
      await fetch(data.bookingNotifyUrl, { method: 'POST', mode: 'no-cors', headers: { 'Content-Type': 'text/plain' }, body: JSON.stringify({ id, idToken }) });
    } catch {}
  }

  function renderDone() {
    const { date, time, fee, withOffer } = state.done;
    root.replaceChildren(el('div', { class: 'booking-done' },
      el('span', { class: 'done-mark', 'aria-hidden': 'true' }, '✓'),
      el('h3', {}, T.bookedTitle),
      el('p', {}, T.bookedText(formatSlot(date, time))),
      fee && el('p', { class: 'book-fee' }, T.feeLabel, ': ', el('strong', {}, rupees(withOffer ? offerPrice(fee) : fee)), withOffer && [' ', el('span', { class: 'chip offer' }, T.offerTitle)]),
      el('p', { class: 'small-note' }, T.payNote),
      el('div', { class: 'button-row' },
        el('a', { class: 'button primary', href: data.accountUrl }, T.viewBookings),
        el('button', { type: 'button', class: 'button outline', onclick: () => { state.done = null; state.time = ''; loadTaken(state.date); } }, T.bookAnother))));
  }

  render();
}

