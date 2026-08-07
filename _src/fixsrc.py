# -*- coding: utf-8 -*-
"""出典と発表日を companies/*.py の evsrc に書き戻す

■ 発表日を採るときの線引き

出典を1件ずつ開いて掲載日を読み取りました。ただし、読み取れた日を
そのまま「発表日」として出してよいとは限りません。

  掲載日が年表の月と同じ         … その月の発表。日まで出す
  掲載日が年表の月より前         … 先に発表して、あとで動いた。日は持つが、
                                    画面では月のままにして「発表は◯月◯日」と書く
  掲載日が年表の月より後         … これは「あとから振り返って書かれたもの」で、
                                    発表日ではありません。採りません

3つめが大事です。たとえば「2025年4月のセグメント再編」を2026年5月の決算短信で
知ったとき、2026年5月は発表日ではありません。ここを混ぜると、日付が嘘になります。
"""
import io, re, sys, glob, os, importlib, calendar, json

sys.path.insert(0, 'companies')

# ── 出典を開いて読み取れた掲載日 ──
DATES = {
 "202608-rakuten-2":"2026-08-04","202608-persol-1":"2026-08-01","202607-mhi-1":"2026-07-29",
 "202607-lycorp-1":"2026-07-02","202606-mhi-1":"2026-06-01","202604-murata-1":"2026-04-01",
 "202604-itochu-1":"2026-04-07","202604-dena-1":"2026-04-27","202603-mhi-1":"2026-03-02",
 "202603-dena-1":"2026-03-19","202601-hitachi-1":"2026-01-06","202601-lycorp-1":"2026-01-30",
 "202511-murata-1":"2025-11-25","202511-softbank-1":"2025-11-11","202510-murata-1":"2025-10-08",
 "202509-nissan-1":"2025-09-22","202509-sony-1":"2025-09-29","202507-nissan-1":"2025-07-15",
 "202507-nec-1":"2025-06-23","202506-honda-1":"2025-06-17","202505-mhi-1":"2025-05-16",
 "202504-itochu-1":"2025-04-21","202504-toyota-1":"2025-02-05","202503-murata-1":"2025-03-13",
 "202503-jreast-1":"2025-02-04","202501-cyberagent-1":"2025-01-10",

 "202608-rakuten-1":"2026-08-03","202608-kddi-1":"2026-08-05","202607-mitsui-1":"2026-07-22",
 "202606-murata-2":"2026-06-25","202605-rakuten-1":"2026-05-20","202604-mhi-1":"2026-04-18",
 "202603-rakuten-1":"2026-03-17","202603-fastretailing-1":"2026-03-02","202602-mhi-2":"2026-02-24",
 "202601-nissan-1":"2026-01-23","202601-kddi-1":"2026-01-22","202511-nissan-1":"2025-11-06",
 "202511-cyberagent-1":"2025-10-30","202509-itochu-1":"2025-09-26","202508-fujitsu-3":"2025-01-06",
 "202507-fujitsu-1":"2025-05-26","202506-mitsui-1":"2025-06-30","202504-murata-1":"2025-04-15",
 "202504-mitsui-2":"2025-04-03","202503-nissan-1":"2025-03-31","202503-dena-1":"2025-03-31",
 "202501-lycorp-1":"2025-01-06",

 "202608-fujifilm-1":"2026-08-03","202607-murata-1":"2026-07-09","202607-cyberagent-1":"2026-07-31",
 "202606-murata-1":"2026-06-03","202605-mitsui-2":"2026-05-29","202604-hitachi-2":"2026-04-22",
 "202604-persol-1":"2026-04-24","202602-mhi-1":"2026-02-27","202601-mhi-1":"2026-01-26",
 "202601-dena-1":"2026-01-29","202511-nintendo-1":"2025-11-27","202511-canon-1":"2025-11-28",
 "202510-docomo-1":"2025-09-26","202509-nintendo-1":"2025-09-30","202508-itochu-1":"2025-08-08",
 "202507-mhi-1":"2025-07-29","202507-dena-1":"2025-07-22","202505-nissan-1":"2025-05-13",
 "202504-fujitsu-1":"2025-04-22","202504-mitsui-1":"2025-04-09","202504-kddi-1":"2025-04-10",
 "202503-itochu-1":"2025-03-31","202502-dena-1":"2025-02-03",

 "202608-itochu-1":"2026-08-03","202607-honda-1":"2026-07-16","202606-mhi-2":"2026-06-02",
 "202605-mitsui-1":"2026-05-08","202604-nissan-1":"2025-03-27","202604-sony-1":"2026-04-14",
 "202603-itochu-1":"2026-03-24","202602-persol-1":"2026-02-25","202601-mitsui-1":"2026-01-28",
 "202512-honda-1":"2025-12-16","202511-mhi-1":"2025-11-07","202510-murata-2":"2025-10-02",
 "202509-hitachi-1":"2025-09-24","202509-mhi-1":"2025-09-30","202508-nintendo-1":"2025-08-27",
 "202507-mitsui-1":"2025-07-31","202506-murata-1":"2025-06-16","202505-nintendo-1":"2025-05-19",
 "202504-ajinomoto-1":"2025-04-24","202504-dena-1":"2025-04-14","202503-mitsui-1":"2025-03-12",
 "202501-itochu-1":"2025-01-10","202604-honda-1":"2026-05-14",
}

# 採らないと決めたもの（理由つき）
SKIP = {
 "202603-ajinomoto-1": "出典URLが差し替わっていて、別の決算資料を指している。URLごと直す必要がある",
 "202603-docomo-1":    "読み取れた日が2019年で、記録（2026.03）と7年ずれている。別の出来事の可能性",
 "202504-recruit-1":   "2026年5月の決算短信。2025年4月の出来事の発表日ではない",
 "202510-itochu-1":    "2026年3月の資料。2025年10月の出来事の発表日ではない",
 "202603-softbank-2":  "2026年5月公表の決算短信。出来事より後に書かれたもの",
 "202507-jreast-1":    "PDFに掲載日の記載がなかった",
 "202504-lycorp-1":    "沿革ページで、本文に掲載日がなかった",
}

# ── 出典がまだ無かったものに、新しく足す出典 ──
NEWSRC = {
 "202606-nintendo-1": ("https://www.nintendo.co.jp/corporate/release/2026/260625.html","任天堂 ニュースリリース","2026-06-25"),
 "202507-shiseido-1": ("https://corp.shiseido.com/jp/ir/pdf/ir20250514_182.pdf","資生堂 IR資料","2025-05-14"),
 "202502-sevenandi-1":("https://www.sej.co.jp/company/news_release/news/2025/202504231330.html","セブン‐イレブン・ジャパン ニュースリリース","2025-04-23"),
 "202501-panasonic-1":("https://news.panasonic.com/jp/press/jn250108-5","パナソニック プレスリリース","2025-01-08"),
 "202408-sevenandi-1":("https://corporate.couche-tard.com/2024-08-19-ALIMENTATION-COUCHE-TARD-CONFIRMS-FRIENDLY-PROPOSAL-SENT-TO-SEVEN-i-HOLDINGS","アリマンタシォン・クシュタール プレスリリース","2024-08-19"),
 "202406-shiseido-1": ("https://corp.shiseido.com/jp/ir/pdf/ir20240621_083.pdf","資生堂 IR資料","2024-06-21"),
 "202302-itochu-1":   ("https://www.itochu.co.jp/ja/news/press/2023/230110.html","伊藤忠商事 ニュースリリース","2023-01-10"),
 "202302-cyberagent-1":("https://www.donuts.ne.jp/news/2023/0215_openrec/","DONUTS ニュースリリース（譲受側）","2023-02-15"),
 "202301-hitachi-1":  ("https://www.hitachi.com/content/dam/hitachi/global/ja_jp/press/articles/2021/04/0428d/f_0428d.pdf","日立製作所 ニュースリリース","2021-04-28"),
 "202301-sony-1":     ("https://www.sony.jp/CorporateCruise/Press/202211/22-1129/index.html","ソニー ニュースリリース","2022-11-29"),
 "202203-docomo-1":   ("https://www.docomo.ne.jp/info/news_release/2021/12/23_00.html","NTTドコモ 報道発表資料","2021-12-23"),
 "202109-sony-1":     ("https://www.sony.jp/professional/News/newsrelease/20210917/index.html","ソニー ニュースリリース","2021-09-17"),
 "202103-jreast-2":   ("https://www.jreast.co.jp/press/2021/20220216_ho01.pdf","JR東日本 プレスリリース","2022-02-16"),
 "2021-jreast-1":     ("https://www.jreast.co.jp/press/2021/20211005_ho01.pdf","JR東日本 プレスリリース","2021-10-05"),
 "202009-hitachi-1":  ("https://www.hitachi.com/content/dam/hitachi/global/ja_jp/press/articles/2019/12/1218c/f_1218c-1.pdf","日立製作所 ニュースリリース","2019-12-18"),
 "201805-nissan-1":   ("https://global.nissannews.com/ja-JP/releases/230119-02-j","日産自動車 ニュースリリース","2023-01-19"),
 "201803-panasonic-1":("https://news.panasonic.com/jp/press/data/2018/03/jn180301-1/jn180301-1.html","パナソニック プレスリリース","2018-03-01"),
 "201604-recruit-1":  ("https://prtimes.jp/main/html/rd/p/000000173.000010032.html","PR TIMES（リクルート）","2016-02-25"),
 "2016-panasonic-1":  ("https://news.panasonic.com/jp/topics/147140","パナソニック トピックス","2016-07-21"),
 "201506-shiseido-1": ("https://corp.shiseido.com/jp/ir/pdf/ir20150630_063.pdf","資生堂 IR資料","2015-06-30"),
 "201301-cyberagent-1":("https://prtimes.jp/main/html/rd/p/000000130.000000258.html","PR TIMES（サイバーエージェント）","2013-01-31"),
 "201001-shiseido-1": ("https://corp.shiseido.com/jp/ir/pdf/ir20100115_125.pdf","資生堂 IR資料","2010-01-15"),
}
# パナソニックのテスラ株売却は、Bloomberg の記事しか見つかりませんでした。
# NEWFOR は「プレスリリース・IR資料・公式サイト」だけを出典にすると書いているので、
# ここは出典なしのまま残します。方針を変えてまで埋める場所ではありません。


def month_end(ym):
    y = int(ym[:4])
    if len(ym) == 4:
        return '%04d-12-31' % y
    m = int(ym[5:7])
    return '%04d-%02d-%02d' % (y, m, calendar.monthrange(y, m)[1])


def jp(d):
    return '%d年%d月%d日' % (int(d[:4]), int(d[5:7]), int(d[8:10]))


import newsdata
IT = {i['slug']: i for i in newsdata.build()}

# slug -> (companyファイル, evsrcのキー)
KEY = {s: (i['coslug'], '%s|%s' % (i['ym'], i['title'])) for s, i in IT.items()}

edits = {}     # coslug -> {key: (url, label)}
skipped, added_date, added_src, late = [], 0, 0, []

for slug, d in DATES.items():
    it = IT.get(slug)
    if not it or slug in SKIP:
        continue
    if d > month_end(it['ym']):
        late.append((slug, it['ym'], d)); continue
    lab = it['srclabel'] or ''
    if re.search(r'20\d\d年\d{1,2}月\d{1,2}日', lab):
        continue                                   # すでに日付が入っている
    lab2 = (lab + '（%s）' % jp(d)) if lab else jp(d)
    edits.setdefault(it['coslug'], {})[KEY[slug][1]] = (it['src'], lab2)
    added_date += 1

for slug, (url, lab, d) in NEWSRC.items():
    it = IT.get(slug)
    if not it:
        print('!! %s が見あたらない' % slug); continue
    lab2 = lab
    if d and d <= month_end(it['ym']):
        lab2 = lab + '（%s）' % jp(d)
    elif d:
        lab2 = lab + '（%s 発表）' % jp(d)          # 出来事より後の資料は、そう書く
    edits.setdefault(it['coslug'], {})[KEY[slug][1]] = (url, lab2)
    added_src += 1

# ── companies/*.py の evsrc を書き換える ──
def q(s):
    return "'" + str(s).replace('\\', '\\\\').replace("'", "\\'") + "'"

n = 0
for coslug, kv in sorted(edits.items()):
    p = 'companies/%s.py' % coslug
    C = importlib.import_module(coslug).C
    ES = dict(C.get('evsrc') or {})
    ES.update({k: [v[0], v[1]] for k, v in kv.items()})
    blk = 'evsrc={\n' + ''.join(' %s: [%s, %s],\n' % (q(k), q(v[0]), q(v[1]))
                                for k, v in sorted(ES.items())) + '},\n'
    s = io.open(p, encoding='utf-8').read()
    i = s.index('evsrc='); b = s.index('{', i); depth = 0
    for j in range(b, len(s)):
        if s[j] == '{': depth += 1
        elif s[j] == '}':
            depth -= 1
            if depth == 0: break
    while j < len(s) and s[j] in '},\n': j += 1
    io.open(p, 'w', encoding='utf-8').write(s[:i] + blk + s[j:])
    n += 1
    print('  %-14s %d件' % (coslug, len(kv)))

print('\n書き換えた企業ファイル: %d' % n)
print('発表日を足した: %d件 / 出典を新しく足した: %d件' % (added_date, added_src))
print('採らなかった（出来事より後の資料）: %d件' % len(late))
for x in late: print('   ', x)
print('採らなかった（理由あり）: %d件' % len(SKIP))
for k, v in SKIP.items(): print('    %-20s %s' % (k, v))
