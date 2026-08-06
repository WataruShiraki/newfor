/* ============================================================
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
                  '<span class="nf-pk-t">に<b>「' + (r.label || "") + '」</b>の声</span>' +
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

    /* 中身の長さに合わせて、速さを決める（1秒あたり60pxくらい） */
    var w = track.scrollWidth / 2;
    track.style.setProperty("--nf-pk-w", w + "px");
    track.style.animationDuration = Math.max(18, Math.round(w / 60)) + "s";
    band.hidden = false;
  })
  .catch(function (e) { console.warn("[NEWFOR pickup]", e); die(); });
})();
