// Firebase web app settings. Paste the values from:
// Firebase console → Project settings → General → Your apps → Web app → SDK setup and configuration → Config.
// These values are public by design; your data is protected by firestore.rules.
export const firebaseConfig = {
  apiKey: 'AIzaSyAUbUYOKopdMg7poHYGujqkqxEC2lmezF4',
  authDomain: 'antarodaya-in.firebaseapp.com',
  projectId: 'antarodaya-in',
  storageBucket: 'antarodaya-in.firebasestorage.app',
  messagingSenderId: '963565839058',
  appId: '1:963565839058:web:e9066e667ddc65368f430b'
};

// App Check (anti-abuse): paste the reCAPTCHA v3 site key from
// Firebase console → App Check → Apps → your web app → reCAPTCHA v3.
// Leave empty until App Check is enabled; the site works either way.
export const recaptchaSiteKey = '';

// Accounts that see the admin panel. Must match the list in firestore.rules,
// which is what actually enforces admin access.
export const adminEmails = ['pandeyravidev2@gmail.com'];
