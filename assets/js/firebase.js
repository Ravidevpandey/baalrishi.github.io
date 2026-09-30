// Lazily loads the Firebase SDK so the page itself stays fast.
import { firebaseConfig, adminEmails, recaptchaSiteKey } from './firebase-config.js';

const SDK = 'https://www.gstatic.com/firebasejs/12.19.0/';
const local = ['localhost', '127.0.0.1'].includes(location.hostname);
try {
  if (local && new URLSearchParams(location.search).has('emulator')) sessionStorage.setItem('emulator', '1');
} catch {}
let emulator = false;
try { emulator = local && sessionStorage.getItem('emulator') === '1'; } catch {}

export const configured = emulator || Boolean(firebaseConfig.apiKey && firebaseConfig.projectId);

let ready;
export function getFirebase() {
  if (!configured) return Promise.resolve(null);
  ready ||= (async () => {
    const [appSdk, A, F] = await Promise.all([
      import(SDK + 'firebase-app.js'),
      import(SDK + 'firebase-auth.js'),
      import(SDK + 'firebase-firestore.js')
    ]);
    const app = appSdk.initializeApp(emulator ? { apiKey: 'demo-key', projectId: 'demo-antarodaya', authDomain: 'localhost' } : firebaseConfig);
    // App Check makes Firebase accept requests only from the real site (blocks scripts and bots).
    // No-op until a reCAPTCHA site key is set and App Check is enforced in the console.
    if (!local && recaptchaSiteKey) {
      const AC = await import(SDK + 'firebase-app-check.js');
      AC.initializeAppCheck(app, { provider: new AC.ReCaptchaV3Provider(recaptchaSiteKey), isTokenAutoRefreshEnabled: true });
    }
    const auth = A.getAuth(app);
    const db = F.getFirestore(app);
    if (emulator) {
      A.connectAuthEmulator(auth, 'http://127.0.0.1:9099', { disableWarnings: true });
      F.connectFirestoreEmulator(db, '127.0.0.1', 8080);
    }
    auth.languageCode = document.documentElement.lang === 'en' ? 'en' : 'hi';
    return { auth, db, A, F };
  })();
  return ready;
}

// Unpublished reviews and inactive profiles get an expireAt 30 days ahead; a daily GitHub Actions
// cleanup deletes them once it passes. Published reviews have no expireAt and are kept.
export const RETENTION_MS = 30 * 24 * 60 * 60 * 1000;
export const isLive = doc => !doc.expireAt?.toMillis || doc.expireAt.toMillis() > Date.now();

export const isAdmin = user => Boolean(user && user.emailVerified && adminEmails.includes((user.email || '').toLowerCase()));
