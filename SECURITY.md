# Security policy

Please report a vulnerability privately through GitHub: **Security → Report a vulnerability** on this repository. Do not open a public issue for security problems.

## How the site is protected

- Static site on GitHub Pages over HTTPS (enforced).
- Customer data (accounts and reviews) lives in Firebase. Access is enforced server-side by `firestore.rules`: customers can read and edit only their own reviews, cannot publish or reply, and must verify their email before posting; only the admin email in the rules can moderate and see users.
- User-written text is always inserted as text, never as HTML.
- Every push runs CI: Gitleaks secret scan, CodeQL (JavaScript, Python, workflows), link checks, a check that generated pages match the source, and an end-to-end test of login, reviews, admin replies and the security rules against the Firebase emulators.
- GitHub Actions are pinned to commit SHAs and kept current by Dependabot.
