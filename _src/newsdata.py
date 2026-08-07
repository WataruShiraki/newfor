# -*- coding: utf-8 -*-
"""NEWS（新規事業ニュース）の元データを、1か所だけで組み立てる

これまで年表の1件は、トップの「新規事業NEWS」・企業ページの一覧・稼働チャートの
3か所に出ていましたが、行き先はどれも企業ページの先頭でした。読みたいのは
その1件なのに、企業ページの上に飛ばされる。それを直すために、1件に1ページを
用意します。そのページの住所と中身を決めるのが、このファイルです。

■ 住所（URL）に日付を入れない理由

  /news/202608-denso-1/

年月＋企業＋その月の連番です。日（08.05 の 05）は入れません。
いま日まで確認できているのは1076件中409件で、残りはこれから出典を1件ずつ
開いて埋めていきます。もし住所に日を入れていると、日を直すたびに住所が変わり、
SNSに貼ったリンクも検索の順位も、そのたびに捨てることになります。

■ 日付の扱い（ここを間違えると、事実を曲げることになります）

年表の「2017.09」は、その事業が**始まった月**です。プレスリリースの日付では
ありません。実際、NSITEXE は 2017年9月に設立ですが、発表は 2017年8月8日でした。
同じように月がズレている記録が55件あります。

そこで、こう決めます。

  出典から読み取れた発表日が、年表の年月と**同じ月**なら … 日まで出す（発表日）
  違う月なら                                             … 年表は月のまま。
                                                            発表日は別に書く

「たぶんこの日だろう」で日を作ることは、絶対にしません。

■ 発表日の読み取り先

  1. 出典ラベルの中の「（2026年3月19日／…）」
  2. 出典URLの中の8桁「/2026/20260805-01/」

1を先に見ます。1のほうが人の手で確認した情報だからです。
"""
import os, re, sys, glob, importlib

sys.path.insert(0, 'companies')

# ─────────────────────────────────────────────
# 会社のデータを読む
# ─────────────────────────────────────────────
def load_companies():
    out = []
    for f in sorted(glob.glob('companies/*.py')):
        n = os.path.basename(f)[:-3]
        if n.startswith('_'):
            continue
        out.append(importlib.import_module(n).C)
    return out


def esrc(ES, ymd, ev):
    """出来事ごとの出典を引く（compgen.py と同じ引き方）"""
    if not ES:
        return None
    return ES.get('%s|%s' % (ymd, ev)) or ES.get(ymd) or ES.get(ymd[:4])


# ─────────────────────────────────────────────
# 発表日を読み取る
# ─────────────────────────────────────────────
def press_date(url, label):
    """出典から発表日（YYYY-MM-DD）を読み取る。読めなければ None。

    どこから読んだかも返します（'label' か 'url'）。あとで見直すときに、
    どちらを信じたのかが分からないと直せないためです。
    """
    m = re.search(r'(20\d\d)年(\d{1,2})月(\d{1,2})日', label or '')
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31:
            return '%04d-%02d-%02d' % (y, mo, d), 'label'
    m = re.search(r'(?<!\d)(20\d\d)(\d\d)(\d\d)(?!\d)', url or '')
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31:
            return '%04d-%02d-%02d' % (y, mo, d), 'url'
    return None, None


# ─────────────────────────────────────────────
# 1件ぶんを組み立てる
# ─────────────────────────────────────────────
def build():
    CO = load_companies()
    items = []
    for c in CO:
        ES = c.get('evsrc') or {}
        # その企業の中で「年月ごとの連番」を振る。同じ年月に2件以上ある
        # ことがあるので（最大3件）、連番がないと住所がぶつかります。
        seq = {}
        for ymd, title, note, live in c['timeline']:
            ymd = str(ymd)
            # 年しか分かっていない記録が16件あります（「2006 あした会議 開始」など）。
            # 月をでっちあげず、年のままの1件として扱います。
            has_month = bool(re.fullmatch(r'\d{4}\.\d{1,2}', ymd))
            key = ymd.replace('.', '')          # '2026.08' -> '202608' / '2006' -> '2006'
            seq[key] = seq.get(key, 0) + 1
            slug = '%s-%s-%d' % (key, c['slug'], seq[key])

            src = esrc(ES, ymd, title)
            url = src[0] if src else ''
            label = src[1] if src else ''
            pd, pdfrom = press_date(url, label)

            # 発表日を「この出来事の日付」として出してよいのは、同じ月のときだけ。
            # 年しか分かっていない記録では、月を作らないので day には上げません。
            same_month = bool(pd) and has_month and pd[:7].replace('-', '.') == ymd
            items.append(dict(
                slug=slug,
                ym=ymd,                       # 年表の年月（＝出来事の月）
                year=int(ymd[:4]),
                month=(int(ymd[5:7]) if has_month else 0),
                title=title,
                note=note or '',
                live=bool(live),
                co=c['name'],
                colegal=c['legal'],
                coslug=c['slug'],
                ind=c['ind'],
                src=url,
                srclabel=label,
                press=pd or '',               # 読み取れた発表日（そのまま保存）
                pressfrom=pdfrom or '',
                # 画面に出す日付
                date=(pd if same_month else ymd.replace('.', '-')),
                prec=('day' if same_month else ('month' if has_month else 'year')),
                # 「発表と開始がズレている」は、それ自体が読みどころになります
                gap=(pd if (pd and not same_month) else ''),
            ))
    # 新しい順に並べる。
    # 年月だけで並べると、同じ月の中で 04.28 より 04.02 が上に来てしまいます
    # （実際にそうなっていました）。日が分かっているものは日で、分からない
    # ものは月末ではなく月の先頭あつかいにして、いちばん下に置きます。
    def key(i):
        if i['prec'] == 'day':
            return i['date']
        if i['prec'] == 'month':
            return i['date'] + '-00'
        return i['date'] + '-00-00'
    items.sort(key=lambda i: (key(i), i['co'], i['slug']), reverse=True)
    for i, it in enumerate(items):
        it['i'] = i
    return items


def by_slug(items):
    return {i['slug']: i for i in items}


def path(it):
    return '/news/%s/' % it['slug']


def disp_date(it, dot=True):
    """2026.08.05 ／ 2026.08 の形にする"""
    s = it['date'].replace('-', '.' if dot else '-')
    return s


if __name__ == '__main__':
    IT = build()
    nd = sum(1 for i in IT if i['prec'] == 'day')
    ng = sum(1 for i in IT if i['gap'])
    ns = sum(1 for i in IT if not i['src'])
    print('NEWS %d件' % len(IT))
    print('  日まで確定 %d件（%.0f%%）／月のまま %d件' % (nd, nd * 100.0 / len(IT), len(IT) - nd))
    print('  発表と開始で月がズレている %d件' % ng)
    print('  出典がまだ無い %d件' % ns)
    print('  住所の重複 %d件' % (len(IT) - len(set(i['slug'] for i in IT))))
    for it in IT[:6]:
        print('   %-26s %-12s %-9s %s' % (it['slug'], it['co'], disp_date(it), it['title'][:26]))
