// Unit tests for the month-end offer dates and prices. Run: node --test tests/offer.test.mjs (Node 22+)
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { offerWindow, offerPrice, OFFER_PRICES } from '../assets/js/offer.js';

const ist = s => Date.parse(`${s}+05:30`);

test('offer runs the last 7 days of the month, IST', () => {
  assert.equal(offerWindow(ist('2026-09-23T23:59:59')).active, false);
  assert.equal(offerWindow(ist('2026-09-24T00:00:00')).active, true);
  assert.equal(offerWindow(ist('2026-09-30T23:59:59')).active, true);
  assert.equal(offerWindow(ist('2026-10-01T00:00:00')).active, false);
  assert.equal(offerWindow(ist('2026-10-25T00:00:00')).active, true);
  assert.equal(offerWindow(ist('2026-10-24T23:59:00')).active, false);
});

test('February and leap years', () => {
  assert.equal(offerWindow(ist('2027-02-22T10:00:00')).active, true);
  assert.equal(offerWindow(ist('2027-02-21T10:00:00')).active, false);
  assert.equal(offerWindow(ist('2028-02-23T10:00:00')).active, true);
  assert.equal(offerWindow(ist('2028-02-22T10:00:00')).active, false);
});

test('month key follows IST, not UTC', () => {
  // 1 Oct 02:00 IST is still 30 Sep in UTC.
  assert.equal(offerWindow(ist('2026-10-01T02:00:00')).month, '2026-10');
  assert.equal(offerWindow(ist('2026-12-31T23:00:00')).month, '2026-12');
  assert.equal(offerWindow(ist('2026-12-31T23:00:00')).end, ist('2027-01-01T00:00:00'));
});

test('offer prices step down to auspicious amounts', () => {
  assert.deepEqual([101, 151, 251, 551, 1100, 2100, 5100].map(offerPrice), [51, 101, 151, 251, 551, 1100, 2100]);
  assert.equal(offerPrice(999), 999);
  for (const [fee, price] of Object.entries(OFFER_PRICES)) assert.ok(price < Number(fee));
});
