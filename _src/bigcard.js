const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const dir = 'posts/big/png';
  fs.mkdirSync(dir, { recursive: true });
  const b = await chromium.launch({executablePath: process.env.PW_CHROMIUM || '/opt/pw-browsers/chromium'});
  const p = await b.newPage({ viewport: { width: 1200, height: 1500 }, deviceScaleFactor: 1 });
  await p.goto('file://' + process.cwd() + '/posts/big/index.html', { waitUntil: 'networkidle' });
  await p.waitForTimeout(900);
  const cards = await p.$$('.card');
  for (let i = 0; i < cards.length; i++) {
    const tag = await cards[i].getAttribute('data-tag');
    await cards[i].screenshot({ path: dir + '/' + tag + '.png' });
  }
  console.log('PNG ' + cards.length + '枚 → ' + dir + '/');
  await b.close();
})();
