/* ============================================================
   NEWFOR 共有ボタンと、訂正・補足の受付窓口

   なぜ作ったか
     記録された会社の新規事業担当者ご本人が、自分の会社の年表を
     社内へ貼れるようにするためです。サウナイキタイが最初に伸びたのは、
     掲載されたサウナが館内にポスターを貼ってくれたからでした。
     同じ構造を作ります。

     あわせて、訂正・補足を受け取る窓口を置きます。企業ページの下には
     前から「Aboutのフォームからお知らせください」と書いてありましたが、
     そのフォームがどこにもありませんでした。ここで本物を作ります。

   置き方の決まり
     **ページのHTMLは1文字も変えません。**
     このファイルは assets/pickup.js から呼ばれます。pickup.js は既に
     全ページに入っているので、枠を足すために1100ページを上げ直す必要が
     ありません（一度それをやりかけて、14回に分けてアップロードする
     羽目になりかけました）。

     置き場所も、出す中身も、このファイルが自分で決めます。
     会社名も件数も、ページの <title> から読みます。同じ内容を
     HTML側にも持たせると、年表を1件足すたびに全ページがズレます。

   言葉づかい
     _src/KOTOBA.md が最優先です。挑戦を否定する言葉は1語も入れません。
     記録された会社の方が読んで、嫌な気持ちにならない文だけを置きます。
   ============================================================ */
(function () {
  "use strict";

  if (window.__nfShareDone) return;
  window.__nfShareDone = true;

  var API = "https://jakwntemjkwqwaqujffh.supabase.co/rest/v1";
  var KEY = "sb_publishable_bQ84WCmRiFUbpPemMcO9xQ_Dj9Mh1mQ";

  /* ── どのページに出すか ──
     企業ページ /companies/<slug>/ と、NEWS 1件ずつ /news/<slug>/ だけ。
     一覧（/companies/ /news/）と年別アーカイブ（/news/2026/）には出しません。 */
  var path = location.pathname;
  var kind, target;
  if (path === "/about/") {
    /* 運営者情報のページ。メールアドレスは公開しません（迷惑メールを避けるため）。
       ここが、そのかわりの窓口です。共有ボタンは出しません。 */
    kind = "contact"; target = "about";
  } else {
    var m = path.match(/^\/(companies|news)\/([^\/]+)\/$/);
    if (!m) return;
    kind = m[1] === "companies" ? "company" : "news";
    target = m[2];
    if (kind === "news" && /^\d{4}$/.test(target)) return;
  }

  /* ── 出す文は <title> から作る ──
     企業  : 「三菱重工業の新規事業44件｜2012年からの全記録と出典 | NEWFOR」
     NEWS  : 「デンソー、RE-CORE を開始｜2026.08.05の新規事業NEWS | NEWFOR」 */
  var title = (document.title || "").replace(/\s*\|\s*NEWFOR\s*$/, "").trim();
  var head = title.split("｜")[0].trim() || "NEWFORの記録";
  var share, label;
  if (kind === "contact") {
    share = ""; label = "";
  } else if (kind === "company") {
    share = head + "を、開始年の古い順に並べた年表です。1件ずつ出典つき。";
    label = head.replace(/の新規事業.*$/, "") + "の年表";
  } else {
    share = title;
    label = "この記録";
  }

  var CSS = ".nf-sr{margin:34px 0 0;padding:26px 24px 24px;border:1px solid var(--border,rgba(18,14,38,.13));border-radius:16px;background:var(--surface-2,#fff)}\n.nf-sr-h{font-size:15px;font-weight:800;letter-spacing:.02em;color:var(--tx-1,#120E26)}\n.nf-sr-h2{margin:26px 0 0;padding:22px 0 0;border-top:1px solid var(--border,rgba(18,14,38,.13));font-size:15px;font-weight:800;letter-spacing:.02em;color:var(--tx-1,#120E26)}\n.nf-sr-p{margin:7px 0 0;font-size:13px;line-height:1.85;color:var(--tx-2,#403C55)}\n.nf-sr-p b{font-weight:700;color:var(--tx-1,#120E26)}\n.nf-sr-row{display:flex;flex-wrap:wrap;gap:9px;margin:15px 0 0}\n.nf-sr-b{display:inline-flex;align-items:center;justify-content:center;gap:7px;padding:11px 16px;border-radius:9px;border:1px solid var(--border-2,rgba(18,14,38,.22));background:var(--surface,#fff);color:var(--tx-1,#120E26);font-size:13px;font-weight:700;text-decoration:none;line-height:1;cursor:pointer;transition:.15s}\n.nf-sr-b:hover{border-color:var(--accent,#2F3BD6);color:var(--accent,#2F3BD6);transform:translateY(-1px)}\n.nf-sr-b.cp.ok{border-color:var(--accent,#2F3BD6);background:var(--accent-w,rgba(47,59,214,.08));color:var(--accent,#2F3BD6)}\n.nf-sr-open{margin:14px 0 0;padding:12px 20px;border-radius:9px;border:1px solid var(--accent,#2F3BD6);background:transparent;color:var(--accent,#2F3BD6);font-size:13.5px;font-weight:800;cursor:pointer;transition:.15s;font-family:inherit}\n.nf-sr-open:hover{background:var(--accent,#2F3BD6);color:#fff}\n.nf-sr-form{margin:16px 0 0}\n.nf-sr-ks{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 12px}\n.nf-sr-k{display:inline-flex;align-items:center;gap:6px;padding:8px 13px;border-radius:8px;border:1px solid var(--border,rgba(18,14,38,.13));background:var(--surface,#fff);font-size:12.5px;font-weight:600;color:var(--tx-2,#403C55);cursor:pointer}\n.nf-sr-k:has(input:checked){border-color:var(--accent,#2F3BD6);color:var(--accent,#2F3BD6);background:var(--accent-w,rgba(47,59,214,.08));font-weight:700}\n.nf-sr-k input{accent-color:var(--accent,#2F3BD6);margin:0}\n.nf-sr-ta,.nf-sr-in{display:block;width:100%;box-sizing:border-box;margin:0 0 9px;padding:12px 14px;border-radius:9px;border:1px solid var(--border-2,rgba(18,14,38,.22));background:var(--page,#fff);color:var(--tx-1,#120E26);font-size:14px;line-height:1.8;font-family:inherit;resize:vertical}\n.nf-sr-ta::placeholder,.nf-sr-in::placeholder{color:var(--tx-3,#8C8497)}\n.nf-sr-ta:focus,.nf-sr-in:focus{outline:none;border-color:var(--accent,#2F3BD6);box-shadow:0 0 0 3px var(--accent-w,rgba(47,59,214,.08))}\n.nf-sr-mini{margin:2px 0 12px;font-size:11.5px;line-height:1.75;color:var(--tx-3,#8C8497)}\n.nf-sr-mini a{color:inherit}\n.nf-sr-go{padding:13px 30px;border-radius:9px;border:0;background:var(--accent,#2F3BD6);color:#fff;font-size:14px;font-weight:800;cursor:pointer;font-family:inherit;transition:.15s}\n.nf-sr-go:hover{filter:brightness(1.08)}\n.nf-sr-go:disabled{opacity:.55;cursor:default}\n.nf-sr-msg{margin:11px 0 0;font-size:12.5px;line-height:1.8}\n.nf-sr-msg.ng{color:#C6410B}\n.nf-sr-msg a{color:inherit}\n.nf-sr-ok{padding:18px 20px;border-radius:11px;background:var(--accent-w,rgba(47,59,214,.08));border:1px solid var(--accent-l,rgba(47,59,214,.30))}\n.nf-sr-ok b{display:block;font-size:14.5px;font-weight:800;color:var(--accent,#2F3BD6)}\n.nf-sr-ok span{display:block;margin:6px 0 0;font-size:13px;line-height:1.85;color:var(--tx-2,#403C55)}\n@media(max-width:560px){\n .nf-sr{padding:22px 17px 20px}\n .nf-sr-row{display:grid;grid-template-columns:1fr 1fr;gap:8px}\n .nf-sr-b{padding:12px 8px;font-size:12px}\n .nf-sr-go{width:100%}\n}";

  if (!document.getElementById("nf-sr-css")) {
    var st = document.createElement("style");
    st.id = "nf-sr-css";
    st.textContent = CSS;
    document.head.appendChild(st);
  }

  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }

  /* 24時間に3件まで。いたずらを止めるためではなく、押し間違いを防ぐためです */
  function sent() {
    try {
      var a = JSON.parse(localStorage.getItem("nf_sr") || "[]");
      var t = Date.now() - 86400000;
      return a.filter(function (x) { return x > t; });
    } catch (e) { return []; }
  }
  function mark() {
    try {
      var a = sent(); a.push(Date.now());
      localStorage.setItem("nf_sr", JSON.stringify(a));
    } catch (e) {}
  }

  var KINDS_PAGE = [
    ["correction", "内容が違う"],
    ["missing", "この事業が抜けている"],
    ["supplement", "その後を知っている"]
  ];
  var KINDS_CONTACT = [
    ["correction", "掲載内容の訂正"],
    ["missing", "掲載してほしい事業"],
    ["other", "その他のお問い合わせ"]
  ];
  var KINDS = (kind === "contact") ? KINDS_CONTACT : KINDS_PAGE;

  function build() {
    var url = location.origin + location.pathname;
    var u = encodeURIComponent(url);
    var t = encodeURIComponent(share);

    var w = el("div", "nf-sr");

    /* ── 共有 ──
       運営者情報のページ（/about/）では共有ボタンを出しません。
       あそこは「連絡する場所」であって、広める場所ではないためです。 */
    if (kind !== "contact") {
    w.appendChild(el("div", "nf-sr-h", "この記録を共有する"));
    w.appendChild(el("p", "nf-sr-p",
      label + "は、公開情報だけで組み立てています。" +
      "社内で回すとき、そのまま使ってください。"));

    var row = el("div", "nf-sr-row");

    function btn(cls, txt, href) {
      var a = el("a", "nf-sr-b " + cls, txt);
      a.href = href; a.target = "_blank"; a.rel = "noopener";
      return a;
    }
    row.appendChild(btn("x", "X で共有",
      "https://twitter.com/intent/tweet?text=" + t + "&url=" + u));
    row.appendChild(btn("li", "LinkedIn で共有",
      "https://www.linkedin.com/sharing/share-offsite/?url=" + u));
    row.appendChild(btn("hb", "はてなブックマーク",
      "https://b.hatena.ne.jp/entry/panel/?url=" + u + "&title=" + t));

    var cp = el("button", "nf-sr-b cp", "リンクをコピー");
    cp.type = "button";
    cp.addEventListener("click", function () {
      var done = function () {
        cp.textContent = "コピーしました";
        cp.classList.add("ok");
        setTimeout(function () {
          cp.textContent = "リンクをコピー";
          cp.classList.remove("ok");
        }, 2200);
      };
      function fallback() {
        var ta = document.createElement("textarea");
        ta.value = url;
        ta.style.cssText = "position:fixed;top:-999px";
        document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy"); done(); } catch (e) {}
        document.body.removeChild(ta);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(done, fallback);
      } else { fallback(); }
    });
    row.appendChild(cp);
    w.appendChild(row);
    }

    /* ── 訂正・補足（/about/ ではお問い合わせ） ── */
    var f = el("div", "nf-sr-f");
    if (kind === "contact") {
      f.className = "nf-sr-f solo";
      f.appendChild(el("div", "nf-sr-h", "お問い合わせ"));
      f.appendChild(el("p", "nf-sr-p",
        "掲載内容の訂正、掲載の取り下げ、取材や広告のご相談。どれでもこちらへお願いします。" +
        "<b>記録した会社の方からのご連絡も、同じ窓口で受け付けています。</b>" +
        "返信が必要な場合は、ご連絡先をお書き添えください。"));
    } else {
      f.appendChild(el("div", "nf-sr-h2", "訂正・補足を送る"));
      f.appendChild(el("p", "nf-sr-p",
        "抜けている事業、日付の違い、その後の動き。どれでも歓迎します。" +
        "<b>記録した会社の方からのご連絡も、同じ窓口で受け付けています。</b>" +
        "いただいた内容は、一次情報を確かめたうえで年表に反映します。"));
    }

    var open = el("button", "nf-sr-open",
      kind === "contact" ? "お問い合わせフォームを開く" : "この記録について知らせる");
    open.type = "button";
    f.appendChild(open);

    var form = el("form", "nf-sr-form");
    form.hidden = true;

    var ks = el("div", "nf-sr-ks");
    KINDS.forEach(function (k, i) {
      var lb = el("label", "nf-sr-k");
      var r = document.createElement("input");
      r.type = "radio"; r.name = "nf-sr-kind"; r.value = k[0];
      if (i === 0) r.checked = true;
      lb.appendChild(r);
      lb.appendChild(el("span", null, k[1]));
      ks.appendChild(lb);
    });
    form.appendChild(ks);

    var ta = document.createElement("textarea");
    ta.className = "nf-sr-ta";
    ta.rows = 4; ta.maxLength = 4000; ta.required = true;
    ta.placeholder = kind === "contact"
      ? "例）弊社の掲載内容について、1点訂正をお願いしたく連絡しました。\n例）取材のご相談です。"
      : "例）2019年3月に、この事業を◯◯社へ引き継いでいます。\n例）開始は2021年4月ではなく、同年7月です。";
    form.appendChild(ta);

    var src = document.createElement("input");
    src.className = "nf-sr-in"; src.type = "url"; src.maxLength = 600;
    src.placeholder = "一次情報のURL（プレスリリース・IR資料など／任意）";
    form.appendChild(src);

    var ct = document.createElement("input");
    ct.className = "nf-sr-in"; ct.type = "text"; ct.maxLength = 200;
    ct.placeholder = "お名前・ご連絡先（任意。返信が要るときだけ）";
    form.appendChild(ct);

    form.appendChild(el("p", "nf-sr-mini",
      (kind === "contact"
        ? "送っていただいた内容は、お返事と掲載内容の確認にだけ使います。"
        : "送っていただいた内容は、年表を直すためだけに使います。") +
      "サイトに公開することはありません。" +
      "<a href=\"/privacy/\">プライバシーポリシー</a>"));

    var go = el("button", "nf-sr-go", "送る");
    go.type = "submit";
    form.appendChild(go);

    var msg = el("p", "nf-sr-msg");
    msg.hidden = true;
    form.appendChild(msg);

    open.addEventListener("click", function () {
      form.hidden = false; open.hidden = true; ta.focus();
    });

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var body = (ta.value || "").trim();
      if (body.length < 5) {
        msg.hidden = false; msg.className = "nf-sr-msg ng";
        msg.textContent = "もう少しだけ詳しく書いてください。";
        return;
      }
      if (sent().length >= 3) {
        msg.hidden = false; msg.className = "nf-sr-msg ng";
        msg.textContent = "1日に送れるのは3件までです。明日またお願いします。";
        return;
      }
      var k = form.querySelector("input[name=nf-sr-kind]:checked");
      go.disabled = true; go.textContent = "送っています…";

      fetch(API + "/rpc/newfor_send_report", {
        method: "POST",
        headers: {
          apikey: KEY,
          Authorization: "Bearer " + KEY,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          p_page_url: url,
          p_page_kind: kind,
          p_target: target,
          p_kind: k ? k.value : "correction",
          p_body: body,
          p_source_url: (src.value || "").trim() || null,
          p_contact: (ct.value || "").trim() || null
        })
      }).then(function (r) {
        if (!r.ok) throw new Error("supabase " + r.status);
        return r.json();
      }).then(function () {
        mark();
        form.innerHTML = "";
        form.appendChild(el("div", "nf-sr-ok",
          "<b>ありがとうございます。受け取りました。</b>" +
          "<span>" + (kind === "contact"
            ? "内容を確かめてお返事します。ご連絡先をいただいた場合のみ、返信いたします。"
            : "一次情報を確かめたうえで、年表に反映します。この記録が良くなります。") +
          "</span>"));
      }).catch(function () {
        go.disabled = false; go.textContent = "送る";
        msg.hidden = false; msg.className = "nf-sr-msg ng";
        msg.textContent = "うまく送れませんでした。通信の具合かもしれません。" +
          "少し時間をおいて、もう一度お試しください。";
      });
    });

    f.appendChild(form);
    w.appendChild(f);

    /* ── 置き場所は自分で決める。フッターの直前 ── */
    var foot = document.querySelector("footer");
    if (foot && foot.parentNode) {
      foot.parentNode.insertBefore(w, foot);
    } else {
      document.body.appendChild(w);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else { build(); }
})();
