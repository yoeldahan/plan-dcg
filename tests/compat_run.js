// Lance tests/compat.html dans Chromium (Playwright) et écrit le résultat + les erreurs de la console.
// Usage : node tests/compat_run.js <url> <fichier de sortie>   (utilisé par tests/compat.sh)
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [url, out] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errs = [];
  const keep = t => !/service worker|favicon|fetching the script|fonts\.g/i.test(t);
  page.on('console', m => { if (m.type() === 'error' && keep(m.text())) errs.push('CONSOLE ' + m.text()); });
  page.on('pageerror', e => errs.push('Uncaught ' + e.message));
  page.on('frameattached', f => {});
  browser.contexts()[0].on('page', () => {});
  await page.goto(url);
  let res = 'NO RESULT';
  try {
    await page.waitForFunction(() => /^(RESULT|REFUS|ERREUR)/.test(document.getElementById('out').textContent), null, { timeout: 30000 });
    const t = await page.textContent('#out');
    if (t.startsWith('RESULT ')) res = t.slice(7);
  } catch (e) { errs.push('TIMEOUT ' + e.message.split('\n')[0]); }
  fs.writeFileSync(out, res);
  fs.writeFileSync(out + '.err', errs.join('\n') + (errs.length ? '\n' : ''));
  await browser.close();
})();
