# -*- coding: utf-8 -*-
"""投稿の下書きを、SNS文体ルールに合っているか機械で点検する

_src/SNS_BUNTAI.md の5つのルールのうち、機械で見られるところだけを見ます。
書き味やフックの強さは人が見るしかないので、ここでは扱いません。

使い方: python3 checkposts.py posts/first_posts.md
"""
import io,re,sys

# 接続詞の直後の読点は禁止
CONJ=['しかし','ただし','そして','また','さらに','だから','なので','つまり',
      'ところが','けれども','したがって','よって','一方','ちなみに','むしろ']
# 消す副詞
ADV=['まさに','やはり','とても','非常に','しっかり','きちんと','まさしく','ぜひ',
     'かなり','非常','しっかりと']
# 定型句
CLICHE=['はじめに','結論から言うと','いかがでしたか','まとめると','ぜひ参考に',
        'することができます','と思われるかもしれません','と言えるでしょう',
        'ではないでしょうか','人それぞれ']
# サイトの言葉づかい
NEG=['失敗','撤退','寿命','消滅','敗北','惨敗','倒れた']

def cells(t):
    """表の行は、セルごとに1文として見る"""
    return [c.strip() for c in t.strip().strip('|').split('|')]

def sentences(text):
    out=[]
    for ln in text.split('\n'):
        s=ln.strip()
        if not s or s.startswith('#') or s.startswith('>') or s.startswith('```'): continue
        if s.startswith('|'):
            for c in cells(s):
                if c and not set(c)<=set('-: '): out.append(c)
            continue
        s=re.sub(r'^[-*\d.]+\s*','',s)
        for x in re.split(r'(?<=[。？！])',s):
            x=x.strip()
            if x: out.append(x)
    return out

def wlen(t):
    """全角2・半角1ではなく、ここは「文字数」で数える（40字ルールのため）"""
    return len(re.sub(r'https?://\S+','',t))

def check(path):
    t=io.open(path,encoding='utf-8').read()
    ss=sentences(t)
    ng=[]
    long_=[s for s in ss if wlen(s)>40]
    for s in long_: ng.append(('40字超（%d字）'%wlen(s),s))
    for s in ss:
        for c in CONJ:
            if re.search(r'(^|[。\s])%s、'%c,s): ng.append(('接続詞の直後の読点「%s、」'%c,s))
        for a in ADV:
            if a in s: ng.append(('不要な副詞「%s」'%a,s))
        for c in CLICHE:
            if c in s: ng.append(('定型句・逃げ表現「%s」'%c,s))
        for n in NEG:
            if n in s: ng.append(('否定的な言葉「%s」'%n,s))
    # 体言止めの割合（。で終わり、直前が漢字かカタカナ）
    tai=sum(1 for s in ss if re.search(r'[ぁ-んァ-ヶ一-龥ー0-9]。$',s)
            and not re.search(r'(です|ます|ました|でした|ません|ない|た|る|う|い)。$',s))
    print('文の数 %d / 体言止め %d（%.0f%%）'%(len(ss),tai,100.0*tai/max(1,len(ss))))
    if ng:
        print('\n直すところ %d 件'%len(ng))
        for why,s in ng: print('  ×',why,'…',s[:60])
    else:
        print('\n機械で見られる範囲では、直すところはありません。')
    return len(ng)

if __name__=='__main__':
    sys.exit(1 if check(sys.argv[1]) else 0)
