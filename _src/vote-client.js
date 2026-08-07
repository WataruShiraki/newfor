/* ============================================================
   NEWFOR 読者の投票

   2つの投票を、このファイル1本で扱います。

     data-poll="daily"        … 今日の1件への期待度（トップ。毎日ちがう1件）
     data-poll="reaction-…"   … 記事を読み終えたあとの反応

   直したこと（前の版で起きていたこと）

   1. 同じ人が何度でも入れられた
      端末の識別子を window.name に置いていたため、タブを開き直すたびに
      別人になっていました。localStorage と Cookie に置き直しています。

   2. 投票したあと、何に答えたのか分からなくなった
      投票を受け付ける関数が問いの文を返さないので、画面から問いが消えて
      いました。問いは最初に受け取ったものを持ち続けます。

   3. ずっと同じ問いだった
      問いも選択肢もこれまでどおり（期待度／否定の選択肢は置かない）ですが、
      毎日ちがう1件を出します。毎日来て、毎日1票入れられます。

   見た目（CSS）もこのファイルの中にあります。ページ側は読み込み1行だけです。
   ============================================================ */
(function () {
  "use strict";

  var API = "https://jakwntemjkwqwaqujffh.supabase.co/rest/v1";
  var KEY = "sb_publishable_bQ84WCmRiFUbpPemMcO9xQ_Dj9Mh1mQ";

  /* ── 見た目 ───────────────────────────────────────── */
  var CSS = __NFVCSS__;

  if (!document.getElementById("nf-vote-css")) {
    var st = document.createElement("style");
    st.id = "nf-vote-css";
    st.textContent = CSS;
    document.head.appendChild(st);
  }

  /* ── 端末の識別子。個人は特定しません ──────────────────
     ログインなしのまま「1問につき1票」にするためだけのものです。
     localStorage が使えない設定（プライベートブラウズなど）でも
     Cookie で残るようにしてあります。 */
  function ck(k, v, days) {
    if (v === undefined) {
      var m = document.cookie.match("(^|; )" + k + "=([^;]*)");
      return m ? decodeURIComponent(m[2]) : null;
    }
    var d = new Date();
    d.setTime(d.getTime() + days * 864e5);
    document.cookie = k + "=" + encodeURIComponent(v) + ";expires=" + d.toUTCString() +
                      ";path=/;SameSite=Lax";
  }
  function ls(k, v) {
    try {
      if (v === undefined) return localStorage.getItem(k);
      localStorage.setItem(k, v);
    } catch (e) {}
    return null;
  }
  function vid() {
    var k = "nf_vid";
    var v = ls(k) || ck(k);
    if (!v) v = Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 11);
    ls(k, v); ck(k, v, 400);
    return v;
  }
  function myVote(pid, set) {
    var k = "nf_v_" + pid;
    if (set === undefined) return ls(k) || ck(k);
    ls(k, set); ck(k, set, 400);
    return set;
  }

  /* ── 通信 ─────────────────────────────────────────── */
  function api(path, body) {
    return fetch(API + "/" + path, {
      method: body ? "POST" : "GET",
      headers: { apikey: KEY, Authorization: "Bearer " + KEY, "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined
    }).then(function (r) {
      if (!r.ok) throw new Error("supabase " + r.status);
      return r.json();
    });
  }
  function results(pid) {
    return api("newfor_poll_results?poll_id=eq." + encodeURIComponent(pid) + "&order=sort.asc")
      .then(function (rows) { return rows.filter(function (r) { return r.option_key !== "flat"; }); });
  }
  function cast(pid, key) {
    return api("rpc/newfor_cast_vote", { p_poll_id: pid, p_option_key: key, p_voter_hash: vid() });
  }
  function total(rows) {
    return rows.reduce(function (s, r) { return s + Number(r.votes || 0); }, 0);
  }
  function esc(t) {
    return String(t == null ? "" : t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  /* ── その日の1問 ───────────────────────────────────── */
  function todayJST() {
    var d = new Date(Date.now() + 9 * 36e5);       /* 日本時間の日付にそろえる */
    return d.toISOString().slice(0, 10);
  }
  function pollFor(day) {
    var Q = window.NF_POLL;
    if (!Q || !Q.d || !Q.d.length) return null;
    var n = Math.round((Date.parse(day + "T00:00:00Z") - Date.parse(Q.s + "T00:00:00Z")) / 864e5);
    n = ((n % Q.d.length) + Q.d.length) % Q.d.length;
    var a = Q.q[Q.d[n]];
    if (!a) return null;
    return { id: "daily-" + day, day: day, co: a[0], date: a[1], t: a[2], note: a[3],
             url: a[4], ind: a[5] };
  }
  function jpday(day) {
    var p = day.split("-");
    return Number(p[1]) + "月" + Number(p[2]) + "日";
  }

  var SAFE =
    '<ul class="nfv-safe">' +
    '<li>ログインは要りません。<b>お名前もメールアドレスもいただきません</b></li>' +
    '<li>公開するのは票数の集計だけ。<b>どなたがどれを選んだかは、誰にも分かりません</b></li>' +
    '<li>1日1件、1票まで。<b>選ぶと、その場でみんなの内訳が見えます</b></li>' +
    '</ul>';

  /* ── 今日の1件への期待度 ───────────────────────────── */
  function renderPoll(el, q, rows, chosen) {
    var t = total(rows);
    var pct = {};
    rows.forEach(function (r) { pct[r.option_key] = Number(r.pct || 0); });
    var head =
      '<div class="nfv-hd"><span class="nfv-tag">今日の1件</span>' +
      '<span class="nfv-day">' + esc(jpday(q.day)) + 'の投票</span></div>';
    var ask =
      '<div class="nfv-q"><span class="nfv-y">' + esc(q.date) + '・' + esc(q.co) + '</span>' +
      '<p class="nfv-t">' + esc(q.t) + '</p>' +
      '<p class="nfv-sub">' + esc(q.note) + '</p>' +
      '<p class="nfv-ask">この新規事業に、<b>どれくらい期待しますか。</b></p></div>';

    if (!chosen) {
      el.innerHTML =
        '<div class="nfv">' + head + ask + SAFE +
        '<div class="nfv-opts">' +
          '<button class="nfv-o" data-k="a"><span class="em">🚀</span>めちゃくちゃ期待！</button>' +
          '<button class="nfv-o" data-k="b"><span class="em">👀</span>いまは様子見</button>' +
        '</div>' +
        '<p class="nfv-n">' + (t > 0
          ? "すでに " + t.toLocaleString() + "人が答えています。選ぶと、内訳が見えます"
          : "まだ回答がありません。<b>最初の1票をお待ちしています</b>") + '</p>' +
        '</div>';
      Array.prototype.forEach.call(el.querySelectorAll(".nfv-o"), function (b) {
        b.addEventListener("click", function () {
          var k = b.getAttribute("data-k");
          Array.prototype.forEach.call(el.querySelectorAll(".nfv-o"), function (x) { x.disabled = true; });
          myVote(q.id, k);
          cast(q.id, k)
            .then(function (rs) { renderPoll(el, q, rs.length ? rs : rows, k); })
            .catch(function () { renderPoll(el, q, rows, k); });
        });
      });
      return;
    }

    var bar = function (key, emoji, label) {
      var p = pct[key] || 0;
      return '<div class="nfv-b' + (key === chosen ? " mine" : "") + '">' +
        '<span class="fill" style="width:' + p + '%"></span>' +
        '<span class="lb"><span class="em">' + emoji + '</span>' + label +
        (key === chosen ? '<em>あなた</em>' : '') + '</span>' +
        '<span class="pv">' + p + '<small>%</small></span></div>';
    };
    /* まだ票が入っていないうちに 0% を並べると、自分の1票が数えられていない
       ように見えます。集計が届くまでは内訳を出しません。 */
    var bars = t > 0
      ? '<div class="nfv-bars">' + bar("a", "🚀", "めちゃくちゃ期待！") + bar("b", "👀", "いまは様子見") + '</div>'
      : '';
    el.innerHTML =
      '<div class="nfv voted">' + head + ask + bars +
      '<p class="nfv-n">' + (t > 1
        ? "あなたを含む " + t.toLocaleString() + "人の回答です"
        : "あなたが最初のひとりです。ありがとうございます") + '</p>' +
      '<p class="nfv-thx">ありがとうございます。<b>あなたの1票が、この事業への応援になりました。</b></p>' +
      '<a class="nfv-cta" href="' + q.url + '">この事業の記録を読む' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13"/><path d="M12 5l7 7-7 7"/></svg></a>' +
      '<p class="nfv-tm">明日は、また別の1件をお出しします。</p>' +
      '</div>';
  }

  /* ── 記事末尾の反応（これまでの形を残しつつ、問いが消えないように） ── */
  function renderReact(el, question, rows, chosen) {
    var t = total(rows);
    el.innerHTML =
      '<div class="nfv nfv-re' + (chosen ? " voted" : "") + '">' +
      '<div class="nfv-hd"><span class="nfv-tag">読者の反応</span>' +
      '<span class="nfv-day">ここまで読んでくださった、あなたへ</span></div>' +
      '<div class="nfv-q"><p class="nfv-ask2">' + esc(question) + '</p></div>' +
      (chosen ? "" : '<p class="nfv-n2">選ぶと、<b>ほかの読者が何を選んだかが、その場で見えます。</b>ログインもメールも要りません。</p>') +
      '<div class="nfv-opts re">' + rows.map(function (r) {
        var p = Number(r.pct || 0);
        return '<button class="nfv-o re' + (chosen === r.option_key ? " mine" : "") + '" data-k="' +
          esc(r.option_key) + '"' + (chosen ? " disabled" : "") + '>' +
          '<span class="fill" style="width:' + (chosen ? p : 0) + '%"></span>' +
          '<span class="lb"><span class="em">' + esc(r.emoji || "") + '</span>' + esc(r.label) +
          (chosen === r.option_key ? '<em>あなた</em>' : '') + '</span>' +
          '<span class="pv">' + (chosen ? p + "%" : "") + '</span></button>';
      }).join("") + '</div>' +
      '<p class="nfv-n">' + (chosen
        ? (t > 1 ? "あなたを含む " + t.toLocaleString() + "人の回答です" : "1人目の回答、ありがとうございます")
        : (t > 0 ? "すでに " + t.toLocaleString() + "人が答えています" : "まだ回答がありません。<b>最初の1票をお待ちしています</b>")) + '</p>' +
      (chosen ? '<p class="nfv-tm">ありがとうございます。この1票が、次にどの記録を掘り起こすかの手がかりになります。</p>' : '') +
      '</div>';

    if (!chosen) {
      Array.prototype.forEach.call(el.querySelectorAll(".nfv-o"), function (b) {
        b.addEventListener("click", function () {
          var k = b.getAttribute("data-k");
          var pid = el.getAttribute("data-poll");
          Array.prototype.forEach.call(el.querySelectorAll(".nfv-o"), function (x) { x.disabled = true; });
          myVote(pid, k);
          cast(pid, k)
            .then(function (rs) { renderReact(el, question, rs.length ? rs : rows, k); })
            .catch(function () { renderReact(el, question, rows, k); });
        });
      });
    }
  }

  /* ── 起動 ─────────────────────────────────────────── */
  Array.prototype.forEach.call(document.querySelectorAll(".vote-slot"), function (el) {
    var kind = el.getAttribute("data-poll");
    if (!kind) return;

    if (kind === "daily") {
      var q = pollFor(todayJST());
      if (!q) { el.remove(); return; }
      el.setAttribute("data-poll", q.id);
      var mine = myVote(q.id);
      /* 集計が取れなくても、問いと選択肢は出せるようにしておく */
      var blank = [{ option_key: "a", label: "めちゃくちゃ期待！", votes: 0, pct: 0 },
                   { option_key: "b", label: "いまは様子見", votes: 0, pct: 0 }];
      results(q.id)
        .then(function (rows) { renderPoll(el, q, rows.length ? rows : blank, mine); })
        .catch(function () { renderPoll(el, q, blank, mine); });
      return;
    }

    results(kind)
      .then(function (rows) {
        if (!rows.length) return;
        renderReact(el, rows[0].question || "", rows, myVote(kind));
      })
      .catch(function (e) { console.warn("[NEWFOR vote]", e); });
  });
})();
