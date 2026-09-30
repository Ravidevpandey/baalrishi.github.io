/**
 * Antarodaya bookings: adds each new website booking to this Google Sheet and emails you, and emails
 * the customer once you confirm the booking in the admin panel.
 *
 * Setup (see docs/BOOKING-SHEET-SETUP.md): paste this into Extensions → Apps Script of your sheet,
 * run setup() once, then Deploy → New deployment → Web app (Execute as: Me, Who has access: Anyone).
 * Put the web app URL in site-config.json as "bookingNotifyUrl".
 *
 * The website sends only the booking ID and a Firebase login token. This script reads the booking back
 * from Firestore with that token, so it only acts on bookings that really exist, and it emails the
 * customer only when the booking's status really is "confirmed" (which only the admin can set), once.
 */
const PROJECT_ID = 'antarodaya-in';
const SHEET_NAME = 'Bookings';
// Leave empty to send the alert to the Google account that owns this script.
const NOTIFY_EMAIL = '';
const SITE = 'https://antarodaya.in/';
const HEADERS = ['Received', 'Consultation (IST)', 'Name', 'WhatsApp / phone', 'Email', 'Service', 'Option',
  'Talk via', 'Question', 'Language', 'Booking ID', 'WhatsApp chat', 'Offer', 'Fee', 'Confirmation emailed'];
const SERVICES = {
  kundali: ['Janam Kundli & Rashi Remedies', 'जन्म कुंडली एवं राशि उपाय'],
  palm: ['Palm Reading (Hast Rekha)', 'हस्तरेखा परामर्श'],
  relationships: ['Love, Marriage & Kundli Milan', 'प्रेम, विवाह एवं कुंडली मिलान'],
  family: ['Children & Family Guidance', 'संतान एवं परिवार मार्गदर्शन'],
  mantra: ['Mantra, Meditation & Sadhana', 'मंत्र, ध्यान एवं साधना']
};
const MODES = { whatsapp: ['WhatsApp call', 'WhatsApp कॉल'], phone: ['Phone call', 'फ़ोन कॉल'], video: ['Video call', 'वीडियो कॉल'] };

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents);
    const id = String(body.id || '');
    if (!/^\d{4}-\d{2}-\d{2}_\d{4}$/.test(id) || !body.idToken) return reply('bad request');
    const v = readBooking_(id, body.idToken);
    if (!v) return reply('not verified');
    const sheet = getSheet_();
    if (body.action === 'confirmed') return reply(emailConfirmation_(sheet, id, v));

    if (findRow_(sheet, id)) return reply('already recorded');
    const row = addRow_(sheet, id, v);
    const when = v('date') + ' ' + v('time');
    MailApp.sendEmail({
      to: NOTIFY_EMAIL || Session.getEffectiveUser().getEmail(),
      subject: 'New booking: ' + v('name') + ' · ' + when + ' IST' + (v('offer') ? ' · offer' : ''),
      htmlBody:
        '<h2 style="margin:0 0 8px">New consultation request</h2>' +
        '<p><b>' + when + ' IST</b> · ' + label_(MODES, v('mode'), 0) + '</p>' +
        '<p>' + esc_(v('name')) + '<br>' + esc_(v('phone')) + '<br>' + esc_(v('email')) + '</p>' +
        '<p>' + esc_(label_(SERVICES, v('service'), 0)) + (v('option') ? ' · ' + esc_(v('option')) : '') + '</p>' +
        (v('offer') ? '<p><b>Month-end offer booking</b> (' + esc_(v('offer')) + ')</p>' : '') +
        (v('note') ? '<p><i>' + esc_(v('note')) + '</i></p>' : '') +
        '<p><a href="' + sheet.getRange(row, HEADERS.indexOf('WhatsApp chat') + 1).getValue() + '">Open WhatsApp chat</a> · <a href="' + SITE + 'admin.html">Open admin panel</a></p>'
    });
    return reply('ok');
  } catch (err) {
    return reply('error');
  }
}

// Reads bookings/{id} from Firestore as the signed-in caller; returns a field reader, or null.
function readBooking_(id, idToken) {
  const res = UrlFetchApp.fetch(
    'https://firestore.googleapis.com/v1/projects/' + PROJECT_ID + '/databases/(default)/documents/bookings/' + id,
    { headers: { Authorization: 'Bearer ' + idToken }, muteHttpExceptions: true });
  if (res.getResponseCode() !== 200) return null;
  const fields = JSON.parse(res.getContentText()).fields || {};
  return key => {
    const f = fields[key];
    return f ? (f.stringValue || f.integerValue || f.timestampValue || '') : '';
  };
}

// Emails the customer that the booking is confirmed, once per booking.
function emailConfirmation_(sheet, id, v) {
  if (v('status') !== 'confirmed') return 'not confirmed';
  const row = findRow_(sheet, id) || addRow_(sheet, id, v);
  const sent = sheet.getRange(row, HEADERS.indexOf('Confirmation emailed') + 1);
  if (sent.getValue()) return 'already emailed';

  const hi = v('lang') === 'hi' ? 1 : 0;
  const service = label_(SERVICES, v('service'), hi) + (v('option') ? ' · ' + v('option') : '');
  const fee = v('price') ? '₹' + String(v('price')).replace(/\B(?=(\d{3})+(?!\d))/g, ',') : '';
  const when = Utilities.formatDate(new Date(v('date') + 'T' + v('time') + ':00+05:30'), 'Asia/Kolkata',
    hi ? 'dd-MM-yyyy, h:mm a' : 'EEE d MMM yyyy, h:mm a');
  const t = hi
    ? { subject: 'आपकी बुकिंग पक्की हो गई · ' + when, hello: 'नमस्ते ' + v('name') + ' जी,', text: 'अंतरोदय के साथ आपका परामर्श पक्का हो गया है।',
        when: 'समय (भारतीय)', service: 'सेवा', mode: 'माध्यम', fee: 'शुल्क', offer: ' (महीने के अंत का ऑफ़र)',
        pay: 'भुगतान की जानकारी हम WhatsApp पर भेजेंगे। भुगतान के विवरण:', account: 'मेरी बुकिंग देखें', sign: 'धन्यवाद,<br>अंतरोदय' }
    : { subject: 'Your booking is confirmed · ' + when, hello: 'Namaste ' + v('name') + ',', text: 'Your consultation with Antarodaya is confirmed.',
        when: 'When (India time)', service: 'Service', mode: 'How', fee: 'Fee', offer: ' (month-end offer)',
        pay: 'We will share payment details on WhatsApp. Payment information:', account: 'See my bookings', sign: 'Thank you,<br>Antarodaya' };
  const row_ = (k, val) => '<tr><td style="padding:4px 12px 4px 0;color:#626960">' + k + '</td><td style="padding:4px 0"><b>' + esc_(val) + '</b></td></tr>';
  MailApp.sendEmail({
    to: v('email'),
    name: 'Antarodaya',
    replyTo: NOTIFY_EMAIL || Session.getEffectiveUser().getEmail(),
    subject: t.subject,
    htmlBody:
      '<div style="font-family:Arial,sans-serif;color:#203e35;max-width:520px">' +
      '<p>' + esc_(t.hello) + '</p><p>' + t.text + '</p><table>' +
      row_(t.when, when) + row_(t.service, service) + row_(t.mode, label_(MODES, v('mode'), hi)) +
      (fee ? row_(t.fee, fee + (v('offer') ? t.offer : '')) : '') + '</table>' +
      '<p>' + t.pay + ' <a href="' + SITE + (hi ? 'hi.html' : '') + '#payment">antarodaya.in</a></p>' +
      '<p><a href="' + SITE + (hi ? 'account-hi.html' : 'account.html') + '#bookings">' + t.account + '</a></p>' +
      '<p>' + t.sign + '</p></div>'
  });
  sent.setValue(new Date());
  if (fee) sheet.getRange(row, HEADERS.indexOf('Fee') + 1).setValue(fee);
  return 'emailed';
}

function findRow_(sheet, id) {
  const cell = sheet.getRange(1, HEADERS.indexOf('Booking ID') + 1, sheet.getLastRow(), 1)
    .createTextFinder(id).matchEntireCell(true).findNext();
  return cell ? cell.getRow() : 0;
}

function addRow_(sheet, id, v) {
  const digits = v('phone').replace(/\D/g, '');
  const wa = 'https://wa.me/' + (digits.length === 10 ? '91' + digits : digits);
  sheet.appendRow([new Date(), v('date') + ' ' + v('time'), v('name'), "'" + v('phone'), v('email'),
    label_(SERVICES, v('service'), 0), v('option'), label_(MODES, v('mode'), 0), v('note'), v('lang'), id, wa,
    v('offer') ? 'Yes (' + v('offer') + ')' : '', '', '']);
  return sheet.getLastRow();
}

function label_(map, key, hi) {
  return map[key] ? map[key][hi] : key;
}

/** Run once from the editor: creates the header row and sends a test email. */
function setup() {
  const sheet = getSheet_();
  MailApp.sendEmail(NOTIFY_EMAIL || Session.getEffectiveUser().getEmail(),
    'Antarodaya booking alerts are on',
    'New website bookings will be added to "' + SpreadsheetApp.getActive().getName() + '" and emailed to you.');
  return sheet.getName();
}

function getSheet_() {
  const book = SpreadsheetApp.getActive();
  let sheet = book.getSheetByName(SHEET_NAME);
  if (!sheet) sheet = book.insertSheet(SHEET_NAME);
  if (sheet.getLastRow() === 0 || sheet.getLastColumn() < HEADERS.length) {
    sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
    sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold').setBackground('#183d35').setFontColor('#ffffff');
    sheet.setFrozenRows(1);
    sheet.setColumnWidths(1, HEADERS.length, 160);
  }
  return sheet;
}

function esc_(s) {
  return String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

function reply(text) {
  return ContentService.createTextOutput(text);
}
