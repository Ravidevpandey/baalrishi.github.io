// Login dialog, header account menu and customer profile record.
import { configured, getFirebase, isAdmin, RETENTION_MS } from './firebase.js';
import { T, errorText } from './i18n.js';
import { el, icon, avatar, modal, toast, siteData } from './ui.js';

let currentUser = null;
let authKnown = false;
const listeners = new Set();

export const getUser = () => currentUser;

// Calls back now (once auth state is known) and whenever the user logs in or out.
export function onUser(callback) {
  listeners.add(callback);
  if (authKnown) callback(currentUser);
  return () => listeners.delete(callback);
}

export async function startAuth() {
  renderHeader();
  const fb = await getFirebase();
  if (!fb) {
    authKnown = true;
    listeners.forEach(fn => fn(null));
    return;
  }
  const { auth, A } = fb;
  A.getRedirectResult(auth).catch(() => {});
  A.onAuthStateChanged(auth, user => {
    currentUser = user;
    authKnown = true;
    renderHeader();
    if (user) saveProfile(user).catch(() => {});
    listeners.forEach(fn => fn(user));
  });
}

// Keeps a small profile document so the admin can see who has registered.
async function saveProfile(user) {
  const { db, F } = await getFirebase();
  const ref = F.doc(db, 'users', user.uid);
  const fields = {
    name: (user.displayName || user.email.split('@')[0]).slice(0, 60),
    email: user.email,
    photoURL: user.photoURL || '',
    provider: user.providerData[0]?.providerId || 'password',
    lastLoginAt: F.serverTimestamp(),
    expireAt: F.Timestamp.fromMillis(Date.now() + RETENTION_MS)
  };
  const snap = await F.getDoc(ref);
  if (snap.exists()) await F.updateDoc(ref, fields);
  else await F.setDoc(ref, { ...fields, createdAt: F.serverTimestamp() });
}

export async function updateDisplayName(name) {
  const { auth, db, A, F } = await getFirebase();
  await A.updateProfile(auth.currentUser, { displayName: name });
  await F.updateDoc(F.doc(db, 'users', auth.currentUser.uid), { name });
  currentUser = auth.currentUser;
  renderHeader();
}

export async function logout() {
  const fb = await getFirebase();
  if (!fb) return;
  await fb.A.signOut(fb.auth);
  toast(T.loggedOut);
}

export async function resendVerification() {
  const { auth, A } = await getFirebase();
  await A.sendEmailVerification(auth.currentUser);
  toast(T.verifySent);
}

// Reloads the user to pick up a just-completed email verification.
export async function refreshUser() {
  const { auth } = await getFirebase();
  await auth.currentUser.reload();
  await auth.currentUser.getIdToken(true);
  currentUser = auth.currentUser;
  renderHeader();
  listeners.forEach(fn => fn(currentUser));
  return currentUser;
}

export async function requireUser() {
  return currentUser || openLogin();
}

function showComingSoon() {
  const data = siteData();
  modal(T.comingSoonTitle, el('div', { class: 'modal-body' },
    el('p', {}, T.comingSoon),
    data.instagramUrl && el('a', { class: 'button primary', href: data.instagramUrl, target: '_blank', rel: 'noopener noreferrer' }, `Instagram ↗`)));
}

// Opens the login / sign-up dialog. Resolves with the user, or null if closed.
export function openLogin(mode = 'login') {
  if (!configured) {
    showComingSoon();
    return Promise.resolve(null);
  }
  return new Promise(resolve => {
    let resolved = false;
    const finish = user => {
      if (resolved) return;
      resolved = true;
      resolve(user);
    };
    const intro = el('p', { class: 'modal-intro' });
    const error = el('p', { class: 'form-error', role: 'alert', hidden: true });
    const nameField = el('label', { class: 'field' }, el('span', {}, T.name),
      el('input', { name: 'name', autocomplete: 'name', maxlength: 60 }));
    const form = el('form', { class: 'auth-form', novalidate: true },
      nameField,
      el('label', { class: 'field' }, el('span', {}, T.email),
        el('input', { name: 'email', type: 'email', autocomplete: 'email', required: true, inputmode: 'email' })),
      el('label', { class: 'field' }, el('span', {}, T.password),
        el('input', { name: 'password', type: 'password', autocomplete: 'current-password', required: true, minlength: 6 }),
        el('small', {}, T.passwordHint)),
      error,
      el('button', { class: 'button primary block', type: 'submit' }));
    const forgot = el('button', { type: 'button', class: 'link-button' }, T.forgot);
    const switchText = el('span');
    const switchButton = el('button', { type: 'button', class: 'link-button strong' });
    const google = el('button', { type: 'button', class: 'button google block' }, icon('google'), T.google);
    const body = el('div', { class: 'modal-body auth' },
      intro, google, el('div', { class: 'divider' }, el('span', {}, T.or)), form,
      el('div', { class: 'auth-foot' }, forgot, el('p', {}, switchText, ' ', switchButton)),
      el('p', { class: 'legal-note' }, T.agreePrefix, ' ', el('a', { href: siteData().privacyUrl || 'privacy.html' }, T.privacyPolicy)));
    const dialog = modal(T.loginTitle, body);
    dialog.addEventListener('close', () => finish(currentUser));

    const setMode = next => {
      mode = next;
      const signup = mode === 'signup';
      dialog.querySelector('#modal-title').textContent = signup ? T.signupTitle : T.loginTitle;
      intro.textContent = signup ? T.signupIntro : T.loginIntro;
      nameField.hidden = !signup;
      form.password.autocomplete = signup ? 'new-password' : 'current-password';
      form.querySelector('[type=submit]').textContent = signup ? T.createAccount : T.signIn;
      switchText.textContent = signup ? T.haveAccount : T.noAccount;
      switchButton.textContent = signup ? T.signIn : T.createAccount;
      forgot.hidden = signup;
      error.hidden = true;
    };
    setMode(mode);
    switchButton.addEventListener('click', () => setMode(mode === 'signup' ? 'login' : 'signup'));

    const fail = err => {
      error.textContent = errorText(err);
      error.hidden = false;
    };
    const busy = (on) => body.querySelectorAll('button, input').forEach(n => { n.disabled = on; });
    const done = user => {
      toast(T.welcome(user.displayName || user.email.split('@')[0]));
      finish(user);
      dialog.close();
    };

    google.addEventListener('click', async () => {
      const { auth, A } = await getFirebase();
      busy(true);
      try {
        const result = await A.signInWithPopup(auth, new A.GoogleAuthProvider());
        done(result.user);
      } catch (err) {
        if (err.code === 'auth/popup-blocked' || err.code === 'auth/operation-not-supported-in-this-environment') {
          await A.signInWithRedirect(auth, new A.GoogleAuthProvider());
          return;
        }
        fail(err);
      } finally {
        busy(false);
      }
    });

    form.addEventListener('submit', async event => {
      event.preventDefault();
      const { auth, A } = await getFirebase();
      const email = form.email.value.trim();
      const password = form.password.value;
      if (!email) return fail({ code: 'auth/invalid-email' });
      if (password.length < 6) return fail({ code: 'auth/weak-password' });
      busy(true);
      try {
        if (mode === 'signup') {
          const { user } = await A.createUserWithEmailAndPassword(auth, email, password);
          const name = form.name.value.trim().slice(0, 60);
          if (name) await A.updateProfile(user, { displayName: name });
          await A.sendEmailVerification(user);
          currentUser = user;
          renderHeader();
          toast(T.verifySent);
          finish(user);
          dialog.close();
        } else {
          const { user } = await A.signInWithEmailAndPassword(auth, email, password);
          done(user);
        }
      } catch (err) {
        fail(err);
      } finally {
        busy(false);
      }
    });

    forgot.addEventListener('click', async () => {
      const email = form.email.value.trim();
      if (!email) {
        error.textContent = T.enterEmailFirst;
        error.hidden = false;
        form.email.focus();
        return;
      }
      const { auth, A } = await getFirebase();
      try {
        await A.sendPasswordResetEmail(auth, email);
        toast(T.resetSent);
      } catch (err) {
        fail(err);
      }
    });
  });
}

// Header button: "Log in" when signed out, avatar + menu when signed in.
function renderHeader() {
  const data = siteData();
  document.querySelectorAll('[data-account-button]').forEach(button => {
    const user = currentUser;
    const menu = button.parentElement.querySelector('.account-menu');
    menu?.remove();
    button.replaceChildren();
    button.setAttribute('aria-expanded', 'false');
    if (!user) {
      button.append(icon('user'), el('span', { class: 'account-label' }, T.login));
      button.removeAttribute('aria-haspopup');
      return;
    }
    const name = user.displayName || user.email.split('@')[0];
    button.setAttribute('aria-haspopup', 'menu');
    button.append(avatar(name, user.photoURL, 'sm'), el('span', { class: 'account-label' }, name.split(' ')[0]));
    const items = [
      el('a', { href: data.accountUrl || 'account.html', role: 'menuitem' }, T.myAccount),
      isAdmin(user) && el('a', { href: data.adminUrl || 'admin.html', role: 'menuitem' }, T.adminPanel),
      el('button', { type: 'button', role: 'menuitem', onclick: () => logout() }, T.logout)
    ];
    button.after(el('div', { class: 'account-menu', role: 'menu', hidden: true },
      el('p', { class: 'account-menu-head' }, el('strong', {}, name), el('small', {}, user.email)), items));
  });
}

document.addEventListener('click', event => {
  const button = event.target.closest('[data-account-button]');
  document.querySelectorAll('.account-menu').forEach(menu => {
    if (!button && !menu.contains(event.target)) {
      menu.hidden = true;
      menu.previousElementSibling?.setAttribute('aria-expanded', 'false');
    }
  });
  if (!button) return;
  event.preventDefault();
  if (!currentUser) {
    openLogin();
    return;
  }
  const menu = button.nextElementSibling;
  if (menu?.classList.contains('account-menu')) {
    menu.hidden = !menu.hidden;
    button.setAttribute('aria-expanded', String(!menu.hidden));
  }
});
document.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  document.querySelectorAll('.account-menu').forEach(menu => { menu.hidden = true; });
});
