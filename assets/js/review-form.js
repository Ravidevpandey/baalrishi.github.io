// Write / edit review dialog, shared by the home page and the account page.
import { getFirebase, RETENTION_MS } from './firebase.js';
import { lang, T, errorText } from './i18n.js';
import { el, icon, modal, toast, siteData } from './ui.js';
import { requireUser, resendVerification, refreshUser } from './auth-ui.js';

function verifyPrompt() {
  const body = el('div', { class: 'modal-body' },
    el('p', {}, T.verifyNeeded),
    el('div', { class: 'button-row' },
      el('button', { type: 'button', class: 'button outline', onclick: () => resendVerification().catch(err => toast(errorText(err), 'error')) }, T.resendVerify),
      el('button', {
        type: 'button', class: 'button primary', onclick: async () => {
          const user = await refreshUser();
          dialog.close();
          if (user.emailVerified) openReviewForm();
        }
      }, T.iVerified)));
  const dialog = modal(T.writeTitle, body);
}

// existing: { id, rating, text, service, name } when editing. Resolves true when saved.
export async function openReviewForm(existing = null) {
  const user = await requireUser();
  if (!user) return false;
  if (!user.emailVerified) {
    verifyPrompt();
    return false;
  }
  const services = siteData().services || [];
  return new Promise(resolve => {
    let saved = false;
    const ratingHint = el('span', { class: 'rating-hint', 'aria-live': 'polite' });
    const starInputs = el('div', { class: 'star-input', role: 'radiogroup', 'aria-label': T.yourRating });
    for (let i = 1; i <= 5; i++) {
      const id = `rate-${i}`;
      starInputs.append(
        el('input', { type: 'radio', name: 'rating', value: i, id, checked: existing?.rating === i }),
        el('label', { for: id, title: T.ratingWords[i - 1], 'data-value': i }, icon('star'), el('span', { class: 'sr-only' }, `${i} – ${T.ratingWords[i - 1]}`)));
    }
    // Stars 1..N light up for the hovered or chosen rating (left to right = 1 to 5).
    const paint = value => starInputs.querySelectorAll('label').forEach(label => {
      label.classList.toggle('on', Number(label.dataset.value) <= value);
    });
    starInputs.addEventListener('mouseover', event => {
      const label = event.target.closest('label');
      if (label) paint(Number(label.dataset.value));
    });
    starInputs.addEventListener('mouseleave', () => paint(Number(starInputs.querySelector('input:checked')?.value || 0)));
    const count = el('small', { class: 'char-count' });
    const textarea = el('textarea', { name: 'text', rows: 5, maxlength: 1000, minlength: 10, required: true, placeholder: T.reviewPlaceholder });
    textarea.value = existing?.text || '';
    const select = el('select', { name: 'service' }, el('option', { value: '' }, T.serviceNone),
      services.map(s => el('option', { value: s.id, selected: existing?.service === s.id }, s.title)));
    const nameInput = el('input', { name: 'name', maxlength: 60, required: true, autocomplete: 'given-name' });
    nameInput.value = existing?.name || (user.displayName || '').split(' ')[0] || '';
    const error = el('p', { class: 'form-error', role: 'alert', hidden: true });
    const submit = el('button', { class: 'button primary block', type: 'submit' }, T.submit);
    const form = el('form', { class: 'review-form', novalidate: true },
      el('fieldset', { class: 'field' }, el('legend', {}, T.yourRating), el('div', { class: 'rating-row' }, starInputs, ratingHint)),
      el('label', { class: 'field' }, el('span', {}, T.yourReview), textarea, el('span', { class: 'field-foot' }, el('small', {}, T.privacyTip), count)),
      el('div', { class: 'field-pair' },
        el('label', { class: 'field' }, el('span', {}, T.displayName), nameInput, el('small', {}, T.displayNameHint)),
        el('label', { class: 'field' }, el('span', {}, T.service), select)),
      el('label', { class: 'check' }, el('input', { type: 'checkbox', name: 'consent', required: true, checked: Boolean(existing) }), el('span', {}, T.consent)),
      existing && el('p', { class: 'small-note' }, T.editNote),
      error, submit);

    const updateHint = () => {
      const value = Number(form.rating.value || 0);
      ratingHint.textContent = value ? T.ratingWords[value - 1] : '';
      paint(value);
    };
    const updateCount = () => { count.textContent = `${textarea.value.length}/1000`; };
    starInputs.addEventListener('change', updateHint);
    textarea.addEventListener('input', updateCount);
    updateHint();
    updateCount();

    const dialog = modal(existing ? T.editTitle : T.writeTitle, el('div', { class: 'modal-body' }, form), { wide: true });
    dialog.addEventListener('close', () => resolve(saved));

    form.addEventListener('submit', async event => {
      event.preventDefault();
      const rating = Number(form.rating.value || 0);
      const text = textarea.value.trim();
      const name = nameInput.value.trim();
      const problem = !rating ? T.chooseRating : text.length < 10 ? T.reviewTooShort : !name ? T.displayName : !form.consent.checked ? T.consentNeeded : '';
      if (problem) {
        error.textContent = problem;
        error.hidden = false;
        return;
      }
      error.hidden = true;
      submit.disabled = true;
      submit.textContent = T.submitting;
      try {
        const { db, F } = await getFirebase();
        const data = { name, rating, text, service: select.value, status: 'pending' };
        if (existing) {
          await F.updateDoc(F.doc(db, 'reviews', existing.id), { ...data, updatedAt: F.serverTimestamp() });
        } else {
          await F.addDoc(F.collection(db, 'reviews'), { ...data, uid: user.uid, lang, createdAt: F.serverTimestamp(), expireAt: F.Timestamp.fromMillis(Date.now() + RETENTION_MS) });
        }
        saved = true;
        toast(T.submitted);
        dialog.close();
      } catch (err) {
        error.textContent = errorText(err);
        error.hidden = false;
      } finally {
        submit.disabled = false;
        submit.textContent = T.submit;
      }
    });
  });
}
