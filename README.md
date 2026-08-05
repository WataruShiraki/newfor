# NEWFOR（newfor.jp）

大企業の新規事業を、公開情報から一件ずつ掘り起こして記録する日本語メディア。

GitHub Pages でそのまま公開しています。ビルドは不要です。
**このリポジトリの中身が、そのままサイトです。**

## 中身

```
index.html          トップ
reports/            新規事業レポート 全10本
companies/          企業データベース
about/ ads/ privacy/    運営者情報・広告について・プライバシーポリシー
assets/             ファビコン・OGP画像・投票スクリプト
CNAME               独自ドメイン（newfor.jp）
.nojekyll           GitHubの自動変換を止める（消さないでください）
supabase/schema.sql 投票テーブルの定義（Supabaseで1回実行するだけ）
```

## 更新のしかた

HTMLを直接編集して push すれば、1〜2分で反映されます。

```bash
git add . && git commit -m "更新" && git push
```

## あとで設定するもの

**投票（Supabase）** … `assets/vote.js` の先頭2行にプロジェクトURLとanonキーを入れる。
入れるまでは投票枠が出ないだけで、サイトは普通に動きます。

**アナリティクス** … 全HTMLの `G-XXXXXXXXXX` をGA4の測定IDに置換。
置換するまでは何も送信しません。

```bash
grep -rl 'G-XXXXXXXXXX' . | xargs sed -i 's/G-XXXXXXXXXX/G-あなたのID/g'
```
