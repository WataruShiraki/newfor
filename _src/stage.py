# -*- coding: utf-8 -*-
"""GitHubのアップロード画面へ渡すファイルを、まとまりごとに用意する

使い方:  python3 stage.py <何番目のまとまりか>
        python3 stage.py list        … まとまりの一覧だけ出す

道の区切り「/」は「~」に置き換えて1枚のファイル名にします。
ブラウザ側で「~」を「/」に戻してから、GitHubの入力欄に渡します。
"""
import io, os, sys, shutil, subprocess

OUT = '/mnt/user-data/outputs/gh-upload'
LIMIT = 2_600_000        # 1まとまりの上限（バイト）
NLIMIT = 260             # 1まとまりの上限（枚数）


def changed():
    out = subprocess.run(['git', 'status', '--porcelain', '-uall'],
                         cwd='gh', capture_output=True, text=True).stdout
    fs = []
    for line in out.splitlines():
        f = line[3:].strip().strip('"')
        p = 'gh/' + f
        if os.path.isfile(p):
            fs.append((f, os.path.getsize(p)))
    # 小さいもの（スクリプトや assets）を先に、NEWSの山を後ろに
    fs.sort(key=lambda x: (x[0].startswith('news/'), x[0]))
    return fs


def batches():
    B, cur, size = [], [], 0
    for f, n in changed():
        if cur and (size + n > LIMIT or len(cur) >= NLIMIT):
            B.append(cur); cur, size = [], 0
        cur.append(f); size += n
    if cur:
        B.append(cur)
    return B


B = batches()
arg = sys.argv[1] if len(sys.argv) > 1 else 'list'
if arg == 'list':
    for i, b in enumerate(B, 1):
        s = sum(os.path.getsize('gh/' + f) for f in b)
        print('%2d/%d  %4d枚  %.2fMB  %s … %s' % (i, len(B), len(b), s / 1048576.0, b[0], b[-1]))
    print('合計 %d枚' % sum(len(b) for b in B))
    sys.exit(0)

i = int(arg)
b = B[i - 1]
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)
for f in b:
    shutil.copyfile('gh/' + f, os.path.join(OUT, f.replace('/', '~')))
s = sum(os.path.getsize('gh/' + f) for f in b)
print('%d/%d 番目を用意しました: %d枚 %.2fMB' % (i, len(B), len(b), s / 1048576.0))
