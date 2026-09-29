// Firebase web app settings. Paste the values from:
// Firebase console → Project settings → General → Your apps → Web app → SDK setup and configuration → Config.
// These values are public by design; your data is protected by firestore.rules.
// While apiKey is empty, login and reviews show a friendly "coming soon" message.
export const firebaseConfig = {
  apiKey: '',
  authDomain: '',
  projectId: '',
  storageBucket: '',
  messagingSenderId: '',
  appId: ''
};

// Accounts that see the admin panel. Must match the list in firestore.rules,
// which is what actually enforces admin access.
export const adminEmails = ['pandeyravidev2@gmail.com'];
