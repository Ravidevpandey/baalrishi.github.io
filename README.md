# Antarodaya (अंतरोदय) website

Responsive static website for GitHub Pages, served at https://antarodaya.in (see `CNAME`).

| Page | Hindi | English |
|---|---|---|
| Home | `hi.html` | `index.html` (default) |
| Customer account | `account-hi.html` | `account.html` |
| Admin panel | `admin-hi.html` | `admin.html` |

English opens first; the हिं / EN switch in the header changes language. `en.html`, `account-en.html` and `admin-en.html` only redirect old links. All pages are generated. Services, disclosures and FAQs work without JavaScript; login and reviews need JavaScript.

## Services and fees

Five services, each with options and fees, are defined at the top of `scripts/build.py` (`services`). Each option is `(Hindi name, English name, fee, Hindi detail, English detail)`; change a fee there and rebuild. Moon-sign remedies for the "Rashi remedies" section are in `rashis`.

## Update content

Edit `scripts/build.py`, then run `python3 scripts/build.py`. Commit the generated HTML pages and `sitemap.xml` together with the source. Styling is in `style.css`; interactive features are in `assets/js/`.

## Login, reviews and admin panel (Firebase)

- Customers log in with Google or email/password, write a review (1–5 stars) and see its status and your reply on their account page.
- Email/password customers must verify their email before posting (reduces spam).
- New and edited reviews stay **pending** until the admin publishes them from the admin panel. The admin can reply, publish, hide or delete, and can see registered users.
- Admin access is granted to the emails listed in `firestore.rules` (enforced) and `assets/js/firebase-config.js` (only shows the menu link). Keep both lists in sync.
- Until `assets/js/firebase-config.js` has an `apiKey`, the site shows a "coming soon" message for login and reviews.

Setup steps: see [`docs/FIREBASE-SETUP.md`](docs/FIREBASE-SETUP.md).

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
