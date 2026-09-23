# NEWFOR 日次ノルマ 引き継ぎ書

**新しいチャットで最初に読むファイルです。**
このファイルの手順どおりに進めれば、その日のノルマを最後まで出せます。

最終更新：2026年9月23日（記事#040 資生堂まで公開済み）

---

## 0. まず、いちばん大事なこと

### オーナー（わたるさん）との約束

これはすべての作業に効きます。ぶつかったら、こちらが勝ちます。

1. **絶対敬語。** 間違えたら、ごまかさずに謝ってください。
2. **説明は主語と名詞を明確に、手順を一つずつ、中学生がわかるレベルで。** たとえ話も入れてください。
3. **GitHubへの反映は Claude in Chrome を使って、あなた自身でやってください。** 絶対に諦めず、多面的に考えてください。
4. **日付や数字が確認できないことは、サイトにもSNSにも書かないでください。**
5. **「失敗」という言葉は使わないでください。** 「判断ミス」はあります。違う道で再チャレンジ、ということです。
6. **容量が重そうな作業の前に「これは重いけどいいですか」と一言聞いてください。**
7. **作ったら必ず自分でブラウザを開いて、上から下まで見てから報告してください。**
8. **目標は1000社。**

### 最上位のルール：KOTOBA.md

リポジトリの `KOTOBA.md` が、他のどのルールよりも上です。
**挑戦を否定する言葉を1語も書かない。** 何かを書き始める前に、必ず開いて読んでください。

書かない言葉の例：どうせ続かない／まだ生きてる／生き残った／失敗／撤退／寿命／消滅

オーナーの言葉がそのまま残っています。

> 挑戦する人は本当に偉いんだよ？
> 諦めない限り失敗じゃないんだって。

`checksite.py` がこの語を機械的に見張っていますが、**リストにない語もあります。**
一次情報の法律用語（「消滅会社」など）をそのまま写すのも違反になります。意味を変えずに言いかえてください。

---

## 1. 作業場をつくる（新しいチャットの最初の1回だけ）

新しいチャットは、まっさらなLinuxの作業場から始まります。ファイルは何も残っていません。
でも**生成プログラム一式はGitHubの中に入っている**ので、そこから戻せます。

たとえるなら、道具箱ごとクラウドに預けてあるので、新しい机に座ったら取り寄せるだけ、という状態です。

```bash
cd /home/claude
git clone https://github.com/WataruShiraki/newfor gh
cp -r gh/_src/. /home/claude/
git -C gh config user.name  "Claude"
git -C gh config user.email "noreply@anthropic.com"
npm install playwright        # png.js / og.js が使います（Chromiumは導入済み）
```

**`gh/_src/` は生成プログラムの手動コピーです。** `cp -r gh/_src/. /home/claude/` で
`build.sh` `articles/` `companies/` `KOTOBA.md` `HIKITSUGI.md` などが全部そろいます。

確認：

```bash
cd /home/claude && ls build.sh && ls articles/*.py | wc -l && ls companies/*.py | wc -l
# build.sh が見え、40 と 44 が出れば成功です（記事が増えていれば数は増えます）
```

必要な道具（たいていは最初から入っています）：
`python3` / `node` / `npm` / `git` / `pngquant`（なくても動きます） /
Python の `PIL` `bs4` `requests` `lxml` / 日本語フォント（Noto）

---

## 2. 毎日の流れ（これが「ノルマ」です）

ノルマ＝ **新規事業ヒストリーの記事を1本 ＋ ニュースを3件**。
書いて、組み立てて、点検して、GitHubへ上げて、ブラウザで見て、引き継ぎメモに書く。ここまでで1日ぶんです。

### 手順

```
① リポジトリを最新にする
② 今日の記事の会社を決める
③ 数字を一次情報で確かめる
④ 記事ファイルを書く
⑤ ニュース3件を一次情報で確かめて年表に足す
⑥ 件数のズレを直す
⑦ build.sh → checksite.py
⑧ GitHubへ分割アップロード
⑨ 差分0を確認 → 90秒待つ → ブラウザで全ページを読む
⑩ HIKITSUGI.md に今日ぶんを書いて公開
⑪ 敬語で報告（判断ミスは隠さず書く）
```

---

### ① リポジトリを最新にする（毎日必ず）

```bash
cd /home/claude/gh && git fetch -q origin main && git reset -q origin/main
git status --short --untracked-files=all | wc -l   # 0 になること
```

**`data/queue.json` は GitHub 側のほうが新しいことがよくあります。**
別の仕組みが「材料の収集」というコミットでニュース候補を足しています。
差分が出たら、手元を上書きせず **`git checkout -- data/queue.json`** で GitHub 側を採用してください。

### ② 今日の記事の会社を決める

まだ記事がない会社のうち、年表が大きいものから選びます。

```bash
cd /home/claude && python3 - <<'EOF'
import io,glob,os,re,importlib.util
rows=[]
for p in sorted(glob.glob('companies/*.py')):
    s=io.open(p,encoding='utf-8').read()
    m=re.search(r"article\s*=\s*(None|'([^']*)')", s)
    art=m.group(2) if m and m.group(2) else None
    spec=importlib.util.spec_from_file_location('c',p); mm=importlib.util.module_from_spec(spec); spec.loader.exec_module(mm)
    tl=mm.C['timeline']
    rows.append((len(tl), os.path.basename(p)[:-3], mm.C['name'], art, max(t[0] for t in tl)))
print('--- 記事なし（年表が大きい順）---')
for n,slug,nm,art,last in sorted(rows,reverse=True):
    if not art: print(f'{n:3d}  {slug:20s} {nm:14s} 最新 {last}')
print('--- 年表が古い順（ニュースを足す候補）---')
for n,slug,nm,art,last in sorted(rows,key=lambda r:r[4])[:8]:
    print(f'{last}  {slug:20s} {nm}')
EOF
```

**2026年9月23日時点で記事がない会社**：三菱電機25件、オムロン22件、三井不動産22件、キリンHD22件、東芝20件、住友商事20件、ANA20件。

角度（記事の切り口）は、**年表を読んで自分で見つけてください。** これまでの例：

- 日産 … 製品より先に「使い終わったあと」の会社を作っていた
- 富士通 … 16年で9件を次へ渡し、計算機だけを残した
- NEC … 海外を4社買い、金額が買うたびにほぼ倍
- 丸紅 … 1件27億ドルから、2年4か月で13件へ
- 資生堂 … 買った単位と、渡す単位がちがう

**数えられる事実**（何件、いくら、何年）が軸になると強い記事になります。

### ③ 数字を一次情報で確かめる（いちばん大事）

**見出しに使う数字は、必ずその会社自身の発表で原文を確認してください。**

**ニュースリリースには金額がなく、適時開示のPDFにだけ載っていることがあります。**
2026年9月22日に、資生堂の年表から4つの数字を直しました。

| 直したもの | これまで | 本人の発表 |
|---|---|---|
| ドランクエレファント | 8億4,500万ドル（約910億円） | **845百万米ドル**。円換算の記載なし |
| 3ブランド譲渡 | 7億ドル（約770億円） | **700百万米ドル**。同上 |
| パーソナルケア事業 | 1,600億円 | **記載なし**（報道のみ） |
| プロフェッショナル事業 | 123億円 | **記載なし**（報道のみ） |

**記事を書くときは、その会社の金額をひととおり適時開示で確かめ直してください。**
ほかの会社の年表にも同じ種類の数字が残っている可能性があります。

過去にこういう判断ミスがありました：

- 村田製作所の「175億円・約8,500名」→ 本人の完了リリースになく、EE Timesのみ。見出しから外した
- 任天堂の技術開発棟「121億円」→ 本人の発表は **1,210億円**。1桁ちがっていた
- 日産の「導入第1弾は広島大学」→ リリースにない一文。削除

**発表主体もよく見てください。** ソフトバンクグループ株式会社 と ソフトバンク株式会社（SBKK）は別会社です。
相手側の会社しか発表していない場合は使ってもかまいませんが、
**出典メモに「※この発表の主体は◯◯社で、当社自身のリリースは確認できていません」と必ず書いてください。**

### ④ 記事ファイルを書く

`articles/aNNN_<slug>.py` に作ります。いちばん新しい記事（いまは `a040_shiseido.py`）を
**そのまま読んで、同じ形で**書くのが確実です。

必要な項目：
`slug, no, topics, company, legal, ind, title, h1, desc, dek, forwho, kw, pub, mod, datejp, read,
kpis（4つ）, summary（3つ）, span, ticks, chart_t, chart_s, chart, tl_t, tl_s, timeline, body, memo_t, memo, sources, next`

- `topics` は10種類から2〜3個：`approval / seed / strength / partner / buildbuy / money / handoff / explain / longrun / starter`
- `body` には必ず `('chart',None)` と `('timeline',None)` を入れる
- `body` の書き方：`('p',文字列)` `('h2',文字列)` `('quote',文字列)` `('note',文字列)`
  `('term',[語, よみ, 説明])` … 3つ / `('tip',[文字列])` … リスト / `('voice',[見出し, 本文])`

**`chart` と `timeline` は手で書かず、会社ファイルから機械的に作ってください。**
`timeline` は会社ファイルのコピー、`chart` は `(ラベル, 開始年, 終了年, 継続中か)` です。
**継続中でないものには必ず終了年を入れてください**（`None` だとビルドが止まります）。

作り方の例（`aNNN_<slug>.py` に `chart=None,` `timeline=None,` と置いてから実行）：

```python
tl=sorted(m.C['timeline'], key=lambda t: t[0] if '.' in t[0] else t[0]+'.00')
cb="chart=[\n"+"\n".join(" (%r,%s,%s,%s)," % (l,s,e if e else 'None',v) for l,s,e,v in chart)+"\n],"
tb="timeline=[\n"+"\n".join(" (%r, %r, %r, %s)," % (y,ev,n,l) for y,ev,n,l in tl)+"\n],"
s=s.replace('chart=None,',cb,1).replace('timeline=None,',tb,1)
```

書けたら登録します。**2か所とも必要です。**

```python
# buildarticles.py と mkreports.py の MODS に追加
s.replace("'a040_shiseido'","'a040_shiseido','a041_xxxx'",1)
# companies/<slug>.py の article=None, を article='<slug>-newbusiness', に
```

### ⑤ ニュース3件を一次情報で確かめて年表に足す

**探し方。** `data/queue.json` に候補が入っていますが、収録44社ぶんは
発表主体が相手側の会社だけ、ということがよくあります。そのときは
**各社のニュースルームをブラウザで直接開いて見出しを拾ってください。** こちらのほうが早いです。
WebFetch は robots.txt で止まることが多いです。

```javascript
// ニュースルームを開いてから、見出しとURLを一気に取る
Array.from(document.querySelectorAll('a'))
  .map(a=>(a.innerText||'').replace(/\s+/g,' ').trim()+' :: '+a.href)
  .filter(s=>/2026/.test(s)&&s.length>35).slice(0,30)
```

**会社ファイルへの追加は、必ず行まるごと（行頭プレフィックス）をアンカーにしてください。**
2026年9月14日に、途中で切ったアンカーを使って4つの会社ファイルを壊しました。

```python
def add(path, ev_prefix, ev_new, tl_prefix, tl_new):
    lines=io.open(path,encoding='utf-8').read().split('\n')
    ev=[i for i,l in enumerate(lines) if l.startswith(ev_prefix)]
    tl=[i for i,l in enumerate(lines) if l.startswith(tl_prefix)]
    assert len(ev)==1 and len(tl)==1, (path, len(ev), len(tl))
    lines.insert(tl[-1]+1, tl_new); lines.insert(ev[-1]+1, ev_new)
    io.open(path,'w',encoding='utf-8').write('\n'.join(lines))
```

`evsrc`（出典）と `timeline`（年表）の両方に足します。
**出典メモには、発表日・金額・比率・時期を原文の表記どおりに、長めに書いてください。**
記載がないものは「記載なし」と書きます。推測で埋めないでください。

**2社にまたがる案件**（KDDI×三菱商事、JR東日本×伊藤忠など）は、
**両方の年表に1件ずつ入れ、出典は同じURL**にします。ニュースページも2本になります。

### ⑥ 件数のズレを直す

ニュースを足すと、その会社の記事に書いてある件数が合わなくなります。

```bash
grep -n "◯◯件" articles/aNNN_xxx.py
```

**昨日の学び：記事は年表のコピーを自分で持っています。**
`companies/*.py` を直しても、記事の `timeline=[...]` と `chart=[...]` は自動では直りません。
**記事側にも1行ずつ足してください。**

たとえるなら、原本を直しても、コピー機で先に刷った紙は直りません。刷った紙も回収する、が正しい手順です。

**置換するときは範囲に注意。** ホンダの記事には「29年後に型式証明」という**年数**の29が出てきます。
`29件` だけを置換し、`29年` は残してください。

**「◯◯社」は使わないでください。** 記事一覧ページに出る文の「13社」を、
`checkgen.py` が収録企業数（44社）と勘違いして止まりました。会社の数は**「件」**で統一します。

### ⑦ build.sh → checksite.py

```bash
cd /home/claude
cp articles/aNNN_*.py articles/（直した記事）.py gh/_src/articles/
cp companies/（触った会社）.py gh/_src/companies/
cp buildarticles.py mkreports.py gh/_src/
timeout 560 bash build.sh > /tmp/build.log 2>&1; echo "exit=$?"; tail -5 /tmp/build.log
python3 checksite.py
```

- **`gh/_src/` は手動コピーです。触ったファイルは毎回コピーしてください。**
- `build.sh` は2分以上かかるので `timeout 560` を必ず付けます
- `build.sh` の最後の `checkgen.py` が「生成物と生成元のズレ」を見張ります → **「ズレ: なし」**
- `checksite.py` は KOTOBA.md の語・リンク・タイトルを見ます → **「問題なし」**

どちらかが止まったら、直してからもう一度ビルドしてください。

### ⑧ GitHubへ分割アップロード

**`git push` は403で通りません。すべて Claude in Chrome から GitHub の画面で行います。**

```bash
cd /home/claude/gh
OUT=/mnt/user-data/outputs/dayMMDD && rm -rf $OUT && mkdir -p $OUT
git status --short --untracked-files=all | awk '{print $2}' > /tmp/files.txt
while read f; do
  if [ "$f" = "sitemap.xml" ]; then cp "$f" "$OUT/sitemap.xml"
  else cp "$f" "$OUT/$(echo "$f" | tr '/' '@')"; fi
done < /tmp/files.txt
```

フォルダが使えないので、`/` を `@` に置き換えて平らに並べます。
アップロード画面で、JavaScriptがファイル名を元に戻します。

**1バッチ16ファイル。sitemap.xml は最後に単独で。** 記事を1本足すと企業ページが44社ぶん
作り直されるので、160〜190ファイル・12〜13コミットになるのがふつうです。

**各バッチの手順（この順番を必ず守ってください）**

1. `https://github.com/WataruShiraki/newfor/upload/main` を開く
2. 下のJavaScriptを流し込む（**ページを移動するたびに毎回必要です**）
3. `find` でファイル入力（`ref_108` のことが多い）を探す
4. `file_upload` で16ファイル送る
5. `NFWAIT` → `NFCOMMIT('2026-MM-DD 説明 (n/N)')`
6. **`git fetch && git log` でコミットが入ったことを確認する**

```javascript
(function(){
  window.NFHOOK = function(){
    if(window.__nfhook_on) return 'already';
    window.__nfhook_on = true;
    document.addEventListener('change', function(e){
      var t = e.target;
      if(!t || t.type !== 'file' || !t.files) return;
      for(var i=0;i<t.files.length;i++){
        var f = t.files[i];
        if(f.name.indexOf('@') < 0) continue;
        var rel = f.name.split('@').join('/');
        try{ Object.defineProperty(f,'name',{value:rel,configurable:true}); }catch(err){}
      }
    }, true);
    return 'installed';
  };
  window.NFWAIT = function(paths){
    return new Promise(function(res){
      var tries = 0, stable = 0;
      var iv = setInterval(function(){
        tries++;
        var txt = document.body.innerText;
        var missing = paths.filter(function(p){ return txt.indexOf(p) < 0; });
        var prog = document.querySelectorAll('progress').length;
        var btn = Array.prototype.slice.call(document.querySelectorAll('button')).filter(function(b){ return /commit changes/i.test(b.innerText||''); })[0];
        var ready = (missing.length===0 && prog===0 && btn && !btn.disabled);
        if(ready){ stable++; } else { stable = 0; }
        if(stable >= 6){ clearInterval(iv); res({ok:true,tries:tries}); }
        else if(tries > 180){ clearInterval(iv); res({ok:false,tries:tries,missing:missing,prog:prog,btn:!!btn}); }
      }, 1000);
    });
  };
  window.NFCOMMIT = function(msg){
    if(document.body.innerText.indexOf('sitemap.xml')>=0 && msg.indexOf('sitemap')<0) return 'SITEMAP_MIXED';
    if(document.querySelectorAll('progress').length>0) return 'STILL_UPLOADING';
    var inp = document.querySelector('input[name="message"], #commit-summary-input, input[aria-label*="commit message" i]');
    if(!inp){ inp = document.querySelectorAll('input[type=text]')[0]; }
    if(!inp) return 'NO_MSG_INPUT';
    var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
    setter.call(inp, msg);
    inp.dispatchEvent(new Event('input',{bubbles:true}));
    inp.dispatchEvent(new Event('change',{bubbles:true}));
    var btn = Array.prototype.slice.call(document.querySelectorAll('button')).filter(function(b){ return /commit changes/i.test(b.innerText||'') && !b.disabled; })[0];
    if(!btn) return 'NO_BUTTON';
    btn.click();
    return 'clicked';
  };
  return window.NFHOOK();
})()
```

**`NFWAIT` の「6秒連続」は絶対に緩めないでください。**
2026年9月18日、1回でもOKなら押す作り方だったとき、ボタンは押せたのに
**GitHubが HTTP 400 を返してコミットが入りませんでした。**
「全ファイル名が出ている」「読み込み中が消えている」「Commitボタンが押せる」の3つが
**6秒続いてから**押すようにしたら、以降すべて一度で通っています。

荷物を積んだ直後に発車させていたのを、扉が閉まったことを6秒たしかめてから発車する、ようにした、ということです。

**`NFCOMMIT` の先頭にある sitemap.xml 混入チェックも残してください。**
2026年9月14日に、ほかのファイルと一緒に上げそうになったのを止めました。

### ⑨ 差分0を確認 → 90秒待つ → ブラウザで全ページを読む

```bash
cd /home/claude/gh && git fetch -q origin main && git reset -q origin/main
git status --short --untracked-files=all | wc -l          # 0 であること
git ls-tree -r --name-only origin/main | grep -c '@'      # 0 であること
sleep 95   # Vercel の反映を待つ
```

**「押したから入ったはず」は通用しません。**（2026年9月11日、15ファイルが入っていませんでした）
**「ツールが返らない＝入っていない」でもありません。**（9月16日・18日・22日、返らなかったのに入っていました）
**どちらの向きでも、判断は `git log` / `git status` でおこないます。**

そのあと、**必ず自分でブラウザを開いて、上から下まで読んでください。**

- 記事本文（/articles/<slug>/）
- ニュース3ページ（/news/YYYYMM-<slug>-1/）
- その会社の企業ページ（/companies/<slug>/）
- TOP（/）と ニュース一覧（/news/）

**公開後に読み返して見つけた判断ミスが何度もあります。** 数字の食い違い、範囲のずれ、出典にない一文。
見つけたら、その場で直して出しなおしてください。

### ⑩ HIKITSUGI.md に今日ぶんを書いて公開

`/home/claude/HIKITSUGI.md` の末尾に追記し、`gh/HIKITSUGI.md` にコピーして上げます。

書く内容：

- 出した記事（角度・確認した数字・KPI）
- ニュース3件（会社・日付・確認した中身）
- **判断ミスがあれば、隠さず、原因と直し方まで**
- 件数のズレを直した会社
- コミット一覧
- 次の担当者が困らないように気づいたこと

### ⑪ 敬語で報告

- 出したもの（リンク付き）
- **判断ミスは必ず自分から言う**
- 確認したこと（コミット数・差分0・ブラウザで読んだこと）
- 数字（収録企業数・累計件数）

---

## 3. これまでに起きた判断ミス（同じ道を通らないために）

| 日 | 何が起きたか | どう防ぐか |
|---|---|---|
| 9/11 | リポジトリURLを `offml/newfor` と間違えた | **`WataruShiraki/newfor`** です |
| 9/11 | 15ファイルが入っていないのに気づかなかった | 毎バッチ `git log` で確認 |
| 9/12 | 「撤退」と書いた | KOTOBA.md を先に読む |
| 9/12 | 継続20件／渡した12件を「同じ数」と書いた | 数えてから書く |
| 9/13 | 121億円と書いた（正しくは1,210億円） | 見出しの数字は原文確認 |
| 9/14 | 途中で切ったアンカーで会社ファイルを4つ壊した | **行まるごとをアンカーに** |
| 9/14 | sitemap.xml を他と混ぜそうになった | `NFCOMMIT` の混入チェック |
| 9/15 | 報道のみの数字を見出しに使いかけた | 本人の発表だけ |
| 9/16 | 「寿命」と書いた | KOTOBA.md |
| 9/17 | 会社ファイルを直したが記事のコピーが古いまま公開 | **記事の timeline / chart も直す** |
| 9/18 | 「消滅会社」と法律用語をそのまま写した | 一次情報の言葉でも言いかえる |
| 9/18 | HTTP 400 でコミットが入らなかった | **NFWAIT の6秒連続** |
| 9/20 | 「13社」と書いて checkgen が止まった | 会社の数は**「件」** |
| 9/20 | 数えた範囲と例に挙げた範囲がずれていた | 公開後に自分で読み返す |
| 9/22 | 報道の数字が4つ年表に残っていた | **適時開示のPDFまで開く** |

---

## 4. いまの状態（2026年9月23日）

- 収録企業 **44社** ／ 年表 **1,303件** ／ 記事 **40本**（最新 #040 資生堂）
- リポジトリ：`https://github.com/WataruShiraki/newfor`（Vercelが自動で公開します）
- サイト：`https://newfor.jp`

### 記事がまだない会社（年表の大きい順）

三菱電機25、オムロン22、三井不動産22、キリンHD22、東芝20、住友商事20、ANA20

### 積み残している仕事

1. **広告の入れ替え**（オーナーから「広告はあとでやる」と言われています）
   いまは起業・個人事業主向け（開業届、青色申告、バーチャルオフィス、確定申告、フジ子さん）。
   読者は新規事業担当者なので、経営企画・ハイクラス転職に寄せる方針で合意済み。
2. `/news/` 約1,300件のタイトルを検索語に寄せる（未着手）
3. 先人の記録72件のタイトル改稿（未着手）
4. SNSの実投稿（下書きとカード画像28枚あり、アカウント未確定）
5. GA4で `shindan_complete` をキーイベント指定（オーナーの操作が必要）
6. 用語を増やす（PoC、フィージビリティ、事業計画、撤退基準など）
7. **ほかの会社の年表に残っている「報道だけの数字」の洗い直し**（9/22に資生堂で4件見つかりました）

---

## 5. 困ったとき

- **ブラウザ拡張が切れた** … 少し待ってやり直す。何度も失敗するならオーナーに確認をお願いする
- **build.sh が止まる** … `/tmp/build.log` の最後を見る。チャートの終了年が `None` なことが多い
- **checkgen が止まる** … 記事の件数表記と実際の年表がずれている。あるいは「◯◯社」と書いている
- **checksite が止まる** … KOTOBA.md にふれる語がある。言いかえる
- **ディスクがいっぱい** … `dist/` や `node_modules` を消して作り直す

---

## 6. くわしい経緯を知りたいとき

リポジトリの **`HIKITSUGI.md`** に、日ごとの記録が全部入っています（1,300行以上）。
「なぜこう書いているのか」で迷ったら、そこを検索してください。
