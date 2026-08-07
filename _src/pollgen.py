# -*- coding: utf-8 -*-
"""読者の投票 ─ 毎日ちがう「今日の1件」への期待度を集める

■ 直したのはUIと運用で、企画は変えていません

問いは これまでどおり「あなたの期待度は？」、選択肢も
「めちゃくちゃ期待！」と「いまは様子見」の2つです。否定の選択肢は置きません。
変えたのは次の3つだけです。

  1. 毎日ちがう1件を出す
     これまでは1つの問いがずっと出たままでした。毎日来ても同じ問いなので、
     2日目からは入れる票がありません。新しい発表から順に、1日1件出します。

  2. 同じ人が何度も入れられないようにする（vote-client.js 側）

  3. 投票したあとも、何に答えたのかが画面に残るようにする（vote-client.js 側）

■ 出題の選び方

  ・新しい発表から順（2024年以降）
  ・説明文があるもの
  ・同じ会社が2日つづかないようにずらす

■ 作るもの

  gh/assets/poll.js      … 日付ごとの1件（画面が読む）
  gh/supabase/poll.sql   … 票を貯めるための polls / poll_options
"""
import io, os, json, datetime

import newsdata

START = datetime.date(2026, 8, 7)      # 出題をはじめる日
DAYS = 365
SINCE = 2024                            # これより古い発表は、期待度を聞いても実感がない


def pool():
    IT = newsdata.build()               # すでに新しい順
    c = [i for i in IT if i['year'] >= SINCE and len(i['note']) >= 20 and i['src']]
    # 同じ会社が2日つづかないように、ずらす
    out, rest = [], c[:]
    while rest:
        pick = 0
        for k, x in enumerate(rest):
            if not out or x['coslug'] != out[-1]['coslug']:
                pick = k
                break
        out.append(rest.pop(pick))
    return out


def main():
    P = pool()
    days = [(START + datetime.timedelta(days=n), P[n % len(P)]) for n in range(DAYS)]

    # ── 画面が読むデータ ──
    # 同じ1件が何度も出るので、1件は1回だけ持ち、日付には番号だけを並べます。
    uniq, idx, order = {}, [], []
    for d, it in days:
        if it['slug'] not in uniq:
            uniq[it['slug']] = len(order)
            order.append([it['co'], it['date'].replace('-', '.'), it['title'], it['note'],
                          newsdata.path(it), it['ind']])
        idx.append(uniq[it['slug']])
    Q = {'s': days[0][0].isoformat(), 'q': order, 'd': idx}
    os.makedirs('gh/assets', exist_ok=True)
    io.open('gh/assets/poll.js', 'w', encoding='utf-8').write(
        '/* NEWFOR 読者の投票「今日の1件」。pollgen.py が作ります。手で書かないでください。\n'
        '   s = 出題をはじめた日 / q = 1件（会社・日付・見出し・説明・行き先・業種）\n'
        '   d = その日に出す番号。s から数えた日数で引きます。 */\n'
        'window.NF_POLL=' + json.dumps(Q, ensure_ascii=False, separators=(',', ':')) + ';\n')

    # ── 票を貯めるための SQL ──
    def q(s):
        return "'" + str(s).replace("'", "''") + "'"

    PP, OO = [], []
    for d, it in days:
        pid = 'daily-%s' % d.isoformat()
        # 問いの文には会社名を必ず入れます。ヘッダー下の帯（ピックアップ）が、
        # この文から掲載企業を拾っているためです。
        question = '%s｜%s「%s」への期待度は？' % (it['co'], it['date'].replace('-', '.'), it['title'])
        PP.append('(%s,%s,%s,%s,%s)' % (
            q(pid), q(question), q('daily'),
            q(d.isoformat() + 'T00:00:00+09:00'),
            q((d + datetime.timedelta(days=1)).isoformat() + 'T00:00:00+09:00')))
        OO.append('(%s,%s,%s,%s,%d)' % (q(pid), q('a'), q('めちゃくちゃ期待！'), q('🚀'), 1))
        OO.append('(%s,%s,%s,%s,%d)' % (q(pid), q('b'), q('いまは様子見'), q('👀'), 2))

    sql = ['-- ============================================================',
           '-- NEWFOR 読者の投票「今日の1件」 1年ぶんの出題',
           '--',
           '-- pollgen.py が作っています。手で書き足さないでください。',
           '-- Supabase の SQL Editor に貼って、1回だけ実行してください。',
           '-- schema.sql を実行済みであることが前提です。',
           '--',
           '-- 1日1件。その日のうちだけ受け付けます（closes_at を翌0時にしています）。',
           '-- 同じ端末からは1件につき1票までです（newfor_votes の unique 制約）。',
           '-- ============================================================',
           '',
           'insert into public.newfor_polls (id, question, kind, opens_at, closes_at) values',
           ',\n'.join(PP),
           'on conflict (id) do update set question = excluded.question,',
           '  opens_at = excluded.opens_at, closes_at = excluded.closes_at;',
           '',
           'insert into public.newfor_poll_options (poll_id, key, label, emoji, sort) values',
           ',\n'.join(OO),
           'on conflict (poll_id, key) do update set label = excluded.label, emoji = excluded.emoji;',
           '']
    os.makedirs('gh/supabase', exist_ok=True)
    io.open('gh/supabase/poll.sql', 'w', encoding='utf-8').write('\n'.join(sql))

    print('-> gh/assets/poll.js  %d日ぶん（%.0fKB）／出題のもと %d件'
          % (len(idx), os.path.getsize('gh/assets/poll.js') / 1024.0, len(order)))
    print('-> gh/supabase/poll.sql  %.0fKB（Supabaseで1回実行）'
          % (os.path.getsize('gh/supabase/poll.sql') / 1024.0))
    for d, it in days[:3]:
        print('     %s  %s %s「%s」' % (d, it['co'], it['date'], it['title'][:26]))


if __name__ == '__main__':
    main()
