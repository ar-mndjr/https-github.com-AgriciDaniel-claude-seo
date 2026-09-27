// Forms on inner pages (contact, SEO audit).
// The site is static, so a submitted form opens the visitor's email app with
// the message pre-filled, addressed to the form's data-mailto address.
// To receive submissions without an email app, point the form's `action` at a
// form service (Formspree, Netlify Forms, Basin…) and remove `data-mailto`.
document.querySelectorAll('form[data-mailto]').forEach(form => {
  const status = form.querySelector('.form-ok');

  form.addEventListener('submit', e => {
    e.preventDefault();

    // Built-in validation, shown on the first invalid field
    if (!form.checkValidity()) {
      const bad = form.querySelector(':invalid');
      bad.reportValidity();
      bad.focus();
      return;
    }

    // Collect answers; checkbox groups become comma-separated lists
    const answers = new Map();
    new FormData(form).forEach((value, key) => {
      value = String(value).trim();
      if (!value) return;
      answers.set(key, answers.has(key) ? answers.get(key) + ', ' + value : value);
    });
    const body = [...answers].map(([k, v]) => `${k}:\n${v}`).join('\n\n');

    const href = `mailto:${form.dataset.mailto}` +
      `?subject=${encodeURIComponent(form.dataset.subject || 'Website enquiry')}` +
      `&body=${encodeURIComponent(body)}`;
    window.location.href = href;

    if (status) {
      status.textContent = `✓ Your email app should open with your message ready to send. If it doesn't, email ${form.dataset.mailto} directly.`;
      status.classList.add('show');
    }
  });
});
