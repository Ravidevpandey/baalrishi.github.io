"""End-to-end test against the Firebase emulators: signup, email verification, review, moderation,
admin reply and Firestore security rules.

Run: firebase emulators:exec --project demo-antarodaya --only auth,firestore "python3 tests/e2e.py"
while the site is served at http://localhost:8000 (python3 -m http.server 8000).
"""
import asyncio, json, os, sys, tempfile, urllib.request
from playwright.async_api import async_playwright, expect

S = os.environ.get('SCREENSHOT_DIR', tempfile.gettempdir()) + '/'
BASE = 'http://localhost:8000/'
PID = 'demo-antarodaya'
results = []

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
    ctx = await browser.new_context(viewport={'width': width, 'height': 900}, ignore_https_errors=os.environ.get('E2E_IGNORE_HTTPS_ERRORS') == '1')
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
        await expect(adm.locator('.stat').nth(1)).to_contain_text('1')
        check('admin sees 1 pending', True)
        check('admin sees 2 users', '2' in await adm.locator('.stat').nth(3).inner_text())
        await adm.screenshot(path=S + 't-admin-pending.png', full_page=True)
        await adm.click('.templates .chip-button >> nth=0')
        await adm.click('text=Save reply')
        await expect(adm.locator('.toast')).to_contain_text('Reply saved')
        await adm.click('button.success')
        await expect(adm.locator('.stat').nth(1)).to_contain_text('0')
        check('admin reply saved and review published', True)
        kept = await adm.evaluate("""async()=>{const {getFirebase}=await import('/assets/js/firebase.js');const {db,F}=await getFirebase();
          const s=await F.getDocs(F.query(F.collection(db,'reviews'),F.where('status','==','approved')));return s.docs.every(d=>!('expireAt' in d.data()))}""")
        check('published review has no expiry (kept)', kept)
        await adm.click('.tabs button >> nth=1')
        await adm.click('button[aria-pressed="false"]:has-text("Feature")')
        await expect(adm.locator('.chip.featured')).to_be_visible()
        check('admin can feature a review', True)
        await adm.click('.tabs button >> nth=4')
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
        r = await rules_probe(pub, "await F.getDocs(F.query(F.collection(db,'reviews'),F.where('status','==','pending')))")
        check('rules: public cannot read pending reviews', r == 'permission-denied', r)

        # customer edits → goes back to review
        await cust.goto(BASE + 'account-hi.html', wait_until='load')
        await expect(cust.locator('.my-reviews .chip')).to_have_text('प्रकाशित')
        check('customer sees published + reply', 'Thank you so much' in await cust.locator('.my-reviews').inner_text())
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
        await expect(adm.locator('.stat').nth(0)).to_contain_text('0')
        check('deleting account removes its reviews and profile', '1' in await adm.locator('.stat').nth(3).inner_text())
        await pub.goto(BASE + 'privacy-hi.html', wait_until='load')
        check('privacy policy page renders', await pub.locator('h1').inner_text() == 'गोपनीयता नीति')

        # mobile screenshots
        mob = await new_page(browser, 390)
        await mob.goto(BASE + 'hi.html?emulator#reviews', wait_until='load')
        await mob.click('[data-account-button]')
        await mob.screenshot(path=S + 't-mobile-login.png')

        for pg in (cust, adm, pub, mob):
            errs = [e for e in pg.errors if 'permission' not in e.lower() and 'Failed to load resource' not in e]
            check('no JS errors on ' + (pg.url.split('/')[-1] or 'index'), not errs, '; '.join(errs[:3]))
        await browser.close()
    failed = [n for n, ok in results if not ok]
    print(f'\n{len(results) - len(failed)}/{len(results)} passed')
    sys.exit(1 if failed else 0)

asyncio.run(main())
