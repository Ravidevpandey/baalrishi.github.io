"""End-to-end test against the Firebase emulators: signup, email verification, review, moderation,
admin reply and Firestore security rules.

Run: firebase emulators:exec --project demo-antarodaya --only auth,firestore "python3 tests/e2e.py"
while the site is served at http://localhost:8000 (python3 -m http.server 8000).
"""
import asyncio, datetime, json, os, sys, tempfile, urllib.request
from playwright.async_api import async_playwright, expect

S = os.environ.get('SCREENSHOT_DIR', tempfile.gettempdir()) + '/'
BASE = 'http://localhost:8000/'
PID = 'demo-antarodaya'
results = []

# Month-end offer window (see assets/js/offer.js): the last 7 days of the IST month.
IST_NOW = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
OFFER_MONTH = IST_NOW.strftime('%Y-%m')
OFFER_ON = (IST_NOW + datetime.timedelta(days=7)).month != IST_NOW.month

def check(name, ok, detail=''):
    results.append((name, ok))
    print(('PASS ' if ok else 'FAIL ') + name + (f' — {detail}' if detail else ''), flush=True)

def http(method, url, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer owner'})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read() or b'{}')

def reset():
    http('DELETE', f'http://127.0.0.1:8080/emulator/v1/projects/{PID}/databases/(default)/documents')
    http('DELETE', f'http://127.0.0.1:9099/emulator/v1/projects/{PID}/accounts')

def verify_email(email):
    codes = http('GET', f'http://127.0.0.1:9099/emulator/v1/projects/{PID}/oobCodes')['oobCodes']
    link = [c for c in codes if c['email'] == email and c['requestType'] == 'VERIFY_EMAIL'][-1]['oobLink']
    urllib.request.urlopen(link).read()

async def new_page(browser, width=1280):
    # The harness evaluates snippets with new Function(), which the site's CSP (rightly) forbids;
    # CSP itself is checked separately in csp_check() with a normal browser context.
    ctx = await browser.new_context(viewport={'width': width, 'height': 900}, bypass_csp=True, ignore_https_errors=os.environ.get('E2E_IGNORE_HTTPS_ERRORS') == '1')
    page = await ctx.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' and 'translate' not in m.text else None)
    page.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
    page.errors = errors
    return page

async def signup(page, name, email, password='secret123'):
    await page.click('[data-account-button]')
    await page.get_by_role('button', name='खाता बनाएँ').or_(page.get_by_role('button', name='Create account')).first.click()
    await page.fill('dialog input[name=name]', name)
    await page.fill('dialog input[name=email]', email)
    await page.fill('dialog input[name=password]', password)
    await page.click('dialog button[type=submit]')
    await expect(page.locator('dialog.modal')).to_have_count(0)

async def rules_probe(page, code):
    """Run a snippet with the page's Firebase instance; returns 'ok' or the error code."""
    return await page.evaluate("""async (code) => {
      const { getFirebase } = await import('/assets/js/firebase.js');
      const { auth, db, F } = await getFirebase();
      try { await (new Function('auth','db','F', 'return (async()=>{' + code + '})()'))(auth, db, F); return 'ok'; }
      catch (e) { return e.code || String(e); }
    }""", code)

async def csp_check(browser):
    """Load every page under the real Content Security Policy and fail on any blocked resource."""
    ctx = await browser.new_context(ignore_https_errors=os.environ.get('E2E_IGNORE_HTTPS_ERRORS') == '1')
    blocked = []
    for path in ('', 'hi.html?emulator', 'account.html', 'admin-hi.html', 'privacy.html'):
        page = await ctx.new_page()
        page.on('console', lambda m: blocked.append(m.text[:200]) if 'Content Security Policy' in m.text and 'gen204' not in m.text else None)
        await page.goto(BASE + path, wait_until='load')
        await page.wait_for_timeout(1500)
        await page.close()
    await ctx.close()
    check('pages load under the Content Security Policy', not blocked, '; '.join(blocked[:2]))


async def main():
    reset()
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # ---------- Customer ----------
        cust = await new_page(browser)
        await cust.goto(BASE + 'hi.html?emulator', wait_until='load')
        await expect(cust.locator('[data-review-list]')).to_contain_text('अभी कोई प्रकाशित अनुभव नहीं')
        check('empty reviews state shown', await cust.locator('.review-empty.first button').is_visible())

        await cust.click('[data-write-review]')
        await expect(cust.locator('dialog.modal')).to_be_visible()
        check('write review while logged out opens login', await cust.locator('dialog .button.google').is_visible())
        await cust.keyboard.press('Escape')

        await cust.click('[data-account-button]')
        await cust.fill('dialog input[name=email]', 'nobody@example.com')
        await cust.fill('dialog input[name=password]', 'wrongpass')
        await cust.click('dialog button[type=submit]')
        await expect(cust.locator('dialog .form-error')).to_be_visible()
        check('wrong login shows friendly error', True, await cust.locator('dialog .form-error').inner_text())
        await cust.keyboard.press('Escape')

        await signup(cust, 'Sita Sharma', 'sita@example.com')
        await expect(cust.locator('[data-account-button] .account-label')).to_have_text('Sita')
        check('signup logs in and header shows first name', True)

        await cust.click('[data-write-review]')
        await expect(cust.locator('dialog')).to_contain_text('पुष्टि करें')
        check('unverified user asked to verify email', True)
        blocked = await rules_probe(cust, "await F.addDoc(F.collection(db,'reviews'),{uid:auth.currentUser.uid,name:'X',rating:5,text:'unverified attempt',status:'pending',createdAt:F.serverTimestamp()})")
        check('rules: unverified user cannot post review', blocked == 'permission-denied', blocked)

        verify_email('sita@example.com')
        await cust.get_by_role('button', name='मैंने पुष्टि कर दी').click()
        await expect(cust.locator('dialog .review-form')).to_be_visible()
        check('after verification the review form opens', True)
        await cust.screenshot(path=S + 't-review-form.png')

        xs = [await cust.locator(f'dialog label[for=rate-{i}]').bounding_box() for i in (1, 5)]
        check('stars run 1 to 5 from left to right', xs[0]['x'] < xs[1]['x'])
        await cust.locator('dialog label[for=rate-2]').hover()
        check('hovering star 2 lights exactly 2 stars', await cust.locator('dialog .star-input label.on').count() == 2)
        await cust.click('dialog button[type=submit]')
        check('validation: rating required', 'रेटिंग' in await cust.locator('dialog .form-error').inner_text())
        await cust.click('dialog label[for=rate-5]')
        check('rating word shown', await cust.locator('dialog .rating-hint').inner_text() == 'उत्कृष्ट')
        check('choosing 5 lights all 5 stars', await cust.locator('dialog .star-input label.on').count() == 5)
        await cust.fill('dialog textarea', 'बहुत ही शांत और स्पष्ट परामर्श मिला। मेरे सवालों को ध्यान से सुना गया।')
        await cust.select_option('dialog select', 'kundali')
        await cust.click('dialog button[type=submit]')
        check('validation: consent required', 'सहमति' in await cust.locator('dialog .form-error').inner_text())
        await cust.check('dialog input[name=consent]')
        await cust.click('dialog button[type=submit]')
        await expect(cust.locator('dialog.modal')).to_have_count(0)
        await expect(cust.locator('.toast')).to_contain_text('धन्यवाद')
        check('review submitted', True)

        await cust.reload(wait_until='load')
        await expect(cust.locator('[data-review-list]')).to_contain_text('अभी कोई प्रकाशित अनुभव नहीं')
        check('pending review is not public yet', True)

        # ---------- Booking ----------
        await cust.goto(BASE + 'hi.html?emulator#booking', wait_until='load')
        await cust.select_option('#book-service', 'kundali')
        await cust.select_option('#book-option', index=1)
        await cust.click('[data-booking] .chip-row.scroll .slot-chip >> nth=0')
        await expect(cust.locator('.time-group .slot-chip').first).to_be_visible()
        first_time = await cust.locator('.time-group .slot-chip').first.inner_text()
        await cust.click('.time-group .slot-chip >> nth=0')
        await cust.fill('#book-name', 'Sita Sharma')
        await cust.fill('#book-phone', '+91 98765 43210')
        await cust.click('.mode-option:has-text("फ़ोन कॉल")')
        await cust.click('[data-booking] button[type=submit]')
        await expect(cust.locator('.booking-done')).to_be_visible()
        check('customer books a weekend slot', True, first_time)
        booked = await cust.evaluate("""async()=>{const {getFirebase}=await import('/assets/js/firebase.js');const {auth,db,F}=await getFirebase();
          const s=await F.getDocs(F.query(F.collection(db,'bookings'),F.where('uid','==',auth.currentUser.uid)));const d=s.docs[0];return {id:d.id,...d.data(),createdAt:null,expireAt:null}}""")
        check('booking stored with slot id, phone and mode', booked['id'] == booked['date'] + '_' + booked['time'].replace(':', '') and booked['mode'] == 'phone' and booked['status'] == 'requested')
        check('month-end offer applied only inside its window', booked.get('offer') == (OFFER_MONTH if OFFER_ON else None), f"offer={booked.get('offer')} window={OFFER_ON}")
        check('booking confirmation shows the fee', ('₹51' if OFFER_ON else '₹101') in await cust.locator('.booking-done .book-fee').inner_text())
        # A second offer booking by the same customer, or one outside the window, is refused.
        d2 = next((d for d in [(datetime.date.today() + datetime.timedelta(days=i)) for i in range(2, 30)] if d.weekday() == 5)).isoformat()
        offer_batch = ("const d='" + d2 + "',t='14:00',id=d+'_1400',m='" + OFFER_MONTH + "',uid=auth.currentUser.uid,ex=F.Timestamp.fromMillis(Date.now()+30*864e5);"
                       "const b=F.writeBatch(db);b.set(F.doc(db,'bookings',id),{uid,name:'X',phone:'9876543210',email:auth.currentUser.email,service:'palm',option:'Main lines reading',mode:'whatsapp',date:d,time:t,status:'requested',createdAt:F.serverTimestamp(),expireAt:ex,offer:m});"
                       "b.set(F.doc(db,'slots',id),{date:d,time:t,expireAt:ex});b.set(F.doc(db,'offerClaims',m+'_'+uid),{uid,booking:id,expireAt:ex});"
                       "b.set(F.doc(db,'offers',m),{claimed:F.increment(1),expireAt:ex},{merge:true});await b.commit()")
        r = await rules_probe(cust, offer_batch)
        check('rules: one offer per customer per month / none outside the window', r == 'permission-denied', r)
        r = await rules_probe(cust, f"await F.setDoc(F.doc(db,'offers','{OFFER_MONTH}'),{{claimed:0,expireAt:F.Timestamp.fromMillis(Date.now()+30*864e5)}})")
        check('rules: customer cannot reset the offer counter', r == 'permission-denied', r)
        if OFFER_ON:
            left = await cust.evaluate(f"""async()=>{{const {{getFirebase}}=await import('/assets/js/firebase.js');const {{db,F}}=await getFirebase();return (await F.getDoc(F.doc(db,'offers','{OFFER_MONTH}'))).data().claimed}}""")
            check('offer counter counts the booking', left == 1, str(left))
            await cust.goto(BASE + 'hi.html?emulator#services', wait_until='load')
            await expect(cust.locator('#services .offer-banner')).to_contain_text('11 में से 10')
            check('offer banner shows places left', True)
            check('fees show regular price struck through', await cust.locator('#kundali .option-list s.regular-fee').count() == 6)
        slot = f"{booked['date']}|{booked['time']}"
        r = await rules_probe(cust, f"const [d,t]='{slot}'.split('|');const id=d+'_'+t.replace(':','');const b=F.writeBatch(db);b.set(F.doc(db,'bookings',id),{{uid:auth.currentUser.uid,name:'Again',phone:'9876543210',email:auth.currentUser.email,service:'palm',mode:'whatsapp',date:d,time:t,status:'requested',createdAt:F.serverTimestamp(),expireAt:F.Timestamp.fromMillis(Date.now()+40*864e5)}});b.set(F.doc(db,'slots',id),{{date:d,time:t,expireAt:F.Timestamp.fromMillis(Date.now()+40*864e5)}});await b.commit()")
        check('rules: the same slot cannot be booked twice', r == 'permission-denied', r)
        def next_day(weekday):  # 0=Mon .. 6=Sun
            import datetime
            d = datetime.date.today() + datetime.timedelta(days=1)
            while d.weekday() != weekday: d += datetime.timedelta(days=1)
            return d.isoformat()
        for label, d, t in [('a weekday', next_day(2), '10:00'), ('a time outside consultation hours', next_day(5), '13:00'), ('a time after 11 pm', next_day(5), '23:00')]:
            r = await rules_probe(cust, f"const d='{d}',t='{t}';const id=d+'_'+t.replace(':','');const b=F.writeBatch(db);b.set(F.doc(db,'bookings',id),{{uid:auth.currentUser.uid,name:'X',phone:'9876543210',email:auth.currentUser.email,service:'palm',mode:'whatsapp',date:d,time:t,status:'requested',createdAt:F.serverTimestamp(),expireAt:F.Timestamp.fromMillis(Date.now()+40*864e5)}});b.set(F.doc(db,'slots',id),{{date:d,time:t,expireAt:F.Timestamp.fromMillis(Date.now()+40*864e5)}});await b.commit()")
            check(f'rules: cannot book {label}', r == 'permission-denied', r)
        r = await rules_probe(cust, f"const id='{booked['id']}';await F.updateDoc(F.doc(db,'bookings',id),{{status:'confirmed'}})")
        check('rules: customer cannot confirm own booking', r == 'permission-denied', r)

        # security rules as customer
        r = await rules_probe(cust, "const s=await F.getDocs(F.query(F.collection(db,'reviews'),F.where('uid','==',auth.currentUser.uid))); await F.updateDoc(s.docs[0].ref,{status:'approved'})")
        check('rules: customer cannot self-publish', r == 'permission-denied', r)
        r = await rules_probe(cust, "const s=await F.getDocs(F.query(F.collection(db,'reviews'),F.where('uid','==',auth.currentUser.uid))); await F.updateDoc(s.docs[0].ref,{reply:{text:'fake'}})")
        check('rules: customer cannot write admin reply', r == 'permission-denied', r)
        r = await rules_probe(cust, "await F.addDoc(F.collection(db,'reviews'),{uid:auth.currentUser.uid,name:'X',rating:5,text:'trying approved',status:'approved',createdAt:F.serverTimestamp()})")
        check('rules: cannot create pre-approved review', r == 'permission-denied', r)
        r = await rules_probe(cust, "await F.addDoc(F.collection(db,'reviews'),{uid:'someone-else',name:'X',rating:5,text:'impersonation',status:'pending',createdAt:F.serverTimestamp()})")
        check('rules: cannot post as another user', r == 'permission-denied', r)
        r = await rules_probe(cust, "await F.addDoc(F.collection(db,'reviews'),{uid:auth.currentUser.uid,name:'X',rating:9,text:'bad rating value',status:'pending',createdAt:F.serverTimestamp()})")
        check('rules: rating must be 1-5', r == 'permission-denied', r)
        r = await rules_probe(cust, "await F.addDoc(F.collection(db,'reviews'),{uid:auth.currentUser.uid,name:'X',rating:5,text:'no expiry field here',status:'pending',createdAt:F.serverTimestamp()})")
        check('rules: review must carry a 30-day expiry', r == 'permission-denied', r)
        r = await rules_probe(cust, "await F.addDoc(F.collection(db,'reviews'),{uid:auth.currentUser.uid,name:'X',rating:5,text:'expiry a year away',status:'pending',createdAt:F.serverTimestamp(),expireAt:F.Timestamp.fromMillis(Date.now()+365*864e5)})")
        check('rules: expiry cannot be pushed beyond 30 days', r == 'permission-denied', r)
        r = await rules_probe(cust, "await F.getDocs(F.collection(db,'users'))")
        check('rules: customer cannot list all users', r == 'permission-denied', r)
        r = await rules_probe(cust, "await F.getDocs(F.collection(db,'reviews'))")
        check('rules: customer cannot list all reviews', r == 'permission-denied', r)

        await cust.goto(BASE + 'account-hi.html', wait_until='load')
        await expect(cust.locator('.my-reviews .chip')).to_have_text('जाँच में')
        check('account page shows my review as pending', True)
        await cust.screenshot(path=S + 't-account-pending.png', full_page=True)

        await cust.goto(BASE + 'admin-hi.html', wait_until='load')
        await expect(cust.locator('[data-app]')).to_contain_text('केवल एडमिन')
        check('non-admin blocked from admin panel', True)

        # ---------- Admin ----------
        adm = await new_page(browser)
        await adm.goto(BASE + '?emulator', wait_until='load')
        await signup(adm, 'Ravi Pandey', 'pandeyravidev2@gmail.com')
        verify_email('pandeyravidev2@gmail.com')
        await adm.evaluate("async()=>{const {refreshUser}=await import('/assets/js/auth-ui.js'); await refreshUser();}")
        await adm.click('[data-account-button]')
        check('admin menu shows Admin panel link', await adm.locator('.account-menu a', has_text='Admin panel').is_visible())
        await adm.goto(BASE + 'admin.html', wait_until='load')
        await expect(adm.locator('.stat').nth(2)).to_contain_text('1')
        check('admin sees 1 pending', True)
        check('admin sees 2 users', '2' in await adm.locator('.stat').nth(4).inner_text())
        await expect(adm.locator('.booking-card')).to_have_count(1)
        check('admin sees the booking with WhatsApp link', 'wa.me/919876543210' in (await adm.locator('.booking-card a:has-text("WhatsApp")').get_attribute('href')))
        await adm.screenshot(path=S + 't-admin-bookings.png', full_page=True)
        await adm.click('.booking-card button:has-text("Confirm")')
        await expect(adm.locator('.booking-card .chip.confirmed')).to_be_visible()
        check('admin confirms a booking', True)
        price = await adm.evaluate(f"""async()=>{{const {{getFirebase}}=await import('/assets/js/firebase.js');const {{db,F}}=await getFirebase();return (await F.getDoc(F.doc(db,'bookings','{booked['id']}'))).data().price}}""")
        check('confirming records the fee quoted', price == (51 if OFFER_ON else 101), str(price))
        await adm.click('.tabs button >> nth=1')
        await adm.screenshot(path=S + 't-admin-pending.png', full_page=True)
        await adm.click('.tabs button >> nth=1')
        await adm.click('.templates .chip-button >> nth=0')
        await adm.click('text=Save reply')
        await expect(adm.locator('.toast')).to_contain_text('Reply saved')
        await adm.click('button.success')
        await expect(adm.locator('.stat').nth(2)).to_contain_text('0')
        check('admin reply saved and review published', True)
        kept = await adm.evaluate("""async()=>{const {getFirebase}=await import('/assets/js/firebase.js');const {db,F}=await getFirebase();
          const s=await F.getDocs(F.query(F.collection(db,'reviews'),F.where('status','==','approved')));return s.docs.every(d=>!('expireAt' in d.data()))}""")
        check('published review has no expiry (kept)', kept)
        await adm.click('.tabs button >> nth=2')
        await adm.click('button[aria-pressed="false"]:has-text("Feature")')
        await expect(adm.locator('.chip.featured')).to_be_visible()
        check('admin can feature a review', True)
        await adm.click('.tabs button >> nth=5')
        await expect(adm.locator('.users-table tbody tr')).to_have_count(2)
        check('admin users tab lists users', True)
        await adm.screenshot(path=S + 't-admin-users.png', full_page=True)

        # ---------- Public visitor ----------
        pub = await new_page(browser)
        await pub.goto(BASE + 'hi.html?emulator#reviews', wait_until='load')
        await expect(pub.locator('.review-card')).to_have_count(1)
        check('public sees published review', True)
        check('featured review shows badge', await pub.locator('.review-card.featured .featured-badge').is_visible())
        await pub.click('[data-bar="5"] button')
        await expect(pub.locator('.filter-bar')).to_be_visible()
        check('5-star filter shows matching reviews', await pub.locator('.review-card').count() == 1)
        check('empty rating filters are disabled', await pub.locator('[data-bar="1"] button').is_disabled())
        await pub.click('.filter-bar button')
        await expect(pub.locator('.filter-bar')).to_have_count(0)
        check('public sees admin reply', 'Thank you so much' in await pub.locator('.review-reply').inner_text())
        check('average rating shown', (await pub.locator('[data-avg]').inner_text()).startswith('5'))
        await pub.locator('#reviews').screenshot(path=S + 't-public-reviews.png')
        await pub.goto(BASE + 'hi.html?emulator#booking', wait_until='load')
        await pub.select_option('#book-service', 'palm')
        await pub.click('[data-booking] .chip-row.scroll .slot-chip >> nth=0')
        await expect(pub.locator('.time-group .slot-chip').first).to_be_visible()
        times = await pub.locator('.time-group .slot-chip').all_inner_texts()
        check('booked time is no longer offered to others', first_time not in times, first_time)
        r = await rules_probe(pub, "const s=await F.getDocs(F.collection(db,'slots'));if(s.docs.some(d=>Object.keys(d.data()).some(k=>!['date','time','expireAt'].includes(k))))throw {code:'LEAK'}")
        check('public slot list holds no personal data', r == 'ok', r)
        r = await rules_probe(pub, "await F.getDocs(F.collection(db,'bookings'))")
        check('rules: public cannot read bookings', r == 'permission-denied', r)
        r = await rules_probe(pub, "await F.getDocs(F.query(F.collection(db,'reviews'),F.where('status','==','pending')))")
        check('rules: public cannot read pending reviews', r == 'permission-denied', r)
        if OFFER_ON:
            # The 12th offer booking of the month is refused; the 11th is accepted.
            await signup(pub, 'Gita Rao', 'gita@example.com')
            verify_email('gita@example.com')
            await pub.evaluate("async()=>{const {refreshUser}=await import('/assets/js/auth-ui.js'); await refreshUser();}")
            counter = f'http://127.0.0.1:8080/v1/projects/{PID}/databases/(default)/documents/offers/{OFFER_MONTH}?updateMask.fieldPaths=claimed'
            http('PATCH', counter, {'fields': {'claimed': {'integerValue': '11'}}})
            r = await rules_probe(pub, offer_batch)
            check('rules: no offer after 11 places are taken', r == 'permission-denied', r)
            http('PATCH', counter, {'fields': {'claimed': {'integerValue': '10'}}})
            r = await rules_probe(pub, offer_batch)
            check('rules: the 11th offer booking is accepted', r == 'ok', r)

        # customer edits → goes back to review
        await cust.goto(BASE + 'account-hi.html', wait_until='load')
        await expect(cust.locator('.my-reviews .chip')).to_have_text('प्रकाशित')
        check('customer sees published + reply', 'Thank you so much' in await cust.locator('.my-reviews').inner_text())
        await expect(cust.locator('.booking-card .chip.confirmed')).to_have_text('पक्की')
        check('customer sees booking confirmed', True)
        await cust.click('.booking-card button:has-text("बुकिंग रद्द करें")')
        await expect(cust.locator('#bookings .review-empty')).to_be_visible()
        freed = await cust.evaluate(f"""async()=>{{const {{getFirebase}}=await import('/assets/js/firebase.js');const {{db,F}}=await getFirebase();return !(await F.getDoc(F.doc(db,'slots','{booked['id']}'))).exists()}}""")
        check('cancelling frees the slot', freed)
        await cust.click('.my-reviews button:has-text("बदलें")')
        await cust.fill('dialog textarea', 'संशोधित: बहुत ही शांत और स्पष्ट परामर्श मिला।')
        await cust.click('dialog button[type=submit]')
        await expect(cust.locator('.my-reviews .chip')).to_have_text('जाँच में')
        check('edited review returns to pending', True)
        await cust.screenshot(path=S + 't-account.png', full_page=True)

        await cust.click('button:has-text("मेरा खाता हटाएँ")')
        await expect(cust.locator('.toast')).to_contain_text('हटा दिए गए')
        gone = await cust.evaluate("""async()=>{const {getFirebase}=await import('/assets/js/firebase.js');const {auth}=await getFirebase();return auth.currentUser===null}""")
        check('customer can delete own account', gone)
        await adm.goto(BASE + 'admin.html', wait_until='load')
        await expect(adm.locator('.stat').nth(1)).to_contain_text('0')
        users_left = '2' if OFFER_ON else '1'  # admin, plus the offer-limit test user (who keeps one booking)
        check('deleting account removes its reviews and profile', users_left in await adm.locator('.stat').nth(4).inner_text())
        check('deleting account removes its bookings', ('1' if OFFER_ON else '0') in await adm.locator('.stat').nth(0).inner_text())
        await pub.goto(BASE + 'privacy-hi.html', wait_until='load')
        check('privacy policy page renders', await pub.locator('h1').inner_text() == 'गोपनीयता नीति')

        # mobile screenshots
        mob = await new_page(browser, 390)
        await mob.goto(BASE + 'hi.html?emulator#reviews', wait_until='load')
        await mob.click('[data-account-button]')
        await mob.screenshot(path=S + 't-mobile-login.png')

        await csp_check(browser)
        for pg in (cust, adm, pub, mob):
            errs = [e for e in pg.errors if 'permission' not in e.lower() and 'Failed to load resource' not in e]
            check('no JS errors on ' + (pg.url.split('/')[-1] or 'index'), not errs, '; '.join(errs[:3]))
        await browser.close()
    failed = [n for n, ok in results if not ok]
    print(f'\n{len(results) - len(failed)}/{len(results)} passed')
    sys.exit(1 if failed else 0)

asyncio.run(main())
