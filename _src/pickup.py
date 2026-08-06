# -*- coding: utf-8 -*-
"""ヘッダーの下に「ピックアップ」（直近の投票が流れる帯）を入れる

福利厚生JPで効果があった仕掛けを、NEWFORにも入れます。

置き方の決まり
- 帯のHTMLとCSSとスクリプトは、全ページの </header> の直後に入れます
- 生成元が6つに分かれているので、ここでまとめて入れます（analytics.py と同じやり方）
- 何度実行しても二重には入りません

出すもの
- Supabase の newfor_recent_votes ビュー（3日ぶん・1時間単位に丸め済み）
- 投票がまだ無いとき、通信できないときは、帯ごと隠します。空の帯は出しません
"""
import io,os,re,glob,json,sys,importlib

sys.path.insert(0,'articles')

# ── 記事スラッグ → 表示名の対応表を作る ──
MAP={}
for f in sorted(glob.glob('articles/a0*.py')):
    A=importlib.import_module(os.path.basename(f)[:-3]).A
    MAP[A['slug']]=dict(
        name=A.get('company') or 'NEWFOR',
        url='/articles/%s/'%A['slug'])

MAPJS=('/* 記事スラッグ → 会社名。pickup.py が articles/ から作ります */\n'
       'window.NF_PICKUP_MAP=%s;\n'%json.dumps(MAP,ensure_ascii=False,separators=(',',':')))
io.open('gh/assets/pickup-map.js','w',encoding='utf-8').write(MAPJS)

JS=r'''/* ============================================================
   NEWFOR ピックアップ（ヘッダー下を流れる、直近3日の投票）

   読むのは newfor_recent_votes ビューだけです。
   投票が無いとき・通信できないときは、帯ごと消します（空の帯は出さない）。
   ============================================================ */
(function () {
  "use strict";
  var URL_ = "https://jakwntemjkwqwaqujffh.supabase.co/rest/v1";
  var KEY  = "sb_publishable_bQ84WCmRiFUbpPemMcO9xQ_Dj9Mh1mQ";
  var band = document.getElementById("nf-pickup");
  if (!band) return;
  var track = band.querySelector(".nf-pk-track");
  var MAP = window.NF_PICKUP_MAP || {};

  function die() { band.remove(); }

  function md(iso) {                       /* 2026-08-05T10:00:00Z → 08-05 */
    var d = new Date(iso);
    if (isNaN(d)) return "";
    var m = ("0" + (d.getMonth() + 1)).slice(-2), day = ("0" + d.getDate()).slice(-2);
    return m + "-" + day;
  }

  function line(r) {
    var slug = String(r.poll_id || "").replace(/^reaction-/, "").replace(/^weekly-.*/, "");
    var m = MAP[slug];
    var who = m ? m.name : "NEWFOR";
    var href = m ? m.url : "/articles/";
    var n = Number(r.votes || 0);
    var tail = n > 1 ? "と" + n + "人が投票しました。" : "と投票がありました。";
    var a = document.createElement("a");
    a.className = "nf-pk-item";
    a.href = href;
    a.innerHTML = '<span class="nf-pk-d">・' + md(r.at) + '</span>' +
                  '<span class="nf-pk-w">' + who + '</span>' +
                  '<span class="nf-pk-t">の記事に「' + (r.label || "") + '」' + tail + '</span>';
    return a;
  }

  fetch(URL_ + "/newfor_recent_votes?order=at.desc&limit=24", {
    headers: { apikey: KEY, Authorization: "Bearer " + KEY }
  })
  .then(function (r) { if (!r.ok) throw new Error("supabase " + r.status); return r.json(); })
  .then(function (rows) {
    rows = (rows || []).filter(function (r) { return r.poll_id && r.label; });
    if (!rows.length) return die();

    var items = rows.map(line);
    items.forEach(function (a) { track.appendChild(a); });

    /* 流れが途切れないよう、同じ並びをもう一組うしろに足す */
    items.forEach(function (a) { track.appendChild(a.cloneNode(true)); });

    /* 中身の長さに合わせて、速さを決める（1秒あたり60pxくらい） */
    var w = track.scrollWidth / 2;
    track.style.setProperty("--nf-pk-w", w + "px");
    track.style.animationDuration = Math.max(18, Math.round(w / 60)) + "s";
    band.hidden = false;
  })
  .catch(function (e) { console.warn("[NEWFOR pickup]", e); die(); });
})();
'''
io.open('gh/assets/pickup.js','w',encoding='utf-8').write(JS)

CSS='''<style id="nf-pickup-css">
/* ピックアップの帯。ヘッダーのすぐ下に置きます */
#nf-pickup{position:relative;overflow:hidden;background:#FFF3EA;border-bottom:1px solid rgba(224,74,12,.16);
 display:flex;align-items:center;gap:14px;height:38px;padding-left:14px;font-size:12.5px;line-height:1}
#nf-pickup .nf-pk-tag{flex:0 0 auto;background:#E04A0C;color:#fff;font-weight:800;font-size:10.5px;
 letter-spacing:.12em;padding:5px 9px;border-radius:5px}
#nf-pickup .nf-pk-win{position:relative;flex:1 1 auto;overflow:hidden;height:100%;
 -webkit-mask-image:linear-gradient(90deg,transparent 0,#000 26px,#000 calc(100% - 42px),transparent 100%);
 mask-image:linear-gradient(90deg,transparent 0,#000 26px,#000 calc(100% - 42px),transparent 100%)}
#nf-pickup .nf-pk-track{display:flex;align-items:center;height:100%;width:max-content;
 animation:nf-pk-flow 40s linear infinite}
#nf-pickup:hover .nf-pk-track{animation-play-state:paused}
#nf-pickup .nf-pk-item{display:inline-flex;align-items:center;gap:7px;padding:0 22px;
 white-space:nowrap;text-decoration:none;color:#57536D}
#nf-pickup .nf-pk-item:hover .nf-pk-w{text-decoration:underline}
#nf-pickup .nf-pk-d{font-family:ui-monospace,Menlo,monospace;font-size:11.5px;color:#9A93AE}
#nf-pickup .nf-pk-w{color:#2F3BD6;font-weight:700}
@keyframes nf-pk-flow{from{transform:translateX(0)}to{transform:translateX(calc(var(--nf-pk-w,1000px) * -1))}}
@media (prefers-reduced-motion:reduce){
  #nf-pickup .nf-pk-track{animation:none}
  #nf-pickup .nf-pk-win{overflow-x:auto}
}
html[data-theme="dark"] #nf-pickup,
[data-theme="dark"] #nf-pickup{background:#171525;border-bottom-color:rgba(255,255,255,.08)}
[data-theme="dark"] #nf-pickup .nf-pk-item{color:#A9A3BC}
[data-theme="dark"] #nf-pickup .nf-pk-w{color:#9AA6FF}
@media (max-width:640px){#nf-pickup{height:34px;font-size:11.5px}
  #nf-pickup .nf-pk-tag{font-size:9.5px;padding:4px 7px}}
</style>'''

BAND=('\n%s\n<div id="nf-pickup" hidden aria-label="直近の投票">'
      '<span class="nf-pk-tag">PICKUP</span>'
      '<div class="nf-pk-win"><div class="nf-pk-track"></div></div></div>\n'
      '<script src="/assets/pickup-map.js" defer></script>\n'
      '<script src="/assets/pickup.js" defer></script>\n'%CSS)

n=0
for f in sorted(set(glob.glob('gh/**/*.html',recursive=True))):
    if '/_src/' in f: continue
    s=io.open(f,encoding='utf-8').read()
    if '</header>' not in s: continue
    # すでに入っていれば、いったん外してから入れ直す（中身の更新のため）
    s=re.sub(r'\n?<style id="nf-pickup-css">.*?<script src="/assets/pickup\.js" defer></script>\n?','',s,flags=re.S)
    i=s.find('</header>')+len('</header>')
    s=s[:i]+BAND+s[i:]
    io.open(f,'w',encoding='utf-8').write(s); n+=1
print('ピックアップの帯を %d ページへ入れました'%n)
