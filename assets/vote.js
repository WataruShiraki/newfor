/* ============================================================
   NEWFOR 投票クライアント（Supabase）
   使い方：
   1. 下の SUPABASE_URL と SUPABASE_ANON_KEY を、自分のプロジェクトの値に置き換える
   2. 投票を置きたいページの </body> の直前で、このファイルを読み込む
        <script src="/assets/vote.js" defer></script>
   3. 投票させたい場所に、次の形のHTMLを置く
        <div class="vote-slot" data-poll="weekly-2026-08-05"></div>
   ============================================================ */
(function () {
  "use strict";

  var SUPABASE_URL = "https://xxxxxxxxxxxx.supabase.co";     // ← 置き換える
  var SUPABASE_ANON_KEY = "eyJhbGciOi...";                    // ← 置き換える（anonキーは公開して問題ありません）

  /* 端末を大まかに識別するハッシュ。個人は特定しません。
     ログイン不要のまま、同じ端末からの二重投票だけを防ぐためのものです。 */
  function voterHash() {
    var k = "newfor_vid";
    var v = null;
    try { v = window.name && window.name.indexOf(k) === 0 ? window.name.slice(k.length) : null; } catch (e) {}
    if (!v) {
      var seed = [navigator.userAgent, navigator.language, screen.width + "x" + screen.height,
                  new Date().getTimezoneOffset()].join("|");
      var h = 5381;
      for (var i = 0; i < seed.length; i++) { h = ((h << 5) + h + seed.charCodeAt(i)) >>> 0; }
      v = h.toString(36) + "-" + Math.floor(Math.random() * 1e9).toString(36);
      try { window.name = k + v; } catch (e) {}
    }
    return v;
  }

  function api(path, body) {
    return fetch(SUPABASE_URL + "/rest/v1/" + path, {
      method: body ? "POST" : "GET",
      headers: {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": "Bearer " + SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
      },
      body: body ? JSON.stringify(body) : undefined
    }).then(function (r) {
      if (!r.ok) throw new Error("supabase " + r.status);
      return r.json();
    });
  }

  function results(pollId) {
    return api("poll_results?poll_id=eq." + encodeURIComponent(pollId) + "&order=sort.asc");
  }

  function vote(pollId, optionKey) {
    return api("rpc/cast_vote", {
      p_poll_id: pollId, p_option_key: optionKey, p_voter_hash: voterHash()
    });
  }

  function total(rows) {
    return rows.reduce(function (s, r) { return s + Number(r.votes || 0); }, 0);
  }

  function render(el, rows, voted, chosen) {
    var t = total(rows);
    el.innerHTML =
      '<div class="vote' + (voted ? " voted" : "") + '">' +
        '<div class="vhead"><span class="vwho">新規事業に取り組んでいる、あなたへ</span></div>' +
        '<p class="q">' + (rows[0] && rows[0].question ? rows[0].question : "") + '</p>' +
        (voted ? "" : '<p class="vask">1タップで、この事業を応援できます。ログインもメールも要りません。<b>今すぐ投票！</b></p>') +
        '<div class="opts">' + rows.map(function (r) {
          var pct = Number(r.pct || 0);
          return '<button class="opt' + (chosen === r.option_key ? " chosen" : "") + '" data-k="' + r.option_key + '">' +
            '<span class="fill" style="width:' + (voted ? pct : 0) + '%"></span>' +
            '<span class="top"><span class="em">' + (r.emoji || "") + '</span>' +
            '<span class="nm">' + r.label + '</span>' +
            (chosen === r.option_key ? '<span class="you">あなた</span>' : "") +
            '<span class="pct" data-p>' + (voted ? pct + "%" : "") + '</span></span></button>';
        }).join("") + '</div>' +
        '<div class="vfoot"><span>' + (voted
            ? "あなたを含む " + t.toLocaleString() + "ユーザーが応援"
            : "すでに " + t.toLocaleString() + "ユーザーが応援しています　1タップで結果も見られます") + '</span></div>' +
        (voted ? '<div class="vthx">ありがとうございます。<b>あなたの1票が、この事業への応援になりました。</b></div>' : "") +
      '</div>';

    if (!voted) {
      Array.prototype.forEach.call(el.querySelectorAll(".opt"), function (b) {
        b.addEventListener("click", function () {
          var k = b.getAttribute("data-k");
          Array.prototype.forEach.call(el.querySelectorAll(".opt"), function (x) { x.disabled = true; });
          vote(el.getAttribute("data-poll"), k)
            .then(function (rows2) { render(el, rows2.length ? rows2 : rows, true, k); })
            .catch(function () { render(el, rows, true, k); });   // 通信に失敗しても画面は進める
        });
      });
    }
  }

  Array.prototype.forEach.call(document.querySelectorAll(".vote-slot"), function (el) {
    var pollId = el.getAttribute("data-poll");
    if (!pollId) return;
    results(pollId)
      .then(function (rows) { if (rows.length) render(el, rows, false, null); })
      .catch(function (e) { console.warn("[NEWFOR vote]", e); });  // 取れなければ何も出さない
  });
})();
