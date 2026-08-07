/* ============================================================
   NEWFOR ピックアップ（ヘッダー下を流れる、直近3日の投票）

   読むのは newfor_recent_votes ビューだけです。
   投票が無いとき・通信できないときは、帯ごと消します（空の帯は出さない）。
   ============================================================ */
(function () {
  "use strict";
  var NF_CSS = "/* ピックアップの帯。ヘッダーのすぐ下に置きます。\n   ここは「人の気配」を出す場所なので、青ではなく差し色のオレンジで拾わせます。 */\n/* 帯の色は画面いっぱい。中身はそのページの .wrap と同じ幅にそろえる。\n   （ページごとに 1240px / 1180px / 760px と違うので、.wrap をそのまま借ります） */\n#nf-pickup{position:relative;overflow:hidden;\n background:linear-gradient(90deg,#FFF1E4 0%,#FFF7F0 60%,#FFF1E4 100%);\n border-bottom:1px solid rgba(224,74,12,.22);font-size:12.5px;line-height:1}\n#nf-pickup .nf-pk-in{display:flex;align-items:center;gap:12px;height:40px;\n flex-wrap:nowrap;min-height:0}\n#nf-pickup .nf-pk-tag{flex:0 0 auto;display:inline-flex;align-items:center;gap:6px;\n background:#E04A0C;color:#fff;font-weight:800;font-size:10.5px;\n letter-spacing:.12em;padding:6px 10px;border-radius:6px;box-shadow:0 1px 0 rgba(0,0,0,.06)}\n#nf-pickup .nf-pk-tag i{width:6px;height:6px;border-radius:50%;background:#fff;\n animation:nf-pk-blink 1.6s ease-in-out infinite}\n@keyframes nf-pk-blink{0%,100%{opacity:1}50%{opacity:.25}}\n#nf-pickup .nf-pk-win{position:relative;flex:1 1 auto;overflow:hidden;height:100%;\n -webkit-mask-image:linear-gradient(90deg,transparent 0,#000 24px,#000 calc(100% - 44px),transparent 100%);\n mask-image:linear-gradient(90deg,transparent 0,#000 24px,#000 calc(100% - 44px),transparent 100%)}\n#nf-pickup .nf-pk-track{display:flex;align-items:center;height:100%;width:max-content;\n animation:nf-pk-flow 40s linear infinite}\n#nf-pickup:hover .nf-pk-track{animation-play-state:paused}\n#nf-pickup .nf-pk-item{display:inline-flex;align-items:center;gap:8px;padding:0 20px;\n white-space:nowrap;text-decoration:none;color:#5A5368;border-radius:6px}\n/* カーソルを乗せたら、その1件まるごとに線を引く */\n#nf-pickup .nf-pk-item:hover{text-decoration:underline;text-decoration-color:rgba(224,74,12,.5);\n text-underline-offset:4px;text-decoration-thickness:1.5px;color:#2A2439}\n#nf-pickup .nf-pk-d{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:#B0A79E;\n border:1px solid rgba(224,74,12,.2);border-radius:4px;padding:2px 5px}\n#nf-pickup .nf-pk-w{color:#E04A0C;font-weight:800}\n#nf-pickup .nf-pk-t b{font-weight:700;color:#2A2439}\n#nf-pickup .nf-pk-n{background:#E04A0C;color:#fff;font-weight:800;font-size:10px;\n border-radius:9px;padding:2px 7px}\n/* 左から右へ流す。うしろに同じ並びをもう一組置いてあるので、\n   -w から 0 へ動かすと、切れ目なく右へ流れ続けます */\n@keyframes nf-pk-flow{from{transform:translateX(calc(var(--nf-pk-w,1000px) * -1))}to{transform:translateX(0)}}\n@media (prefers-reduced-motion:reduce){\n  #nf-pickup .nf-pk-track{animation:none}\n  #nf-pickup .nf-pk-tag i{animation:none}\n  #nf-pickup .nf-pk-win{overflow-x:auto}\n}\nhtml[data-theme=\"dark\"] #nf-pickup,\n[data-theme=\"dark\"] #nf-pickup{background:#1B1526;border-bottom-color:rgba(255,138,69,.22)}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-item{color:#B6ADBF}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-item:hover{color:#F2ECF7}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-w{color:#FF8A45}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-t b{color:#EDE7F2}\n[data-theme=\"dark\"] #nf-pickup .nf-pk-d{color:#8C8397;border-color:rgba(255,138,69,.24)}\n@media (max-width:640px){#nf-pickup{font-size:11.5px}\n  #nf-pickup .nf-pk-in{height:36px;gap:8px}\n  #nf-pickup .nf-pk-tag{font-size:9.5px;padding:5px 8px}\n  #nf-pickup .nf-pk-item{padding:0 14px;gap:6px}}";
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
