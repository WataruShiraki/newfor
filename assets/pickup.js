/* ============================================================
   NEWFOR ピックアップ（ヘッダー下を流れる、直近3日の投票）

   読むのは newfor_recent_votes ビューだけです。
   投票が無いとき・通信できないときは、帯ごと消します（空の帯は出さない）。
   ============================================================ */
(function () {
  "use strict";
  var NF_CSS = "/* ピックアップの帯。ヘッダーのすぐ下に置きます。\n   ここは「人の気配」を出す場所なので、青ではなく差し色のオレンジで拾わせます。 */\n/* 帯の色は画面いっぱい。中身はそのページの .wrap と同じ幅にそろえる。\n   （ページごとに 1240px / 1180px / 760px と違うので、.wrap をそのまま借ります） */\n#nf-pickup{position:relative;overflow:hidden;\n background:linear-gradient(90deg,#FFF1E4 0%,#FFF7F0 60%,#FFF1E4 100%);\n border-bottom:1px solid rgba(224,74,12,.22);font-size:12.5px;line-height:1}\n#nf-pickup .nf-pk-in{display:flex;align-items:center;gap:12px;height:40px;\n flex-wrap:nowrap;min-height:0}\n#nf-pickup .nf-pk-tag{flex:0 0 auto;display:inline-flex;align-items:center;gap:6px;\n background:#E04A0C;color:#fff;font-weight:800;font-size:10.5px;\n letter-spacing:.12em;padding:6px 10px;border-radius:6px;box-shadow:0 1px 0 rgba(0,0,0,.06)}\n#nf-pickup .nf-pk-tag i{width:6px;height:6px;border-radius:50%;background:#fff;\n animation:nf-pk-blink 1.6s ease-in-out infinite}\n@keyframes nf-pk-blink{0%,100%{opacity:1}50%{opacity:.25}}\n#nf-pickup .nf-pk-win{position:relative;flex:1 1 auto;overflow:hidden;height:100%;\n -webkit-mask-image:linear-gradient(90deg,transparent 0,#000 24px,#000 calc(100% - 44px),transparent 100%);\n mask-image:linear-gradient(90deg,transparent 0,#000 24px,#000 calc(100% - 44px),transparent 100%)}\n#nf-pickup .nf-pk-track{display:flex;align-items:center;height:100%;width:max-content;\n animation:nf-pk-flow 40s linear infinite}\n#nf-pickup:hover .nf-pk-track{animation-play-state:paused}\n#nf-pickup .nf-pk-item{display:inline-flex;align-items:center;gap:8px;padding:0 20px;\n white-space:nowrap;text-decoration:none;color:#5A5368;border-radius:6px}\n/* カーソルを乗せたら、その1件まるごとに線を引く */\n#nf-pickup .nf-pk-item:hover{text-decoration:underline;text-decoration-color:rgba(224,74,12,.5);\n text-underline-offset:4px;text-decoration-thickness:1.5px;color:#2A2439}\n#nf-pickup .nf-pk-d{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:#B0A79E;\n border:1px solid rgba(224,74,12,.2);border-radius:4px;padding:2px 5px}\n#nf-pickup .nf-pk-w{color:#E04A0C;font-weight:800}\n#nf-pickup .nf-pk-t b{font-weight:700;color:#2A2439}\n#nf-pickup .nf-pk-n{background:#E04A0C;color:#fff;font-weight:800;font-size:10px;\n border-radius:9px;padding:2px 7px}\n/* 右から左へ流す。ニュースの帯はこの向きです。\n   うしろに同じ並びをもう一組置いてあるので、0 から -w へ動かすと\n   切れ目なく左へ流れ続けます */\n@keyframes nf-pk-flow{from{transform:translateX(0)}to{transform:translateX(calc(var(--nf-pk-w,1000px) * -1))}}\n@media (prefers-reduced-motion:reduce){\n  #nf-pickup .nf-pk-track{animation:none}\n  #nf-pickup .nf-pk-tag i{animation:none}\n  #nf-pickup .nf-pk-win{overflow-x:auto}\n}\nhtml[data-theme=\"dark\"] #nf-pickup,\n[data-theme=\"dark\"] #nf-pickup{background:#1B1526;border-bottom-color:rgba(255,138,69,.22)}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-item{color:#B6ADBF}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-item:hover{color:#F2ECF7}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-w{color:#FF8A45}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-t b{color:#EDE7F2}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-d{color:#8C8397;border-color:rgba(255,138,69,.24)}\n@media (max-width:640px){#nf-pickup{font-size:11.5px}\n  #nf-pickup .nf-pk-in{height:36px;gap:8px}\n  #nf-pickup .nf-pk-tag{font-size:9.5px;padding:5px 8px}\n  #nf-pickup .nf-pk-item{padding:0 14px;gap:6px}}";
  var URL_ = "https://jakwntemjkwqwaqujffh.supabase.co/rest/v1";
  var KEY  = "sb_publishable_bQ84WCmRiFUbpPemMcO9xQ_Dj9Mh1mQ";
  /* 帯そのものを、ここで作ってヘッダーの下に差し込みます。
     以前はCSSとHTMLを全ページに焼き込んでいたため、見た目を1文字直すだけで
     58ファイルを上げ直す必要がありました。触る場所は、このファイル1本だけにします。 */
  var header = document.querySelector("header");
  if (!header) return;
  if (!document.getElementById("nf-pickup-css")) {
    var st = document.createElement("style");
    st.id = "nf-pickup-css";
    st.textContent = NF_CSS;
    document.head.appendChild(st);
  }
  var band = document.createElement("div");
  band.id = "nf-pickup";
  band.hidden = true;
  band.setAttribute("aria-label", "直近の投票");
  band.innerHTML = '<div class="wrap nf-pk-in">' +
    '<span class="nf-pk-tag"><i></i>PICKUP</span>' +
    '<div class="nf-pk-win"><div class="nf-pk-track"></div></div></div>';
  header.parentNode.insertBefore(band, header.nextSibling);
  var track = band.querySelector(".nf-pk-track");
  var MAP = window.NF_PICKUP_MAP || {};

  function die() { band.remove(); }

  function md(iso) {                       /* 2026-08-05T10:00:00Z → 08-05 */
    var d = new Date(iso);
    if (isNaN(d)) return "";
    var m = ("0" + (d.getMonth() + 1)).slice(-2), day = ("0" + d.getDate()).slice(-2);
    return m + "-" + day;
  }

  var CO = window.NF_PICKUP_CO || [];

  /* 今週の投票は、問いの文から掲載企業を拾う。見つからなければ企業名は出さない */
  function fromQuestion(q) {
    q = q || "";
    var best = null;
    CO.forEach(function (c) {
      c.keys.forEach(function (k) {
        if (q.indexOf(k) >= 0 && (!best || k.length > best.len)) best = { c: c, len: k.length };
      });
    });
    return best ? best.c : null;
  }

  function line(r) {
    var id = String(r.poll_id || "");
    var n = Number(r.votes || 0);
    var who, href;
    if (id.indexOf("weekly-") === 0) {
      var c = fromQuestion(r.question);
      who = c ? c.name : "今週の投票";
      href = c ? c.url : "/#vote";
    } else {
      var m = MAP[id.replace(/^reaction-/, "")];
      who = m ? m.name : "NEWFOR";
      href = m ? m.url : "/articles/";
    }
    var a = document.createElement("a");
    a.className = "nf-pk-item";
    a.href = href;
    a.innerHTML = '<span class="nf-pk-d">' + md(r.at) + '</span>' +
                  '<span class="nf-pk-w">' + who + '</span>' +
                  '<span class="nf-pk-t">に<b>「' + (r.label || "") + '」</b>が投票されました</span>' +
                  (n > 1 ? '<span class="nf-pk-n">' + n + '</span>' : '');
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

    /* 先に見えるようにしてから測る。
       隠れたままだと scrollWidth が 0 になり、動かない帯になります（実際になりました）。 */
    band.hidden = false;
    var w = track.scrollWidth / 2;
    track.style.setProperty("--nf-pk-w", w + "px");
    track.style.animationDuration = Math.max(18, Math.round(w / 60)) + "s";
  })
  .catch(function (e) { console.warn("[NEWFOR pickup]", e); die(); });
})();

/* ============================================================
   NEWFOR ─ 読み終えた方への「次の一歩」

   置く場所は2つ。ヘッダーのナビと、本文の終わりです。
   向ける先は「新規事業の言葉」。調達診断は、同じカードの
   いちばん下に小さく1行だけ残しています。
   HTMLは1枚も書き換えません。直すのは、このファイル1本だけです。
   ============================================================ */
(function () {
  "use strict";
  var P = location.pathname;
  if (P.indexOf("/shindan") === 0) return;          /* 診断の中では出しません */
  if (P.indexOf("/words") === 0) return;            /* 用語集の中では出しません */

  function ev(name, from) {
    if (typeof gtag === "function") { try { gtag("event", name, { from: from }); } catch (e) {} }
  }

  /* ── 1. ヘッダーのナビに「用語集」を足す ── */
  var nav = document.querySelector("header nav.main") || document.querySelector("header nav");
  if (nav && !nav.querySelector('a[href="/words/"]')) {
    var na = document.createElement("a");
    na.href = "/words/";
    na.textContent = "用語集";
    na.addEventListener("click", function () { ev("words_guide_click", "nav"); });
    var co = nav.querySelector('a[href="/companies/"]');
    if (co && co.parentNode === nav) nav.insertBefore(na, co.nextSibling);
    else nav.appendChild(na);
  }

  /* トップページには、すでに大きな帯があります */
  if (P === "/" || P === "/index.html") return;

  /* ── 2. 本文の終わりに、次の一歩を1枚置く ── */
  var foot = document.querySelector("footer");
  if (!foot || document.getElementById("nf-nb")) return;

  /* 読んでいたものに合わせて、最初の一文だけ変えます */
  var lead = "先に進んだ人の記録を、いま読んでいただきました。";
  if (P.indexOf("/articles/") === 0)       lead = "1社の年表を、いま読んでいただきました。";
  else if (P.indexOf("/news/") === 0)      lead = "この1件を、いま読んでいただきました。";
  else if (P.indexOf("/companies/") === 0) lead = "1社の記録を、いま見ていただきました。";

  var st = document.createElement("style");
  st.id = "nf-nb-css";
  st.textContent = "#nf-nb{max-width:780px;margin:44px auto 10px;padding:0 22px;box-sizing:border-box}#nf-nb .nf-nb-in{background:linear-gradient(180deg,#F1F2FE 0%,#FAFAFF 100%);border:1px solid rgba(47,59,214,.26);border-radius:16px;padding:26px 24px;box-shadow:0 1px 2px rgba(24,20,40,.05),0 14px 34px -22px rgba(47,59,214,.55)}#nf-nb .nf-nb-k{display:block;font-family:ui-monospace,Menlo,monospace;font-size:10.5px;letter-spacing:.14em;color:#2F3BD6;font-weight:800}#nf-nb .nf-nb-t{margin:10px 0 10px;font-size:clamp(18px,2.4vw,23px);font-weight:850;letter-spacing:-.03em;line-height:1.55;color:#0C0A16}#nf-nb .nf-nb-d{margin:0 0 18px;font-size:14.5px;line-height:1.95;color:#403C55}#nf-nb .nf-nb-b{display:inline-flex;align-items:center;gap:8px;background:#2F3BD6;color:#fff;font-weight:800;font-size:15px;padding:14px 26px;border-radius:12px;text-decoration:none;box-shadow:0 10px 24px -12px rgba(47,59,214,.9)}#nf-nb .nf-nb-b:hover{background:#212DBE}#nf-nb .nf-nb-s{display:block;margin-top:14px;font-size:13.5px;color:#403C55;font-weight:600}#nf-nb .nf-nb-s a{color:#2F3BD6;font-weight:800;text-decoration:none;margin-right:16px}#nf-nb .nf-nb-s a:hover{text-decoration:underline}#nf-nb .nf-nb-x{display:block;margin-top:16px;padding-top:14px;border-top:1px solid rgba(18,14,38,.12);font-size:12.5px;line-height:1.9;color:#57536D}#nf-nb .nf-nb-x a{color:#C63E08;font-weight:800;text-decoration:none}#nf-nb .nf-nb-x a:hover{text-decoration:underline}html[data-theme=\"dark\"] #nf-nb .nf-nb-in,[data-theme=\"dark\"] #nf-nb .nf-nb-in{background:linear-gradient(180deg,#15161F 0%,#101018 100%);border-color:rgba(124,140,255,.32)}[data-theme=\"dark\"] #nf-nb .nf-nb-t{color:#F5F5F8}[data-theme=\"dark\"] #nf-nb .nf-nb-d{color:#CBCBD6}[data-theme=\"dark\"] #nf-nb .nf-nb-k{color:#7C8CFF}[data-theme=\"dark\"] #nf-nb .nf-nb-b{background:#4A57E8}[data-theme=\"dark\"] #nf-nb .nf-nb-s{color:#CBCBD6}[data-theme=\"dark\"] #nf-nb .nf-nb-s a{color:#9BA4FF}[data-theme=\"dark\"] #nf-nb .nf-nb-x{color:#95959F;border-top-color:rgba(255,255,255,.12)}[data-theme=\"dark\"] #nf-nb .nf-nb-x a{color:#FF6A2B}@media(max-width:640px){#nf-nb .nf-nb-in{padding:22px 18px}#nf-nb .nf-nb-b{width:100%;justify-content:center}}";
  document.head.appendChild(st);

  var box = document.createElement("div");
  box.id = "nf-nb";
  box.innerHTML =
    '<div class="nf-nb-in">' +
      '<span class="nf-nb-k">NEWFOR ／ 新規事業の担当になった方へ</span>' +
      '<p class="nf-nb-t">会議で出た言葉が、分からないまま進んでいませんか。</p>' +
      '<p class="nf-nb-d">' + lead +
        'のれん、カーブアウト、持分法、TOB、社内公募制度。' +
        '担当になると出てくる言葉17語を、1語ずつ引けるようにしました。' +
        '意味だけでなく、<b>その言葉が実際に出てくる公開情報の記録</b>も付けています。</p>' +
      '<a class="nf-nb-b" href="/words/">言葉を引く →</a>' +
      '<span class="nf-nb-s"><a href="/articles/">新規事業ヒストリー</a>' +
        '<a href="/companies/">企業を探す</a><a href="/news/">新規事業NEWS</a></span>' +
      '<span class="nf-nb-x">お金を集める側の方へ：' +
        '<a href="/shindan/">スタートアップ調達診断</a>' +
        '　3分・全18問・登録なし・先人の記録72件</span>' +
    '</div>';
  foot.parentNode.insertBefore(box, foot);

  box.querySelector(".nf-nb-b").addEventListener("click", function () {
    ev("words_guide_click", P.split("/")[1] || "other");
  });
  box.querySelector(".nf-nb-x a").addEventListener("click", function () {
    ev("shindan_guide_click", P.split("/")[1] || "other");
  });
})();
