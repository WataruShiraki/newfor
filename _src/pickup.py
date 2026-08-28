# -*- coding: utf-8 -*-
"""ヘッダーの下に「ピックアップ」（直近の投票が流れる帯）を入れる

福利厚生JPで効果があった仕掛けを、NEWFORにも入れます。

置き方の決まり
- ページに入れるのは <script> 2行だけ。CSSも帯のHTMLも assets/pickup.js の中にあります
- 以前は全ページにCSSとHTMLを焼き込んでいたため、見た目を1文字直すだけで
  58ファイルを上げ直す必要がありました。触る場所は1本にします
- 何度実行しても二重には入りません

出すもの
- Supabase の newfor_recent_votes ビュー（3日ぶん・1時間単位に丸め済み）
- 投票がまだ無いとき、通信できないときは、帯ごと出しません。空の帯は出しません
"""
import io,os,re,glob,json,sys,importlib,hashlib

sys.path.insert(0,'articles')

# ── 記事スラッグ → 表示名の対応表を作る ──
MAP={}
for f in sorted(glob.glob('articles/a0*.py')):
    A=importlib.import_module(os.path.basename(f)[:-3]).A
    MAP[A['slug']]=dict(name=A.get('company') or 'NEWFOR',
                        url='/articles/%s/'%A['slug'])

# ── 今週の投票（weekly）には記事がない ──
#
# 「NEWFOR の記事に」と出てしまい、掲載企業の名前が消えていました。
# 投票の問い（question）の中から企業名を拾って、その企業ページへ送ります。
# 「NTTドコモ」は問いの中では「ドコモ」と書かれるので、短い呼び名も持ちます。
sys.path.insert(0,'companies')
CO=[]
for f in sorted(glob.glob('companies/*.py')):
    n=os.path.basename(f)[:-3]
    if n.startswith('_'): continue
    c=importlib.import_module(n).C
    keys=[c['name']]
    for cut in ('NTT','株式会社'):
        if c['name'].startswith(cut) and len(c['name'])>len(cut)+1:
            keys.append(c['name'][len(cut):])
    for cut in ('グループ','ホールディングス','自動車','工業','商事','重工業'):
        if c['name'].endswith(cut) and len(c['name'])>len(cut)+1:
            keys.append(c['name'][:-len(cut)])
    # 長い呼び名から先に照合する（「三菱商事」より先に「三菱」を当てない）
    CO.append(dict(name=c['name'],url='/companies/%s/'%c['slug'],
                   keys=sorted(set(keys),key=len,reverse=True)))

io.open('gh/assets/pickup-map.js','w',encoding='utf-8').write(
    '/* pickup.py が articles/ と companies/ から作ります。手で書かないでください */\n'
    'window.NF_PICKUP_MAP=%s;\n'
    'window.NF_PICKUP_CO=%s;\n'
    %(json.dumps(MAP,ensure_ascii=False,separators=(',',':')),
      json.dumps(CO,ensure_ascii=False,separators=(',',':'))))

# ── 帯のCSS。JSの中に持たせて、ページには入れない ──
CSSTEXT = "/* ピックアップの帯。ヘッダーのすぐ下に置きます。\n   ここは「人の気配」を出す場所なので、青ではなく差し色のオレンジで拾わせます。 */\n/* 帯の色は画面いっぱい。中身はそのページの .wrap と同じ幅にそろえる。\n   （ページごとに 1240px / 1180px / 760px と違うので、.wrap をそのまま借ります） */\n#nf-pickup{position:relative;overflow:hidden;\n background:linear-gradient(90deg,#FFF1E4 0%,#FFF7F0 60%,#FFF1E4 100%);\n border-bottom:1px solid rgba(224,74,12,.22);font-size:12.5px;line-height:1}\n#nf-pickup .nf-pk-in{display:flex;align-items:center;gap:12px;height:40px;\n flex-wrap:nowrap;min-height:0}\n#nf-pickup .nf-pk-tag{flex:0 0 auto;display:inline-flex;align-items:center;gap:6px;\n background:#E04A0C;color:#fff;font-weight:800;font-size:10.5px;\n letter-spacing:.12em;padding:6px 10px;border-radius:6px;box-shadow:0 1px 0 rgba(0,0,0,.06)}\n#nf-pickup .nf-pk-tag i{width:6px;height:6px;border-radius:50%;background:#fff;\n animation:nf-pk-blink 1.6s ease-in-out infinite}\n@keyframes nf-pk-blink{0%,100%{opacity:1}50%{opacity:.25}}\n#nf-pickup .nf-pk-win{position:relative;flex:1 1 auto;overflow:hidden;height:100%;\n -webkit-mask-image:linear-gradient(90deg,transparent 0,#000 24px,#000 calc(100% - 44px),transparent 100%);\n mask-image:linear-gradient(90deg,transparent 0,#000 24px,#000 calc(100% - 44px),transparent 100%)}\n#nf-pickup .nf-pk-track{display:flex;align-items:center;height:100%;width:max-content;\n animation:nf-pk-flow 40s linear infinite}\n#nf-pickup:hover .nf-pk-track{animation-play-state:paused}\n#nf-pickup .nf-pk-item{display:inline-flex;align-items:center;gap:8px;padding:0 20px;\n white-space:nowrap;text-decoration:none;color:#5A5368;border-radius:6px}\n/* カーソルを乗せたら、その1件まるごとに線を引く */\n#nf-pickup .nf-pk-item:hover{text-decoration:underline;text-decoration-color:rgba(224,74,12,.5);\n text-underline-offset:4px;text-decoration-thickness:1.5px;color:#2A2439}\n#nf-pickup .nf-pk-d{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:#B0A79E;\n border:1px solid rgba(224,74,12,.2);border-radius:4px;padding:2px 5px}\n#nf-pickup .nf-pk-w{color:#E04A0C;font-weight:800}\n#nf-pickup .nf-pk-t b{font-weight:700;color:#2A2439}\n#nf-pickup .nf-pk-n{background:#E04A0C;color:#fff;font-weight:800;font-size:10px;\n border-radius:9px;padding:2px 7px}\n/* 右から左へ流す。ニュースの帯はこの向きです。\n   うしろに同じ並びをもう一組置いてあるので、0 から -w へ動かすと\n   切れ目なく左へ流れ続けます */\n@keyframes nf-pk-flow{from{transform:translateX(0)}to{transform:translateX(calc(var(--nf-pk-w,1000px) * -1))}}\n@media (prefers-reduced-motion:reduce){\n  #nf-pickup .nf-pk-track{animation:none}\n  #nf-pickup .nf-pk-tag i{animation:none}\n  #nf-pickup .nf-pk-win{overflow-x:auto}\n}\nhtml[data-theme=\"dark\"] #nf-pickup,\n[data-theme=\"dark\"] #nf-pickup{background:#1B1526;border-bottom-color:rgba(255,138,69,.22)}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-item{color:#B6ADBF}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-item:hover{color:#F2ECF7}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-w{color:#FF8A45}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-t b{color:#EDE7F2}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-d{color:#8C8397;border-color:rgba(255,138,69,.24)}\n@media (max-width:640px){#nf-pickup{font-size:11.5px}\n  #nf-pickup .nf-pk-in{height:36px;gap:8px}\n  #nf-pickup .nf-pk-tag{font-size:9.5px;padding:5px 8px}\n  #nf-pickup .nf-pk-item{padding:0 14px;gap:6px}}"

JS = "/* ============================================================\n   NEWFOR ピックアップ（ヘッダー下を流れる、直近3日の投票）\n\n   読むのは newfor_recent_votes ビューだけです。\n   投票が無いとき・通信できないときは、帯ごと消します（空の帯は出さない）。\n   ============================================================ */\n(function () {\n  \"use strict\";\n  var NF_CSS = __NFCSS__;\n  var URL_ = \"https://jakwntemjkwqwaqujffh.supabase.co/rest/v1\";\n  var KEY  = \"sb_publishable_bQ84WCmRiFUbpPemMcO9xQ_Dj9Mh1mQ\";\n  /* 帯そのものを、ここで作ってヘッダーの下に差し込みます。\n     以前はCSSとHTMLを全ページに焼き込んでいたため、見た目を1文字直すだけで\n     58ファイルを上げ直す必要がありました。触る場所は、このファイル1本だけにします。 */\n  var header = document.querySelector(\"header\");\n  if (!header) return;\n  if (!document.getElementById(\"nf-pickup-css\")) {\n    var st = document.createElement(\"style\");\n    st.id = \"nf-pickup-css\";\n    st.textContent = NF_CSS;\n    document.head.appendChild(st);\n  }\n  var band = document.createElement(\"div\");\n  band.id = \"nf-pickup\";\n  band.hidden = true;\n  band.setAttribute(\"aria-label\", \"直近の投票\");\n  band.innerHTML = '<div class=\"wrap nf-pk-in\">' +\n    '<span class=\"nf-pk-tag\"><i></i>PICKUP</span>' +\n    '<div class=\"nf-pk-win\"><div class=\"nf-pk-track\"></div></div></div>';\n  header.parentNode.insertBefore(band, header.nextSibling);\n  var track = band.querySelector(\".nf-pk-track\");\n  var MAP = window.NF_PICKUP_MAP || {};\n\n  function die() { band.remove(); }\n\n  function md(iso) {                       /* 2026-08-05T10:00:00Z → 08-05 */\n    var d = new Date(iso);\n    if (isNaN(d)) return \"\";\n    var m = (\"0\" + (d.getMonth() + 1)).slice(-2), day = (\"0\" + d.getDate()).slice(-2);\n    return m + \"-\" + day;\n  }\n\n  var CO = window.NF_PICKUP_CO || [];\n\n  /* 今週の投票は、問いの文から掲載企業を拾う。見つからなければ企業名は出さない */\n  function fromQuestion(q) {\n    q = q || \"\";\n    var best = null;\n    CO.forEach(function (c) {\n      c.keys.forEach(function (k) {\n        if (q.indexOf(k) >= 0 && (!best || k.length > best.len)) best = { c: c, len: k.length };\n      });\n    });\n    return best ? best.c : null;\n  }\n\n  function line(r) {\n    var id = String(r.poll_id || \"\");\n    var n = Number(r.votes || 0);\n    var who, href;\n    if (id.indexOf(\"weekly-\") === 0) {\n      var c = fromQuestion(r.question);\n      who = c ? c.name : \"今週の投票\";\n      href = c ? c.url : \"/#vote\";\n    } else {\n      var m = MAP[id.replace(/^reaction-/, \"\")];\n      who = m ? m.name : \"NEWFOR\";\n      href = m ? m.url : \"/articles/\";\n    }\n    var a = document.createElement(\"a\");\n    a.className = \"nf-pk-item\";\n    a.href = href;\n    a.innerHTML = '<span class=\"nf-pk-d\">' + md(r.at) + '</span>' +\n                  '<span class=\"nf-pk-w\">' + who + '</span>' +\n                  '<span class=\"nf-pk-t\">に<b>「' + (r.label || \"\") + '」</b>が投票されました</span>' +\n                  (n > 1 ? '<span class=\"nf-pk-n\">' + n + '</span>' : '');\n    return a;\n  }\n\n  fetch(URL_ + \"/newfor_recent_votes?order=at.desc&limit=24\", {\n    headers: { apikey: KEY, Authorization: \"Bearer \" + KEY }\n  })\n  .then(function (r) { if (!r.ok) throw new Error(\"supabase \" + r.status); return r.json(); })\n  .then(function (rows) {\n    rows = (rows || []).filter(function (r) { return r.poll_id && r.label; });\n    if (!rows.length) return die();\n\n    var items = rows.map(line);\n    items.forEach(function (a) { track.appendChild(a); });\n\n    /* 流れが途切れないよう、同じ並びをもう一組うしろに足す */\n    items.forEach(function (a) { track.appendChild(a.cloneNode(true)); });\n\n    /* 先に見えるようにしてから測る。\n       隠れたままだと scrollWidth が 0 になり、動かない帯になります（実際になりました）。 */\n    band.hidden = false;\n    var w = track.scrollWidth / 2;\n    track.style.setProperty(\"--nf-pk-w\", w + \"px\");\n    track.style.animationDuration = Math.max(18, Math.round(w / 60)) + \"s\";\n  })\n  .catch(function (e) { console.warn(\"[NEWFOR pickup]\", e); die(); });\n})();\n"
JS = JS.replace('__NFCSS__', json.dumps(CSSTEXT, ensure_ascii=False))
io.open('gh/assets/pickup.js','w',encoding='utf-8').write(JS)
# ── ?v= のハッシュは、もう付けません ──
#
# JSの中身から作ったハッシュを付けていたころは、このファイルを1文字直すたびに
# ?v= が変わり、全1,300ページのHTMLまで書き換わっていました。
# 「触る場所は1本だけにする」という狙いが、そこで崩れていました。
# vercel.json で pickup.js は must-revalidate にしてあります。
# ファイルを差し替えれば、次のアクセスで新しいものが届きます。だから固定でよい。
VER = '1426e853'   # 以前のハッシュ値をそのまま引き継ぎます（HTMLを書き換えないため）

# ── ページに入れるのは、この2行だけ ──
BAND = ('\n<script src="/assets/pickup-map.js" defer></script>\n'
        '<script src="/assets/pickup.js?v=%s" defer></script>\n'%VER)

n=0
for f in sorted(set(glob.glob('gh/**/*.html',recursive=True))):
    if '/_src/' in f: continue
    s=io.open(f,encoding='utf-8').read()
    if '</header>' not in s: continue
    # 古い形（CSSと帯のHTMLを焼き込んでいたもの）も、新しい形も、いったん外す
    s=re.sub(r'\n?<style id="nf-pickup-css">.*?<script src="/assets/pickup\.js[^"]*" defer></script>\n?','',s,flags=re.S)
    s=re.sub(r'\n?<script src="/assets/pickup-map\.js" defer></script>\s*<script src="/assets/pickup\.js[^"]*" defer></script>\n?','',s,flags=re.S)
    i=s.find('</header>')+len('</header>')
    s=s[:i]+BAND+s[i:]
    io.open(f,'w',encoding='utf-8').write(s); n+=1
print('ピックアップを %d ページへ入れました（ページに入るのは<script>2行だけ）'%n)

# ═══════════════════════════════════════════════════════════════
# 調達診断への導線（全ページ共通）
#
# GA4で見ると、検索から来た方が最初に踏むのは記事・NEWS・企業ページです。
# ところがその3種類には、調達診断への入口が1つもありませんでした。
# 玄関（診断）へ橋を架けるのが、この部分の役目です。
#
# HTMLには手を入れません。1,300ページを書き換えずに、ここ1本を直せば
# 全ページに出ます。上のピックアップと同じ考え方です。
# ═══════════════════════════════════════════════════════════════
_KD = json.load(io.open('karte/site_data.json', encoding='utf-8'))
_NC = len(_KD['cases'])

GUIDE_CSS = (
 "#nf-sd{max-width:780px;margin:44px auto 10px;padding:0 22px;box-sizing:border-box}"
 "#nf-sd .nf-sd-in{background:linear-gradient(180deg,#FFF6EF 0%,#FFFBF7 100%);"
 "border:1px solid rgba(224,74,12,.28);border-radius:16px;padding:26px 24px;"
 "box-shadow:0 1px 2px rgba(24,20,40,.05),0 14px 34px -22px rgba(224,74,12,.55)}"
 "#nf-sd .nf-sd-k{display:block;font-family:ui-monospace,Menlo,monospace;font-size:10.5px;"
 "letter-spacing:.14em;color:#C63E08;font-weight:800}"
 "#nf-sd .nf-sd-t{margin:10px 0 10px;font-size:clamp(18px,2.4vw,23px);font-weight:850;"
 "letter-spacing:-.03em;line-height:1.55;color:#0C0A16}"
 "#nf-sd .nf-sd-d{margin:0 0 18px;font-size:14.5px;line-height:1.95;color:#403C55}"
 "#nf-sd .nf-sd-b{display:inline-flex;align-items:center;gap:8px;background:#E8490F;color:#fff;"
 "font-weight:800;font-size:15px;padding:14px 26px;border-radius:12px;text-decoration:none;"
 "box-shadow:0 10px 24px -12px rgba(232,73,15,.9)}"
 "#nf-sd .nf-sd-b:hover{background:#C63E08}"
 "#nf-sd .nf-sd-f{display:block;margin-top:13px;font-size:12.5px;color:#57536D;font-weight:600}"
 "#nf-sd .nf-sd-f b{color:#C63E08;font-size:14px}"
 'html[data-theme="dark"] #nf-sd .nf-sd-in,[data-theme="dark"] #nf-sd .nf-sd-in'
 "{background:linear-gradient(180deg,#1C1622 0%,#141019 100%);border-color:rgba(255,106,43,.34)}"
 '[data-theme="dark"] #nf-sd .nf-sd-t{color:#F5F5F8}'
 '[data-theme="dark"] #nf-sd .nf-sd-d{color:#CBCBD6}'
 '[data-theme="dark"] #nf-sd .nf-sd-k{color:#FF6A2B}'
 '[data-theme="dark"] #nf-sd .nf-sd-f{color:#95959F}'
 '[data-theme="dark"] #nf-sd .nf-sd-f b{color:#FF6A2B}'
 "@media(max-width:640px){#nf-sd .nf-sd-in{padding:22px 18px}#nf-sd .nf-sd-b{width:100%;justify-content:center}}"
)

GUIDE_JS = r'''
/* ============================================================
   NEWFOR ─ 調達診断への導線

   置く場所は2つ。ヘッダーのナビと、本文の終わりです。
   記事・NEWS・企業ページから、玄関（診断）へ橋を架けます。
   HTMLは1枚も書き換えません。直すのは、このファイル1本だけです。
   ============================================================ */
(function () {
  "use strict";
  var P = location.pathname;
  if (P.indexOf("/shindan") === 0) return;          /* 診断の中では出しません */

  function ev(name, from) {
    if (typeof gtag === "function") { try { gtag("event", name, { from: from }); } catch (e) {} }
  }

  /* ── 1. ヘッダーのナビに「調達診断」を足す ── */
  var nav = document.querySelector("header nav.main") || document.querySelector("header nav");
  if (nav && !nav.querySelector('a[href="/shindan/"]')) {
    var na = document.createElement("a");
    na.href = "/shindan/";
    na.textContent = "調達診断";
    na.addEventListener("click", function () { ev("shindan_guide_click", "nav"); });
    var co = nav.querySelector('a[href="/companies/"]');
    if (co && co.parentNode === nav) nav.insertBefore(na, co.nextSibling);
    else nav.appendChild(na);
  }

  /* トップページには、すでに大きな帯があります */
  if (P === "/" || P === "/index.html") return;

  /* ── 2. 本文の終わりに、診断への1枚を置く ── */
  var foot = document.querySelector("footer");
  if (!foot || document.getElementById("nf-sd")) return;

  /* 読んでいたものに合わせて、最初の一文だけ変えます */
  var lead = "先に道を通った経営者の記録を、いま読んでいただきました。";
  if (P.indexOf("/articles/") === 0)      lead = "先人が通った道を、いま読んでいただきました。";
  else if (P.indexOf("/news/") === 0)     lead = "この1件を、いま読んでいただきました。";
  else if (P.indexOf("/companies/") === 0) lead = "1社の年表を、いま見ていただきました。";

  var st = document.createElement("style");
  st.id = "nf-sd-css";
  st.textContent = __GUIDECSS__;
  document.head.appendChild(st);

  var box = document.createElement("div");
  box.id = "nf-sd";
  box.innerHTML =
    '<div class="nf-sd-in">' +
      '<span class="nf-sd-k">NEWFOR ／ スタートアップ調達診断</span>' +
      '<p class="nf-sd-t">その資金調達は、あなたに向いていますか。</p>' +
      '<p class="nf-sd-d">' + lead +
        'つぎは、あなたの番です。向いているかどうか、やるなら、いま何が足りないか。' +
        '先に道を通った経営者__NC__人の記録から、あなたに近いものを探してお返しします。</p>' +
      '<a class="nf-sd-b" href="/shindan/">3分の診断をはじめる →</a>' +
      '<span class="nf-sd-f"><b>3分</b>・全<b>18</b>問・登録なし　/　先人の記録<b>__NC__</b>件</span>' +
    '</div>';
  foot.parentNode.insertBefore(box, foot);

  box.querySelector(".nf-sd-b").addEventListener("click", function () {
    ev("shindan_guide_click", P.split("/")[1] || "other");
  });
})();
'''
GUIDE_JS = GUIDE_JS.replace('__GUIDECSS__', json.dumps(GUIDE_CSS, ensure_ascii=False))
GUIDE_JS = GUIDE_JS.replace('__NC__', str(_NC))
io.open('gh/assets/pickup.js', 'a', encoding='utf-8').write(GUIDE_JS)
print('診断への導線を pickup.js に足しました（先人の記録 %d件）' % _NC)
