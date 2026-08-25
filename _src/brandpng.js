// brand/*.svg を、各SNSが求める大きさの PNG に書き出す
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT = 'brand/png';
fs.mkdirSync(OUT, { recursive: true });

// [元のSVG, 出力名, 幅, 高さ]
const JOBS = [
  // アイコン（各SNSの推奨サイズ）
  ['icon-blue',  'icon-x-400',            400, 400],   // X
  ['icon-blue',  'icon-instagram-320',    320, 320],   // Instagram
  ['icon-blue',  'icon-tiktok-200',       200, 200],   // TikTok
  ['icon-blue',  'icon-note-400',         400, 400],   // note
  ['icon-blue',  'icon-1000',            1000,1000],   // 予備の大サイズ
  ['icon-white', 'icon-white-1000',      1000,1000],
  ['icon-paper', 'icon-paper-1000',      1000,1000],
  ['icon-ink',   'icon-ink-1000',        1000,1000],
  ['icon-orange','icon-orange-1000',     1000,1000],
  // ヘッダー
  ['header-x',    'header-x-1500x500',   1500, 500],
  ['header-note', 'header-note-1280x670',1280, 670],
  ['header-note-wide', 'header-note-1920x1006', 1920, 1006],
  // 投稿テンプレ
  ['post-square',  'post-square-1080',   1080,1080],
  ['post-vertical','post-vertical-1080x1920', 1080,1920],
  // ロゴ
  ['logo-lockup-light', 'logo-lockup-light-1280',  1280, 320],
  ['logo-lockup-dark',  'logo-lockup-dark-1280',   1280, 320],
  ['logo-lockup-mono',  'logo-lockup-mono-1280',   1280, 320],
  ['logo-lockup-onblue','logo-lockup-onblue-1280', 1280, 320],
  ['logo-stack-light',  'logo-stack-light-960',     960, 588],
  ['logo-stack-dark',   'logo-stack-dark-960',      960, 588],
  ['logo-mark-blue',    'logo-mark-blue-512',       512, 512],
  ['logo-mark-white',   'logo-mark-white-512',      512, 512],
  ['logo-mark-ink',     'logo-mark-ink-512',        512, 512],
  ['logo-mark-orange',  'logo-mark-orange-512',     512, 512],
];

// 背景を透明にするもの（ロゴ本体）
const TRANSPARENT = /^logo-/;

(async () => {
  const b = await chromium.launch({executablePath: process.env.PW_CHROMIUM || '/opt/pw-browsers/chromium'});
  for (const [src, out, w, h] of JOBS) {
    const svg = fs.readFileSync(path.join('brand', src + '.svg'), 'utf8')
      .replace(/width="\d+"/, 'width="' + w + '"')
      .replace(/height="\d+"/, 'height="' + h + '"');
    const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    await p.setContent('<body style="margin:0;padding:0">' + svg + '</body>');
    await p.waitForTimeout(150);
    await p.screenshot({ path: path.join(OUT, out + '.png'),
                         omitBackground: TRANSPARENT.test(src) });
    await p.close();
  }
  await b.close();
  console.log('PNG ' + JOBS.length + '枚を書き出しました → ' + OUT + '/');
})();
