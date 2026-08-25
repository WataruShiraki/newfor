# -*- coding: utf-8 -*-
"""「数字1枚」カード28枚に添える投稿文を、カードと同じ素材から作る

カードの絵と投稿文で数字がズレる事故を防ぐため、素材は posts/big/cards.json
の1本だけから取ります。bigcard.py が書き、ここが読みます。

守っている決まり
  1. _src/KOTOBA.md（最上位）… 挑戦を否定する言い方は1語も入れません。
  2. _src/SNS_BUNTAI.md … 1文40字以内。接続詞の直後に読点を置かない。
     体言止めを混ぜる。副詞と定型句を使わない。
  3. 数はすべて companies/ の実データ。推測で足しません。

媒体ごとの置き方（_src/SNS_BUNTAI.md より）
  Instagram … キャプションにURLを書いても飛べません。プロフィールへ送ります。
  X         … 本体にURLを置きません。ぶら下げの1本目に置きます。
  Threads   … 本文の最後に1つ。問いかけで終えて、返信が来る形にします。

使い方
  python3 bigcard.py && python3 bigpost.py
  点検は python3 checkposts.py posts/big_posts.md
"""
import io, json, sys, datetime

CARDS = json.load(io.open('posts/big/cards.json', encoding='utf-8'))

# Instagram は月・水・金の20時（_src/calendar のとおり）。
# 開始日は引数で変えられます: python3 bigpost.py 2026-08-10
START = (datetime.date(*[int(x) for x in sys.argv[1].split('-')])
         if len(sys.argv) > 1 else datetime.date(2026, 8, 10))

MONEY_URL = 'https://newfor.jp/articles/newbusiness-money-ranking/'
TOP_URL = 'https://newfor.jp'
CO_URL = 'https://newfor.jp/companies/%s/'

IG_TAGS = '#スタートアップ #起業 #資金調達 #新規事業 #事業開発'
TH_TAG = '#スタートアップ'
IG_CTA = 'プロフィールのリンクからどうぞ。'


def rank_line(m):
    """順位の言い方。1位のときだけ文の形を変えます。

    「この1件はいちばん大きい1件です」と重ねると読みにくいためです。
    """
    if m['rank'] == 1:
        return 'その中でいちばん大きいのが、この1件です。'
    return 'この1件は%d番目です。' % m['rank']


def money(m):
    co, disp, ev = m['co'], m['disp'], m['ev']
    when = '%d年%d月、%s。' % (m['y'], m['m'], ev)
    tot = m['total']
    place = ('払った額がわかる%d件の中で、いちばん大きい1件です。' % tot
             if m['rank'] == 1 else
             '払った額がわかる%d件のうち、%d番目の大きさです。' % (tot, m['rank']))

    ig = ('%sが、%s。\n\n%s\n%s\n\n'
          '額の大きい順に並べた一覧を newfor.jp に置いています。\n%s\n\n%s'
          % (co, disp, when, place, IG_CTA, IG_TAGS))

    x = ('%sが%s。\n\n%s\n\n新規事業に払った額を%d件ぶん集めました。\n%s'
         % (co, disp, when, tot, rank_line(m)))
    xr = '額の大きい順に並べた一覧です。\n%s' % MONEY_URL

    th = ('%sが%s。\n\n%s\n\n新規事業に払った額を%d件ぶん集めて、大きい順に並べました。\n'
          '%s\n\nみなさんが「これは大きい」と思う1件、どれですか？\n\n%s\n\n%s'
          % (co, disp, when, tot, rank_line(m), MONEY_URL, TH_TAG))
    return ig, x, xr, th


def count(m):
    co, n, live = m['co'], m['n'], m['live']
    yrs = m['hi'] - m['lo']
    span = '%d年から%d年まで、%d年ぶんの挑戦です。' % (m['lo'], m['hi'], yrs)
    url = CO_URL % m['slug']

    ig = ('%sの新規事業、%d件。\n\n%s\nいま動いているのが%d件。\n'
          '1件ずつ開始年と出典をつけて年表にしました。\n\n'
          '年表は newfor.jp で見られます。\n%s\n\n%s'
          % (co, n, span, live, IG_CTA, IG_TAGS))

    x = ('%sの新規事業を数えたら%d件ありました。\n\n%s\n\n'
         'いま動いているのが%d件。\n1件ずつ開始年と出典をつけています。'
         % (co, n, span, live))
    xr = '年表はこちらです。\n%s' % url

    th = ('%sの新規事業、%d件。\n\n%s\nいま動いているのが%d件です。\n\n'
          'この中に、ご存じの事業はありますか？\n\n%s\n\n%s'
          % (co, n, span, live, url, TH_TAG))
    return ig, x, xr, th


def allcard(m):
    tot, nco, live = m['tot'], m['nco'], m['live']
    yrs = m['hi'] - m['lo']
    span = '%d社ぶん、%d年から%d年まで。' % (nco, m['lo'], m['hi'])

    ig = ('大企業の新規事業、%s件。\n\n%s\n%d年ぶんの挑戦を1件ずつ並べました。\n'
          '続いているのが%s件です。\n\n全件に開始年と出典をつけています。\n'
          'newfor.jp で見られます。\n%s\n\n%s'
          % ('{:,}'.format(tot), span, yrs, '{:,}'.format(live), IG_CTA, IG_TAGS))

    x = ('大企業の新規事業を%s件、集めました。\n\n%s\n\n'
         '続いているのが%s件。\n全件に出典をつけています。'
         % ('{:,}'.format(tot), span, '{:,}'.format(live)))
    xr = '1件ずつ見られます。\n%s' % TOP_URL

    th = ('大企業の新規事業、%s件。\n\n%s\n続いているのが%s件です。\n\n'
          '全件に開始年と出典をつけました。\n\n'
          'どの会社の年表から見てみたいですか？\n\n%s\n\n%s'
          % ('{:,}'.format(tot), span, '{:,}'.format(live), TOP_URL, TH_TAG))
    return ig, x, xr, th


def setupcard(m):
    s, tot = m['setup'], m['tot']
    ig = ('新規事業のために会社を建てた回数、%d回。\n\n'
          '記録した%s件のうち%d件が「会社をつくる」でした。\n'
          '設立・新設・分社・子会社化を数えています。\n\n'
          '1件ずつ newfor.jp で見られます。\n%s\n\n%s'
          % (s, '{:,}'.format(tot), s, IG_CTA, IG_TAGS))

    x = ('新規事業のために会社を建てた回数、%d回。\n\n'
         '記録した%s件のうち%d件。\n\n設立・新設・分社・子会社化を数えました。'
         % (s, '{:,}'.format(tot), s))
    xr = '1件ずつ見られます。\n%s' % TOP_URL

    th = ('新規事業のために会社を建てた回数、%d回。\n\n'
          '記録した%s件のうち%d件が「会社をつくる」でした。\n\n'
          '新しいことを始めるとき、別会社にしますか。それとも中でやりますか？\n\n%s\n\n%s'
          % (s, '{:,}'.format(tot), s, TOP_URL, TH_TAG))
    return ig, x, xr, th


MAKER = {'money': money, 'count': count, 'all': allcard, 'setup': setupcard}


# ── 出す順 ──
#
# 同じ型が続くと、プロフィールに並んだときに単調に見えます。
# 「払った額」と「会社ごとの件数」を1枚ずつ交互に置きます。
# 全体の数（all）は最初に、会社を建てた回数（setup）は最後に置きます。
def order(cards):
    by = {}
    for c in cards:
        by.setdefault(c['meta']['kind'], []).append(c)
    money_, count_ = by.get('money', []), by.get('count', [])
    seq = by.get('all', [])[:]
    for i in range(max(len(money_), len(count_))):
        if i < len(money_):
            seq.append(money_[i])
        if i < len(count_):
            seq.append(count_[i])
    seq += by.get('setup', [])
    return seq


def slots(n, start):
    """月・水・金の20時を n 個ぶん。開始日以降のいちばん近い月曜から数えます。"""
    d = start
    while d.weekday() != 0:
        d += datetime.timedelta(days=1)
    out, wk = [], 0
    while len(out) < n:
        for off in (0, 2, 4):          # 月・水・金
            if len(out) == n:
                break
            out.append(d + datetime.timedelta(days=wk * 7 + off))
        wk += 1
    return out


WD = '月火水木金土日'
SEQ = order(CARDS)
DAYS = slots(len(SEQ), START)

out = ['# 「数字1枚」カード28枚の投稿文',
       '',
       '`python3 bigcard.py && python3 bigpost.py` で作り直せます。',
       '数はすべて companies/ の実データから引いています。手で書き替えないでください。',
       '',
       '画像は `posts/big/png/<タグ>.png`。1投稿につき1枚です。',
       '',
       '出す前に `python3 checkposts.py posts/big_posts.md` を通してください。',
       '',
       '---',
       '',
       '## 出す順（Instagram 月・水・金 20時）',
       '',
       '払った額と会社ごとの件数を、1枚ずつ交互に置いています。',
       '同じ型が続くと、プロフィールに並んだときに単調に見えるためです。',
       '',
       '| 出す日 | カード | 中身 |',
       '|---|---|---|']

for d, c in zip(DAYS, SEQ):
    out.append('| %d/%d（%s） | `%s` | %s %s |'
               % (d.month, d.day, WD[d.weekday()], c['tag'],
                  c['co'].replace('&amp;', '&'),
                  c['big'].replace('<span class="n">', '').replace('<span class="u">', '')
                          .replace('</span>', '')))

out += ['',
        'XとThreadsは毎日出せます。上の順に上から使ってください。',
        '',
        '---', '']

for i, c in enumerate(SEQ):
    m = c['meta']
    ig, x, xr, th = MAKER[m['kind']](m)
    d = DAYS[i]
    out += ['## %d. %s（%d/%d %s）' % (i + 1, c['tag'], d.month, d.day, WD[d.weekday()]),
            '',
            '画像 … `posts/big/png/%s.png`' % c['tag'],
            '',
            '### Instagram', '', '```', ig, '```', '',
            '### X（本体・URLなし）', '', '```', x, '```', '',
            '### X（ぶら下げ1本目）', '', '```', xr, '```', '',
            '### Threads', '', '```', th, '```', '',
            '---', '']

io.open('posts/big_posts.md', 'w', encoding='utf-8').write('\n'.join(out))
print('投稿文を %d 枚ぶん書きました → posts/big_posts.md' % len(CARDS))
print('  点検: python3 checkposts.py posts/big_posts.md')
