// Month-end offer: in the last OFFER_DAYS days of every month (IST) the first OFFER_SEATS bookings get
// each fee one step down the ladder below. Pure functions only, so they also run under Node for tests.
// The window, seat limit and one-offer-per-customer rule are enforced in firestore.rules (keep in sync).
export const OFFER_SEATS = 11;
export const OFFER_DAYS = 7;
const IST_MS = 5.5 * 3600 * 1000;
const DAY_MS = 24 * 3600 * 1000;

// Regular fee → offer fee. Fees not listed here get no discount.
export const OFFER_PRICES = { 101: 51, 151: 101, 251: 151, 551: 251, 1100: 551, 2100: 1100, 5100: 2100 };
export const offerPrice = fee => OFFER_PRICES[fee] ?? fee;

// The offer window of the IST month containing `now`: month key "YYYY-MM", start and end (epoch ms)
// and whether `now` is inside it. The window is the IST days d for which d + OFFER_DAYS is next month.
export function offerWindow(now = Date.now()) {
  const ist = new Date(now + IST_MS);
  const y = ist.getUTCFullYear();
  const m = ist.getUTCMonth();
  const end = Date.UTC(y, m + 1, 1) - IST_MS;
  const start = end - OFFER_DAYS * DAY_MS;
  return { month: `${y}-${String(m + 1).padStart(2, '0')}`, start, end, active: now >= start && now < end };
}

// Offer claims and counters are kept a little past the month, then removed by the daily cleanup.
export const offerExpiry = win => win.end + 40 * DAY_MS;
export const claimId = (month, uid) => `${month}_${uid}`;
