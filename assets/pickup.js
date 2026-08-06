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

  function line(r) {
    var id = String(r.poll_id || "");
    var n = Number(r.votes || 0);
    var tail = n > 1 ? "と" + n + "人が投票しました。" : "と投票がありました。";
    var who, href, mid;
    if (id.indexOf("weekly-") === 0) {
      /* 今週の投票には記事がない。記事名を出すと嘘になるので言い方を変える */
      who = "今週の投票";
      href = "/#vote";
      mid = "で「";
    } else {
      var m = MAP[id.replace(/^reaction-/, "")];
      who = m ? m.name : "NEWFOR";
      href = m ? m.url : "/articles/";
      mid = "の記事に「";
    }
    var a = document.createElement("a");
    a.className = "nf-pk-item";
    a.href = href;
    a.innerHTML = '<span class="nf-pk-d">・' + md(r.at) + '</span>' +
                  '<span class="nf-pk-w">' + who + '</span>' +
                  '<span class="nf-pk-t">' + mid + (r.label || "") + '」' + tail + '</span>';
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
