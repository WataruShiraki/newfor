# -*- coding: utf-8 -*-
"""SNS用の「数字1枚」カードを、実データから作る

わたるさんが選んだ形（2026年8月7日）。ブランドの青ベタに、大きな数字を1つ。
「イメージカラーでブランディングもできるし、インパクトあるし！」

2026年8月7日の直し
  ・数字は横幅ギリギリまで自動でふくらませる（埋もれないように）
  ・会社名を独立させて大きく出す（誰の話かが一目でわかるように）
  ・「新規事業ヒストリーメディア」を必ず題字に入れる

作り方の決まり
  1. 数字は companies/*.py と money.py からしか取りません。
     ここに無い数字は1枚も作りません。推測で埋めない、はサイトと同じです。
  2. 言葉は _src/KOTOBA.md に従います。挑戦を否定する言い方は入れません。
     「買収」「取得」は事実なのでそのまま書きます。
     「失敗」「撤退」「生き残った」は書きません。
  3. 煽りません。驚きは数字に持たせて、言葉は静かにします。

サイズ
  1080 × 1350（4:5）。Instagramのフィードでいちばん縦に長く出せる比率です。

使い方
  python3 bigcard.py && node bigcard.js
"""
import io, os, sys, glob, json, importlib, re

sys.path.insert(0, 'companies')

OUT = 'posts/big'
os.makedirs(OUT, exist_ok=True)

# ── データ ──
CO = []
for f in sorted(glob.glob('companies/*.py')):
    n = os.path.basename(f)[:-3]
    if n.startswith('_'):
        continue
    CO.append(importlib.import_module(n).C)

TOT = sum(len(c['timeline']) for c in CO)
YRS = [int(str(y)[:4]) for c in CO for y, _, _, _ in c['timeline']]
LO, HI = min(YRS), max(YRS)

# 金額は money.py が年表の説明文から拾ったもの。出典は年表の各行についています。
os.system('python3 money.py >/dev/null 2>&1')
PAY = json.load(io.open('/tmp/money.json', encoding='utf-8'))


def esc(t):
    return (str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


CARDS = []


def card(kicker, big, head, proof, tag='', co='', meta=None):
    """meta は投稿文を組むための素材。カードの絵には出ません。

    bigpost.py がこれを読んで、InstagramとXとThreadsの文面を作ります。
    カードと投稿文で数字がズレないように、素材は1か所（ここ）から配ります。
    """
    CARDS.append(dict(kicker=kicker, big=big, head=head, proof=proof,
                      tag=tag, co=co, meta=meta or {}))


# ── 見出しだけは手で書きます ──
#
# 年表の説明文（「Armを取得」）をそのまま見出しにすると、事実は正しいのに
# 「それが何の決断だったのか」が伝わりません。数字はもう大きく出ているので、
# 見出しはその数字の意味を引き受ける場所にします。
#
# 決まりは3つ。
#   ・事実の範囲を出ない。年表と出典にない数や順位（「国内最大」など）は書かない。
#   ・_src/KOTOBA.md に従う。挑戦を否定する言い方は入れない。
#   ・煽らない。静かに書いて、驚きは数字に持たせる。
# 元の説明文は消さずに、下の出典の行へ移します。
#
# 鍵は（会社名, 表示金額）です。順位（money-01）を鍵にすると、データが増えた
# ときに見出しが別のカードへずれます。
HEADS = {
    ('NTTドコモ', '4兆2,500億円'):
        '親会社が、子会社を<br>まるごと引き受けた。',
    ('ソフトバンクグループ', '3兆3,000億円'):
        'スマホの中身を設計する会社を、<br>まるごと。',
    ('セブン&アイ', '2兆2,000億円'):
        'コンビニの会社が、<br>米国の給油所を買いにいった。',
    ('ソフトバンクグループ', '1兆8,000億円'):
        '日本の通信会社が、<br>米国の通信会社を持った。',
    ('ソフトバンクグループ', '1兆7,500億円'):
        '携帯電話事業への、<br>入場券だった。',
    ('伊藤忠商事', '1兆2,000億円'):
        '商社が、中国とタイの<br>巨大企業と手を組んだ。',
    ('NTTドコモ', '1兆1,000億円'):
        '世界で戦うために、<br>米国の通信会社へ出資した。',
    ('日立製作所', '1兆368億円'):
        'モノをつくる会社が、<br>ソフトをつくる会社を迎えた。',
    ('ソフトバンクグループ', '7,700億円'):
        'ゲームをつくる会社へ、<br>フィンランドまで出資した。',
    ('日立製作所', '7,400億円'):
        '電気を送る仕組みを、<br>世界規模で引き受けた。',
    ('三菱UFJ FG', '7,163億円'):
        '銀行が、飛行機に<br>お金を貸す事業を買った。',
    ('キヤノン', '6,655億円'):
        'カメラの会社が、<br>医療機器の会社を迎えた。',
    ('日産自動車', '6,050億円'):
        '1社では届かない場所へ、<br>2社で行くことにした。',
    ('伊藤忠商事', '5,800億円'):
        '商社が、コンビニを<br>自分の事業として抱えた。',
}

# ── 1. 払った額（money.py の109件から）──
rows = sorted(PAY, key=lambda r: -r['yen'])
seen, uniq = set(), []
for r in rows:
    k = (r['co'], r['yen'])
    if k in seen:
        continue          # 「買収を発表」と「子会社化が完了」で同じ額が2回出るため
    seen.add(k)
    uniq.append(r)
rows = uniq

for i, r in enumerate(rows[:14], 1):
    big = re.sub(r'([\d,]+)', r'<span class="n">\1</span>', r['disp'])
    big = re.sub(r'(兆円|億円|兆)', r'<span class="u">\1</span>', big)
    y, m = str(r['date']).split('.')
    card(kicker='新規事業に払った額' + ('｜109件中いちばん大きい1件' if i == 1 else '｜109件中 %d番目' % i),
         co=esc(r['co']),
         big=big,
         head=HEADS.get((r['co'], r['disp'])) or (esc(r['ev']) + '。'),
         proof='%s年%s月、%s。払った額がわかる109件を newfor.jp に大きい順で並べています。'
               % (y, int(m), esc(r['ev'])),
         tag='money-%02d' % i,
         meta=dict(kind='money', co=r['co'], disp=r['disp'], ev=r['ev'],
                   y=int(y), m=int(m), rank=i, total=len(PAY)))

# ── 2. 会社ごとの記録の数 ──
for c in sorted(CO, key=lambda c: -len(c['timeline']))[:12]:
    ys = [int(str(y)[:4]) for y, _, _, _ in c['timeline']]
    n = len(c['timeline'])
    live = sum(1 for x in c['timeline'] if x[3])
    card(kicker='手がけた新規事業の数',
         co=esc(c['name']),
         big='<span class="n">%d</span><span class="u">件</span>' % n,
         head='%d年から%d年まで、<br>%d年ぶんの挑戦。' % (min(ys), max(ys), max(ys) - min(ys)),
         proof='いま動いているのが%d件。1件ずつ出典をつけて newfor.jp に並べています。' % live,
         tag='count-%s' % c['slug'],
         meta=dict(kind='count', co=c['name'], slug=c['slug'], n=n, live=live,
                   lo=min(ys), hi=max(ys)))

# ── 3. 全体 ──
card(kicker='NEWFORが記録している新規事業',
     co='%d年 → %d年' % (LO, HI),
     big='<span class="n">%s</span><span class="u">件</span>' % '{:,}'.format(TOT),
     head='%d社ぶん、%d年ぶんの挑戦の記録。' % (len(CO), HI - LO),
     proof='1件ずつ、開始年と出典をつけて newfor.jp に並べています。',
     tag='all',
     meta=dict(kind='all', tot=TOT, nco=len(CO), lo=LO, hi=HI,
               live=sum(1 for c in CO for x in c['timeline'] if x[3])))

setup = sum(1 for c in CO for x in c['timeline'] if re.search(r'設立|新設|分社|会社化', x[1]))
card(kicker='新規事業のために',
     co='会社を建てた回数',
     big='<span class="n">%d</span><span class="u">回</span>' % setup,
     head='記録した%s件のうち、<br>%d件が「会社をつくる」だった。' % ('{:,}'.format(TOT), setup),
     proof='設立・新設・分社・子会社化を数えました。newfor.jp で1件ずつ見られます。',
     tag='setup',
     meta=dict(kind='setup', setup=setup, tot=TOT, nco=len(CO)))

# ── HTML を書き出す ──
TPL = io.open('bigcard.tpl.html', encoding='utf-8').read()
io.open('%s/index.html' % OUT, 'w', encoding='utf-8').write(
    TPL.replace('__CARDS__', json.dumps(CARDS, ensure_ascii=False)))

# 投稿文はここから作ります（bigpost.py）。素材を2か所に持たないための1本道です。
io.open('%s/cards.json' % OUT, 'w', encoding='utf-8').write(
    json.dumps(CARDS, ensure_ascii=False, indent=1))

print('数字1枚のカードを %d 枚ぶん用意しました → %s/index.html' % (len(CARDS), OUT))
print('  PNGにするには: node bigcard.js')
print('  投稿文にするには: python3 bigpost.py')
