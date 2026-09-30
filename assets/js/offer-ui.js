// Shows the month-end offer on the home page: a banner with seats left, and struck-through fees.
import { configured, getFirebase } from './firebase.js';
import { OFFER_SEATS, offerWindow, offerPrice, claimId } from './offer.js';
import { lang, T } from './i18n.js';
import { el } from './ui.js';

export const rupees = n => `₹${n.toLocaleString('en-IN')}`;

// { month, start, end, active, left, used }: `left` seats this month, `used` if this customer already had it.
export async function loadOffer(user) {
  const win = offerWindow();
  const closed = { ...win, active: false, left: 0, used: false };
  if (!win.active || !configured) return closed;
  try {
    const { db, F } = await getFirebase();
    const counter = await F.getDoc(F.doc(db, 'offers', win.month));
    const left = Math.max(0, OFFER_SEATS - (counter.data()?.claimed || 0));
    const used = user ? (await F.getDoc(F.doc(db, 'offerClaims', claimId(win.month, user.uid)))).exists() : false;
    return { ...win, left, used };
  } catch {
    return closed;
  }
}

export const offerOpen = offer => offer.active && offer.left > 0;
export const offerApplies = (offer, fee) => offerOpen(offer) && !offer.used && offerPrice(fee) < fee;

// Last day of the offer, e.g. "30 Sept".
export const offerLastDay = offer => new Intl.DateTimeFormat(lang === 'hi' ? 'hi-IN' : 'en-IN',
  { timeZone: 'Asia/Kolkata', day: 'numeric', month: 'short' }).format(new Date(offer.end - 1));

// Price shown with the regular fee struck through, or just the fee.
export function priceTag(fee, withOffer) {
  const price = offerPrice(fee);
  if (!withOffer || price >= fee) return [rupees(fee)];
  return [el('s', { class: 'regular-fee' }, rupees(fee)), ' ', el('span', { class: 'offer-fee' }, rupees(price))];
}

// Rewrites every [data-fee] price on the page and shows or removes the offer banner.
export function showOffer(offer) {
  const open = offerOpen(offer);
  document.querySelectorAll('[data-fee]').forEach(node => node.replaceChildren(...priceTag(Number(node.dataset.fee), open)));
  document.querySelectorAll('.offer-banner').forEach(node => node.remove());
  if (!open) return;
  const banner = () => el('p', { class: 'offer-banner', role: 'status' },
    el('span', { 'aria-hidden': 'true' }, '✦'),
    el('strong', {}, T.offerTitle),
    el('span', {}, `${T.offerSeats(offer.left, OFFER_SEATS)} · ${T.offerUntil(offerLastDay(offer))}`),
    offer.used && el('small', {}, T.offerUsed));
  document.querySelector('#services .section-heading')?.append(banner());
  document.querySelector('#booking .section-heading')?.append(banner());
}
