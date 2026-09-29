/**
 * Antarodaya bookings: adds each new website booking to this Google Sheet and emails you.
 *
 * Setup (see docs/BOOKING-SHEET-SETUP.md): paste this into Extensions → Apps Script of your sheet,
 * run setup() once, then Deploy → New deployment → Web app (Execute as: Me, Who has access: Anyone).
 * Put the web app URL in site-config.json as "bookingNotifyUrl".
 *
 * The website sends only the booking ID and the customer's Firebase login token. This script reads the
 * booking back from Firestore with that token, so it only accepts bookings that really exist.
 */
const PROJECT_ID = 'antarodaya-in';
const SHEET_NAME = 'Bookings';
// Leave empty to send the alert to the Google account that owns this script.
const NOTIFY_EMAIL = '';
const HEADERS = ['Received', 'Consultation (IST)', 'Name', 'WhatsApp / phone', 'Email', 'Service', 'Option',
  'Talk via', 'Question', 'Language', 'Booking ID', 'WhatsApp chat'];
const SERVICES = {
  kundali: 'Janam Kundli & Rashi Remedies', palm: 'Palm Reading (Hast Rekha)',
  relationships: 'Love, Marriage & Kundli Milan', family: 'Children & Family Guidance',
  mantra: 'Mantra, Meditation & Sadhana'
};
const MODES = { whatsapp: 'WhatsApp call', phone: 'Phone call', video: 'Video call' };

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents);
    const id = String(body.id || '');
    if (!/^\d{4}-\d{2}-\d{2}_\d{4}$/.test(id) || !body.idToken) return reply('bad request');

    const res = UrlFetchApp.fetch(
      'https://firestore.googleapis.com/v1/projects/' + PROJECT_ID + '/databases/(default)/documents/bookings/' + id,
      { headers: { Authorization: 'Bearer ' + body.idToken }, muteHttpExceptions: true });
    if (res.getResponseCode() !== 200) return reply('not verified');
    const fields = JSON.parse(res.getContentText()).fields || {};
    const v = key => (fields[key] && (fields[key].stringValue || fields[key].timestampValue)) || '';

    const sheet = getSheet_();
    if (sheet.createTextFinder(id).matchEntireCell(true).findNext()) return reply('already recorded');

    const digits = v('phone').replace(/\D/g, '');
    const wa = 'https://wa.me/' + (digits.length === 10 ? '91' + digits : digits);
    const when = v('date') + ' ' + v('time');
    sheet.appendRow([new Date(), when, v('name'), "'" + v('phone'), v('email'), SERVICES[v('service')] || v('service'),
      v('option'), MODES[v('mode')] || v('mode'), v('note'), v('lang'), id, wa]);

    MailApp.sendEmail({
      to: NOTIFY_EMAIL || Session.getEffectiveUser().getEmail(),
      subject: 'New booking: ' + v('name') + ' · ' + when + ' IST',
      htmlBody:
        '<h2 style="margin:0 0 8px">New consultation request</h2>' +
        '<p><b>' + when + ' IST</b> · ' + (MODES[v('mode')] || v('mode')) + '</p>' +
        '<p>' + esc_(v('name')) + '<br>' + esc_(v('phone')) + '<br>' + esc_(v('email')) + '</p>' +
        '<p>' + esc_(SERVICES[v('service')] || v('service')) + (v('option') ? ' · ' + esc_(v('option')) : '') + '</p>' +
        (v('note') ? '<p><i>' + esc_(v('note')) + '</i></p>' : '') +
        '<p><a href="' + wa + '">Open WhatsApp chat</a> · <a href="https://antarodaya.in/admin.html">Open admin panel</a></p>'
    });
    return reply('ok');
  } catch (err) {
    return reply('error');
  }
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
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
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
