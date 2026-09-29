# Antarodaya (अंतरोदय) website

Responsive static website for GitHub Pages, served at https://antarodaya.in (see `CNAME`).

| Page | Hindi | English |
|---|---|---|
| Home | `hi.html` | `index.html` (default) |
| Customer account | `account-hi.html` | `account.html` |
| Admin panel | `admin-hi.html` | `admin.html` |
| Privacy policy | `privacy-hi.html` | `privacy.html` |

English opens first; the हिं / EN switch in the header changes language. `en.html` only redirects the old English address. All pages are generated. Services, disclosures and FAQs work without JavaScript; login and reviews need JavaScript.

## Services and fees

Five services, each with options and fees, are defined at the top of `scripts/build.py` (`services`). Each option is `(Hindi name, English name, fee, Hindi detail, English detail)`; change a fee there and rebuild. Moon-sign remedies for the "Rashi remedies" section are in `rashis`.

## Update content

Edit `scripts/build.py`, then run `python3 scripts/build.py`. Commit the generated HTML pages and `sitemap.xml` together with the source. Styling is in `style.css`; interactive features are in `assets/js/`.

## Login, reviews and admin panel (Firebase)

- Customers log in with Google or email/password, write a review (1–5 stars) and see its status and your reply on their account page.
- Email/password customers must verify their email before posting (reduces spam).
- New and edited reviews stay **pending** until the admin publishes them from the admin panel. The admin can reply, publish, hide or delete, and can see registered users.
- Published reviews are kept and shown best first; the admin can feature reviews. Unpublished or hidden reviews and profiles with no login for 30 days carry an `expireAt` and are deleted by the daily **Daily cleanup** workflow (`scripts/cleanup.py`).
- **Bookings:** customers pick a service, a Saturday/Sunday date and a 30-minute slot (IST: 9–12, 2–5, 8–12) in the Book section. Slots are defined in `assets/js/booking.js` and `slotTimes()` in `firestore.rules` (keep both in sync). A booking is stored at `bookings/{date_HHMM}` with a public `slots/{date_HHMM}` marker, so a slot can be booked once. The admin panel's Bookings tab confirms, completes or cancels bookings and opens WhatsApp/phone. Owner alerts go to a Google Sheet and email via `docs/booking-sheet/Code.gs` (setup: `docs/BOOKING-SHEET-SETUP.md`, URL in `site-config.json` → `bookingNotifyUrl`). Bookings are deleted 30 days after the consultation.
- **Contact icons:** WhatsApp, phone, email, Instagram and Facebook come from `site-config.json` → `contact` (set in site-config.json).
- Customers can delete their own account; the privacy policy is `privacy.html` / `privacy-hi.html` (generated).
- Admin access is granted to the emails listed in `firestore.rules` (enforced) and `assets/js/firebase-config.js` (only shows the menu link). Keep both lists in sync.
- Until `assets/js/firebase-config.js` has an `apiKey`, the site shows a "coming soon" message for login and reviews.

Firebase project: `antarodaya-in` (Firestore in asia-south1). Deploy rules and auth providers with `firebase deploy --only firestore:rules,auth --project antarodaya-in`. How the Firebase project, access and credentials are set up: [`docs/FIREBASE.md`](docs/FIREBASE.md).

### Local testing with emulators

```
firebase emulators:start --project demo-antarodaya --only auth,firestore
python3 -m http.server 8000
```

Open http://localhost:8000/?emulator — the site then uses the local emulators instead of the live project.

## Languages

Hindi and English are complete local pages (English is the default); the हिं / EN switch sits in the header. The globe button opens Google's Website Translator for other languages (machine translation, may contain errors; no API key used). Website language availability does not imply consultation availability in that language.

## Google Form

Put the public responder link (not the `/edit` URL) in `site-config.json` under `googleFormUrl`, then run the build. Accepted hosts: `forms.gle` and `docs.google.com/forms/`.

## SEO

Each home page has a keyword-focused title and description, canonical and `hreflang` links, Open Graph/Twitter tags with `assets/brand/og-image.png`, and JSON-LD (Organization, WebSite, WebPage, Service with INR price ranges, FAQPage). `robots.txt` and `sitemap.xml` point to https://antarodaya.in. Account and admin pages are `noindex`.

Review stars from the site's own reviews are deliberately **not** added as `AggregateRating` markup: Google does not show star snippets for self-hosted reviews of your own business and can treat it as spam. For stars in Google Search/Maps, use a Google Business Profile.

## Assets

Brand assets are in `assets/brand/` (see `assets/IMAGE-NOTES.md`). `assets/antarodaya-portrait.png` is the supplied portrait; `qr.png` is the existing payment QR.
