# Firebase setup — login aur reviews chalu karne ke liye (10 minute)

Firebase Google ki free service hai. Login, reviews aur admin panel isi se chalte hain. Free "Spark" plan kaafi hai, card ki zaroorat nahi.

## 1. Project banao
1. https://console.firebase.google.com par **pandeyravidev2@gmail.com** se login karo.
2. **Create a project** → naam: `antarodaya` → Google Analytics chaho to off kar do → **Create**.

## 2. Web app jodo aur config copy karo
1. Project Overview ke paas **</>** (Web) icon dabao → nickname `antarodaya-web` → **Register app** (Hosting wala box mat chuno).
2. Jo `firebaseConfig = { apiKey: ..., authDomain: ..., ... }` dikhe, woh values copy karo.
3. Repo mein `assets/js/firebase-config.js` kholo aur khaali `''` ki jagah ye values bhar do. (Ye values public hoti hain, inhe chhupane ki zaroorat nahi. Data ki suraksha rules se hoti hai.)

## 3. Login ke tareeke chalu karo
**Build → Authentication → Get started → Sign-in method**:
- **Google** → Enable → support email chuno → Save.
- **Email/Password** → Enable (sirf pehla switch) → Save.

Phir **Authentication → Settings → Authorized domains → Add domain**: `antarodaya.in` aur `www.antarodaya.in` jodo.

Optional: **Authentication → Templates** mein verification email ka sender naam "Antarodaya" kar do.

## 4. Database banao aur rules lagao
1. **Build → Firestore Database → Create database** → location **asia-south1 (Mumbai)** → **Start in production mode** → Create.
2. **Rules** tab kholo, repo ki `firestore.rules` file ka poora content paste karo → **Publish**.

## 5. Deploy
`firebase-config.js` save karke commit/push karo (ya Claude se kaho). 1-2 minute mein antarodaya.in par login aur reviews chalu ho jayenge.

## 6. Pehli baar admin login
1. Site par **लॉगिन → Google से जारी रखें** → pandeyravidev2@gmail.com chuno.
2. Upar apne naam par click karo → **एडमिन पैनल**.
3. Yahan naye reviews "जाँच बाकी" tab mein aayenge: **प्रकाशित करें**, **छिपाएँ**, **हटाएँ**, aur **उत्तर** likh kar **उत्तर सहेजें**.

## Admin badalna / doosra admin jodna
Email do jagah likhna hota hai, aur dono jagah same hona chahiye:
- `firestore.rules` → `isAdmin()` ke andar list (asli suraksha yahi hai. Badalne ke baad Firebase console mein dobara Publish karo).
- `assets/js/firebase-config.js` → `adminEmails` (isse sirf menu mein link dikhta hai).
