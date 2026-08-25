// posts/img/*.svg を PNG にする（postimg.py が書いた jobs.json のとおりに）
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SRC = 'posts/img';
const OUT = 'posts/img/png';
fs.mkdirSync(OUT, { recursive: true });

const JOBS = JSON.parse(fs.readFileSync(path.join(SRC, 'jobs.json'), 'utf8'));

(async () => {
  const b = await chromium.launch({executablePath: process.env.PW_CHROMIUM || '/opt/pw-browsers/chromium'});
  for (const [name, w, h] of JOBS) {
    const svg = fs.readFileSync(path.join(SRC, name + '.svg'), 'utf8');
    const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    await p.setContent('<body style="margin:0;padding:0">' + svg + '</body>');
    await p.waitForTimeout(120);
    await p.screenshot({ path: path.join(OUT, name + '.png') });
    await p.close();
  }
  await b.close();
  console.log('PNG ' + JOBS.length + '枚を書き出しました → ' + OUT + '/');
})();
