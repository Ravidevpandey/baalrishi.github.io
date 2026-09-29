# Booking alerts: Google Sheet + email (5 minute)

Website par har nayi booking is Google Sheet mein ek nayi line ban kar aayegi aur aapko email bhi aayega.

1. **Sheet banayein:** https://sheets.new kholein (pandeyravidev2@gmail.com se). Naam rakhein: `Antarodaya Bookings`.
2. **Code daalein:** menu **Extensions → Apps Script**. Wahan jo code hai use hata kar `docs/booking-sheet/Code.gs` ka poora code paste karein. Upar 💾 **Save** dabayein.
3. **Ek baar chalayein:** upar function list mein `setup` chunein → **Run**. Permission maange to **Review permissions** → apna account → **Advanced → Go to … (unsafe)** → **Allow**. (Ye aapka apna script hai, isliye Google "unsafe" likhta hai.) Aapko ek test email aayega aur Sheet mein "Bookings" tab ban jayega.
4. **Publish karein:** **Deploy → New deployment** → ⚙️ se type **Web app** chunein.
   - Execute as: **Me**
   - Who has access: **Anyone**
   - **Deploy** dabayein aur jo **Web app URL** mile (`https://script.google.com/macros/s/.../exec`) use copy karein.
5. **URL website mein daalein:** `site-config.json` mein `"bookingNotifyUrl"` ki jagah ye URL daalein aur `python3 scripts/build.py` chalayein (ya URL Claude ko bhej dein).

Phone par alerts ke liye Gmail app mein notifications on rakhein. Sheet ko phone ke Google Sheets app mein bhi dekh sakte hain.

Code badalne ke baad: **Deploy → Manage deployments → ✏️ → Version: New version → Deploy** (URL wahi rehta hai).
