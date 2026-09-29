# Firebase: kya hai, kahan hai, aur credentials

## Aapka access (sabse zaroori)
- Firebase ka **alag koi password nahi hai.** Project aapke Google account **pandeyravidev2@gmail.com** se juda hai; jo is account mein login hai, wahi project ka malik hai.
- Console: https://console.firebase.google.com/project/antarodaya-in
- Is Google account par **2-Step Verification** zaroor on rakhein (myaccount.google.com → Security). Admin panel ki chaabi bhi yahi account hai.

## Project ki jaankari
| Cheez | Value |
|---|---|
| Project ID | `antarodaya-in` |
| Project number | `963565839058` |
| Plan | Spark (free, koi card/billing nahi) |
| Database | Cloud Firestore, `asia-south1` (Mumbai) |
| Login | Email/Password aur Google |
| Authorized domains | antarodaya.in, www.antarodaya.in (+ Firebase ke apne) |
| Admin email | pandeyravidev2@gmail.com (`firestore.rules` → `isAdmin()` aur `assets/js/firebase-config.js`) |

Database ke collections: `reviews`, `users`, `bookings`, `slots`. Kaun kya padh/likh sakta hai, ye `firestore.rules` tay karta hai.

## "Keys" jo dikhti hain, par secret nahi hain
- `assets/js/firebase-config.js` mein **web config (apiKey waghairah)** hai. Ye Google ke design ke hisaab se public hoti hai; har Firebase website mein browser ko dikhti hai. Suraksha rules se hoti hai.
- Ye key sirf in websites se chalti hai: `https://antarodaya.in/*`, `https://www.antarodaya.in/*`, `https://antarodaya-in.firebaseapp.com/*`. Kahan dekhein: Google Cloud Console → APIs & Services → Credentials → "Browser key (auto created by Firebase)".
- GitHub ka secret-scanning alert isi key ka tha; ise "public by design" likh kar band kiya gaya hai.

## Roz ki safai wala bot (bina kisi key ke)
- Service account: `cleanup-bot@antarodaya-in.iam.gserviceaccount.com`, role sirf `Cloud Datastore User` (database padhna/mitaana).
- Iski **koi key file nahi banayi gayi.** GitHub Actions (`.github/workflows/cleanup.yml`) Workload Identity Federation se login karta hai, aur ye sirf repo `Ravidevpandey/antarodaya` ki `main` branch se ho sakta hai.
- Kahan dekhein: Google Cloud Console → IAM & Admin → Workload Identity Federation → pool `github`.

## Kahin bhi store nahi hai
- Koi service-account key file nahi, GitHub par koi Actions secret nahi, aur repo mein koi password nahi (Gitleaks har push par check karta hai).
- Setup ke waqt jo CLI logins (Firebase CLI, GitHub CLI) use hue the, woh is computer se logout kar diye gaye hain.
- Aur pakka karne ke liye aap khud access hata sakte hain:
  - Google: https://myaccount.google.com/permissions → **Firebase CLI** → Remove access
  - GitHub: Settings → Applications → Authorized OAuth Apps → **GitHub CLI** → Revoke

## Aage kabhi rules badalne hon
```
firebase login
firebase deploy --only firestore:rules,auth --project antarodaya-in
```
