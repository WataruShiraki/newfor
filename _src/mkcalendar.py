# -*- coding: utf-8 -*-
"""SNSの配信カレンダーを、いまの実データから作る

企業の数や記事の数が変わっても、これを流し直せばカレンダーが作り直せます。
ネタは companies/ と articles/ から拾うので、実在しない話が入りません。

使い方: python3 mkcalendar.py 2026-08-10 28   （開始日と日数）
"""
import io,os,sys,glob,importlib,datetime

sys.path.insert(0,'companies'); sys.path.insert(0,'articles')

START=sys.argv[1] if len(sys.argv)>1 else '2026-08-10'
DAYS=int(sys.argv[2]) if len(sys.argv)>2 else 28

CO=[]
for f in sorted(glob.glob('companies/*.py')):
    n=os.path.basename(f)[:-3]
    if n.startswith('_'): continue
    c=importlib.import_module(n).C
    CO.append((c['slug'],c['name'],len(c['timeline'])))
CO.sort(key=lambda x:-x[2])

ART=[]
for f in sorted(glob.glob('articles/a0*.py')):
    A=importlib.import_module(os.path.basename(f)[:-3]).A
    ART.append((A['slug'],A['h1'].replace('<br>','')))

WD='月火水木金土日'

# 曜日ごとのテーマ。( テーマ名, 送り先の作り方 )
THEME={
 0:('1社の年表から見つけた1つのこと','企業ページ'),
 1:('記事の中の1節を切り出す','記事'),
 2:('払った額の1件','投資額ランキング'),
 3:('新規事業の言葉を1つ','用語の記事'),
 4:('2社を並べて比べる','企業ページ2つ'),
 5:('今週足した記録のまとめ','企業DB'),
 6:('問いかけ。返信を集める','リンクなし'),
}

# 媒体ごとの投稿枠（曜日 -> [(媒体, 時刻)]）
SLOT={
 0:[('X','7:30'),('Threads','12:15'),('X','21:00'),('Instagram','20:00')],
 1:[('X','7:30'),('Threads','12:15'),('note','19:00'),('X','21:00')],
 2:[('X','7:30'),('Threads','12:15'),('Instagram','20:00'),('TikTok','20:30'),('X','21:00')],
 3:[('X','7:30'),('Threads','12:15'),('X','21:00')],
 4:[('X','7:30'),('Threads','12:15'),('Instagram','20:00'),('X','21:00')],
 5:[('Threads','12:15'),('TikTok','20:30'),('X','21:00')],
 6:[('Threads','12:15'),('X','21:00')],
}

TAG={
 'X':'なし（初期のみ #新規事業 を1個まで）',
 'Threads':'#新規事業（1個だけ）',
 'Instagram':'#新規事業 #事業開発 #社内起業 #新規事業担当者 #オープンイノベーション（5個）',
 'TikTok':'#新規事業 #事業開発 #大企業 #ビジネス #会社員（5個）',
 'note':'#新規事業 #事業開発 #社内起業 #オープンイノベーション #新規事業担当者 #大企業 #ビジネス ＋ そのときの公式お題タグ',
}

d0=datetime.date(*[int(x) for x in START.split('-')])
out=[]
out.append('# NEWFOR 配信カレンダー（%s から %d日ぶん）\n'%(START,DAYS))
out.append('`python3 mkcalendar.py 開始日 日数` で作り直せます。'
           'ネタは companies/ と articles/ の実データから拾っています。\n')

ci=ai=0
for i in range(DAYS):
    d=d0+datetime.timedelta(days=i)
    w=d.weekday()
    theme,dest=THEME[w]
    out.append('\n## %d/%d（%s）%s\n'%(d.month,d.day,WD[w],theme))
    # ネタを決める
    if w==0:
        s,n,c=CO[ci%len(CO)]; ci+=1
        neta='%s（%d件）／ https://newfor.jp/companies/%s/'%(n,c,s)
    elif w==1:
        s,h=ART[ai%len(ART)]; ai+=1
        neta='%s ／ https://newfor.jp/articles/%s/'%(h,s)
    elif w==2:
        neta='投資額ランキングから1件 ／ https://newfor.jp/articles/newbusiness-money-ranking/'
    elif w==3:
        neta='新規事業の言葉を1つ ／ https://newfor.jp/articles/newbusiness-words/'
    elif w==4:
        a=CO[ci%len(CO)]; ci+=1; b=CO[ci%len(CO)]; ci+=1
        neta='%s と %s を並べる ／ /companies/%s/ と /companies/%s/'%(a[1],b[1],a[0],b[0])
    elif w==5:
        neta='今週足した記録のまとめ ／ https://newfor.jp/companies/'
    else:
        neta='問いかけ。リンクなし。返信を集める日'
    out.append('- ネタ … %s\n'%neta)
    out.append('\n| 時刻 | 媒体 | タグ |\n|---|---|---|\n')
    for m,t in sorted(SLOT[w],key=lambda x:(int(x[1].split(':')[0]),int(x[1].split(':')[1]))):
        out.append('| %s | %s | %s |\n'%(t,m,TAG[m]))

n_by={}
for i in range(DAYS):
    w=(d0+datetime.timedelta(days=i)).weekday()
    for m,t in SLOT[w]: n_by[m]=n_by.get(m,0)+1
out.append('\n---\n\n## 合計\n\n| 媒体 | %d日ぶん | 1週あたり |\n|---|---|---|\n'%DAYS)
for m in ['X','Threads','Instagram','TikTok','note']:
    out.append('| %s | %d本 | %.1f本 |\n'%(m,n_by[m],n_by[m]*7.0/DAYS))
out.append('| **合計** | **%d本** | **%.1f本** |\n'%(sum(n_by.values()),sum(n_by.values())*7.0/DAYS))

os.makedirs('posts',exist_ok=True)
io.open('posts/calendar.md','w',encoding='utf-8').write(''.join(out))
print('posts/calendar.md を作りました（%d日ぶん / 合計%d本）'%(DAYS,sum(n_by.values())))
