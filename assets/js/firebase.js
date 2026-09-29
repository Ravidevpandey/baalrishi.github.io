// Lazily loads the Firebase SDK so the page itself stays fast.
import { firebaseConfig, adminEmails } from './firebase-config.js';

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

export const isAdmin = user => Boolean(user && user.emailVerified && adminEmails.includes((user.email || '').toLowerCase()));
