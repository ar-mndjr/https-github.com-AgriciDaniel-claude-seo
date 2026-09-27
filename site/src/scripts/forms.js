// Sends every form with data-endpoint (contact, SEO audit, newsletter) to
// /contact.php on your hosting, which emails the submission to you.
document.querySelectorAll('form[data-endpoint]').forEach((form) => {
  const status = form.querySelector('.form-ok');
  const button = form.querySelector('button[type="submit"]');
  const say = (msg, ok = true) => {
    if (status) {
      status.textContent = msg;
      status.classList.toggle('error', !ok);
      status.classList.add('show');
    } else {
      // Compact forms (footer newsletter) report in the input itself
      const input = form.querySelector('input[type="email"]');
      input.value = '';
      input.placeholder = msg;
    }
  };

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!form.checkValidity()) {
      const bad = form.querySelector(':invalid');
      bad.reportValidity();
      bad.focus();
      return;
    }
    const data = new FormData(form);
    data.append('_kind', form.dataset.kind || 'contact');
    button && (button.disabled = true);
    try {
      const res = await fetch(form.dataset.endpoint, { method: 'POST', body: data, headers: { Accept: 'application/json' } });
      const json = await res.json().catch(() => ({}));
      if (!res.ok || !json.ok) throw new Error(json.error || 'send failed');
      form.reset();
      say(form.dataset.success || '✓ Thanks! Your message is on its way. We reply within 24 hours on business days.');
    } catch (err) {
      const email = form.dataset.fallback;
      say(`Sorry, that didn't send.${email ? ` Please email ${email} directly.` : ' Please try again.'}`, false);
    } finally {
      button && (button.disabled = false);
    }
  });
});
