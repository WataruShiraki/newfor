// 全ページぶんのOGP画像（1200×630）を作る
//
// 中身は ogspec.py が実データから組み立てた /tmp/ogspec.json を読みます。
// ここに文言を手で書かないでください。数が古いまま残り、SNSに貼ったときだけ
// 「12社226事業」のような古い数字が出ます（実際にそうなっていました）。
const { chromium } = require('playwright');
const fs = require('fs');

const UFO='<path d="M10.6 16.4 L21.4 16.4 L25.8 31 L6.2 31 Z" fill="currentColor" opacity=".16"/><path d="M12.5 16.4 L19.5 16.4 L21.9 26.5 L10.1 26.5 Z" fill="currentColor" opacity=".24"/><ellipse cx="16" cy="15.4" rx="12.6" ry="4.4" fill="currentColor"/><path d="M9.7 13.4C10.4 9.2 12.9 6.5 16 6.5s5.6 2.7 6.3 6.9" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" fill="none"/>';

const PAGES = JSON.parse(fs.readFileSync('/tmp/ogspec.json', 'utf8'));

// 見出しの最長行と行数から、はみ出さない字の大きさを選ぶ
function fit(title) {
  const lines = title.split('<br>');
  const max = Math.max(...lines.map(l => l.replace(/<[^>]+>/g, '').length));
  let size = 62;
  if (max > 14) size = 56;
  if (max > 16) size = 50;
  if (max > 19) size = 44;
  if (max > 22) size = 39;
  if (lines.length >= 3) size = Math.min(size, 46);
  return size;
}

const tpl = (p) => `<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0}
body{width:1200px;height:630px;overflow:hidden;position:relative;
 background:linear-gradient(160deg,#2730CE 0%,#2F3BD6 52%,#3843E6 100%);
 font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP",sans-serif;color:#fff;
 -webkit-font-smoothing:antialiased}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.055) 1px,transparent 1px);background-size:76px 76px}
.ufo{position:absolute;right:-70px;bottom:-90px;width:520px;color:#fff;opacity:.13}
.in{position:relative;padding:60px 72px;height:100%;display:flex;flex-direction:column}
.brand{display:flex;align-items:center;gap:13px}
.brand svg{width:46px;height:46px;color:#fff}
.wm{font-family:ui-monospace,Menlo,monospace;font-size:27px;font-weight:800;letter-spacing:.17em}
.wm b{color:#FF8A45}
.eye{margin-top:auto;font-family:ui-monospace,Menlo,monospace;font-size:19px;letter-spacing:.15em;color:#FFB489;font-weight:700}
h1{margin:16px 0 0;font-size:${fit(p.title)}px;line-height:1.3;letter-spacing:-.035em;font-weight:850}
.sub{margin-top:20px;font-size:23px;color:rgba(255,255,255,.9);line-height:1.6;letter-spacing:-.01em}
.bar{margin-top:26px;height:8px;width:150px;background:#FF5A14;border-radius:99px}
.url{position:absolute;right:72px;bottom:50px;font-family:ui-monospace,Menlo,monospace;
 font-size:20px;font-weight:700;color:rgba(255,255,255,.6);letter-spacing:.08em}
</style></head><body>
<div class="grid"></div>
<svg class="ufo" viewBox="0 0 32 32" fill="none">${UFO}</svg>
<div class="in">
 <div class="brand"><svg viewBox="0 0 32 32" fill="none">${UFO}</svg><span class="wm">NEW<b>FOR</b></span></div>
 <div class="eye">${p.eyebrow}</div>
 <h1>${p.title}</h1>
 <div class="sub">${p.sub}</div>
 <div class="bar"></div>
</div>
<div class="url">newfor.jp</div>
</body></html>`;

(async () => {
  const b = await chromium.launch({executablePath: process.env.PW_CHROMIUM || '/opt/pw-browsers/chromium'});
  const pg = await b.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  for (const p of PAGES) {
    await pg.setContent(tpl(p));
    await pg.waitForTimeout(60);
    await pg.screenshot({ path: 'dist/assets/' + p.f });
  }
  await pg.close();
  await b.close();
  console.log('OGP画像 ' + PAGES.length + '枚を書き出しました → dist/assets/');
})();
