# Baal Rishi website

Responsive static website for GitHub Pages. Hindi: `index.html`; English: `en.html`. All services, disclosures and FAQs are rendered in HTML and work without JavaScript.

## Update content

Edit `scripts/build.py`, then run `python3 scripts/build.py`. Commit both generated HTML pages along with the source. Styling is in `style.css`.

## Google Form

Open your own form at https://forms.google.com. Publish it / enable responder access, then copy the **responder link** from Publish/Send → link. Test the link in a private browser window. Do not use the editor URL ending in `/edit`.

Put the exact public URL in `site-config.json` under `googleFormUrl`, then run `python3 scripts/build.py`. Accepted hosts: `forms.gle` and `docs.google.com/forms/`. Until configured, both pages clearly state that the form is unavailable and provide the existing Instagram contact link.

Suggested form fields: name, contact method, selected service, main question, preferred consultation language; birth details only when relevant. Avoid collecting medical reports, identity documents, banking credentials or third-party data without consent. Explain the service limits and how submitted information is used in the form itself.

## Languages

Hindi and English are complete local pages. Other language links open Google Translate's website translation service; its language picker provides additional supported languages. These are external machine translations, not reviewed local translations or a guarantee of support for every language. No API key is exposed and no unsupported embedded translator widget is used. Website language availability does not imply consultation availability in that language.

## Preview and deployment

Run `python3 -m http.server 8000` in this folder. GitHub Pages should publish the `main` branch, `/ (root)`. Expected project URL: https://ravidevpandey.github.io/baalrishi.github.io/

The existing fees, Instagram destination and payment QR are preserved. Availability, fee range details, consultation format and refund terms must be confirmed by the owner with the customer before payment.

## Assets

`assets/spiritual-still-life.webp`: generated editorial spiritual still life. `assets/baalrishi.webp`: optimized copy of the existing symbolic brand artwork; not represented as a practitioner photograph. The original `baalrishi.png` and `qr.png` are retained. Image-generation prompt and provenance are in `assets/IMAGE-NOTES.md`.
