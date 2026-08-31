# -*- coding: utf-8 -*-
"""
中身が同じOGP画像を、毎回作り直さないようにするための後始末です。

なぜ必要か（2026年8月30日に原因を突き止めました）
──────────────────────────────────────
2026年8月29日、ビルドのたびに157枚のOGP画像が「変わった」と出て、
コミットが12回ぶんに膨らんでいました。調べた結果はこうです。

  ・og.js を2回続けて動かす → 出てくる画像は完全に同じ（ズレなし）
  ・pngquant を2回動かす   → こちらも完全に同じ（ズレなし）
  ・それでも「公開中の画像」と「いま作った画像」は違う

つまり、いまの作り方がブレているのではなく、**公開中の画像のほうが
昔の作り方で作られていた**、ということでした。絵は同じに見えますが、
中のバイト列だけが違います。

そこで2026年8月30日に、153枚をいまの作り方で作り直して一度だけ上げました。
これで土台がそろったので、明日からは差分が出なくなります。

このファイルが残っている理由
────────────────────────
土台がそろったあとも、念のための見張りとして置いておきます。
gh/assets/ の og-*.png のうち git が「変わった」と言っているものについて、
公開中のもの（HEAD）と画素を1つずつ比べ、**絵が同じなら公開中のものへ戻します。**

たとえ話
────────
同じ文章を毎日きれいに清書し直しているようなものです。
中身が1文字も変わっていないなら、清書し直したほうを捨てて、
きのうの紙をそのまま使えばいい。差し替えるのは、中身が変わったページだけです。
"""
import hashlib
import io
import os
import subprocess
import sys

from PIL import Image

GH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gh')


def sh(args):
    return subprocess.run(args, cwd=GH, capture_output=True, text=True)


def pixels(data_or_path):
    """PNGを開いて、画素の並びだけのハッシュを返します（メタ情報や圧縮の違いを無視するため）。"""
    if isinstance(data_or_path, bytes):
        im = Image.open(io.BytesIO(data_or_path))
    else:
        im = Image.open(data_or_path)
    im = im.convert('RGBA')
    return im.size, hashlib.md5(im.tobytes()).hexdigest()


def main():
    if not os.path.isdir(os.path.join(GH, '.git')):
        print('pngkeep: gh/ がgitの管理下にありません。何もしません。')
        return

    st = sh(['git', 'status', '--porcelain', '--', 'assets'])
    targets = []
    for line in st.stdout.splitlines():
        if len(line) < 4:
            continue
        code, path = line[:2], line[3:].strip()
        if code.strip() != 'M':
            continue          # 新しく増えた画像は、そのまま残します
        if not path.endswith('.png'):
            continue
        targets.append(path)

    if not targets:
        print('OGP画像の作り直し: 差分なし')
        return

    kept = 0
    for path in targets:
        show = subprocess.run(['git', 'show', 'HEAD:' + path],
                              cwd=GH, capture_output=True)
        if show.returncode != 0:
            continue
        try:
            old = pixels(show.stdout)
            new = pixels(os.path.join(GH, path))
        except Exception:
            continue          # 読めないものは触りません
        if old == new:
            sh(['git', 'checkout', '--', path])
            kept += 1

    print('OGP画像の作り直し: %d枚のうち %d枚は絵が同じだったので、公開中のものに戻しました（差し替えるのは %d枚）'
          % (len(targets), kept, len(targets) - kept))


if __name__ == '__main__':
    main()
