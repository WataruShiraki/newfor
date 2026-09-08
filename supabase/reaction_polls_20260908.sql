-- ============================================================
-- NEWFOR 記事の「読者の反応」投票を、まだ受け皿の無い16記事に足します
-- 2026-09-08 作成
--
-- これは何か
--   記事の下にある「READERS' VOICE」は、Supabase に問いと選択肢が
--   入っている記事だけ中身が出ます。入っていない記事は、見出しだけの
--   空っぽの箱になります。いま12記事にしか入っていないので、
--   残り16記事ぶんをここで足します。
--
-- 使い方
--   Supabase の SQL Editor にこのまま貼って、Run を押すだけです。
--   何度実行しても増えません（on conflict do nothing）。
-- ============================================================

insert into public.newfor_polls (id, question, kind) values
  ('reaction-canon-newbusiness', 'この記録を読んで、いちばん近い気持ちはどれですか', 'reaction'),
  ('reaction-dena-newbusiness', 'この記録を読んで、いちばん近い気持ちはどれですか', 'reaction'),
  ('reaction-denso-newbusiness', 'この記録を読んで、いちばん近い気持ちはどれですか', 'reaction'),
  ('reaction-fastretailing-newbusiness', 'この記録を読んで、いちばん近い気持ちはどれですか', 'reaction'),
  ('reaction-komatsu-newbusiness', 'この記録を読んで、いちばん近い気持ちはどれですか', 'reaction'),
  ('reaction-lycorp-newbusiness', 'この記録を読んで、いちばん近い気持ちはどれですか', 'reaction'),
  ('reaction-mercari-newbusiness', 'この記録を読んで、いちばん近い気持ちはどれですか', 'reaction'),
  ('reaction-mhi-newbusiness', 'この記録を読んで、いちばん近い気持ちはどれですか', 'reaction'),
  ('reaction-mitsui-newbusiness', 'この記録を読んで、いちばん近い気持ちはどれですか', 'reaction'),
  ('reaction-mufg-newbusiness', 'この記録を読んで、いちばん近い気持ちはどれですか', 'reaction'),
  ('reaction-persol-newbusiness', 'この記録を読んで、いちばん近い気持ちはどれですか', 'reaction'),
  ('reaction-rakuten-newbusiness', 'この記録を読んで、いちばん近い気持ちはどれですか', 'reaction'),
  ('reaction-takeda-newbusiness', 'この記録を読んで、いちばん近い気持ちはどれですか', 'reaction'),
  ('reaction-newbusiness-money-ranking', 'この記録を読んで、いちばん近い気持ちはどれですか', 'reaction'),
  ('reaction-newbusiness-partners', 'この記録を読んで、いちばん近い気持ちはどれですか', 'reaction'),
  ('reaction-newbusiness-words', 'この記録を読んで、いちばん近い気持ちはどれですか', 'reaction')
on conflict (id) do nothing;

insert into public.newfor_poll_options (poll_id, key, label, emoji, sort) values
  ('reaction-canon-newbusiness','hot','胸があつくなった',NULL,1),
  ('reaction-canon-newbusiness','great','自分の会社にも当てはまる',NULL,2),
  ('reaction-canon-newbusiness','expect','これからのキヤノンに期待したい',NULL,3),
  ('reaction-canon-newbusiness','join','自分もこういう事業に関わってみたい',NULL,4),
  ('reaction-dena-newbusiness','hot','胸があつくなった',NULL,1),
  ('reaction-dena-newbusiness','great','自分の会社にも当てはまる',NULL,2),
  ('reaction-dena-newbusiness','expect','これからのDeNAに期待したい',NULL,3),
  ('reaction-dena-newbusiness','join','自分もこういう事業に関わってみたい',NULL,4),
  ('reaction-denso-newbusiness','hot','胸があつくなった',NULL,1),
  ('reaction-denso-newbusiness','great','自分の会社にも当てはまる',NULL,2),
  ('reaction-denso-newbusiness','expect','これからのデンソーに期待したい',NULL,3),
  ('reaction-denso-newbusiness','join','自分もこういう事業に関わってみたい',NULL,4),
  ('reaction-fastretailing-newbusiness','hot','胸があつくなった',NULL,1),
  ('reaction-fastretailing-newbusiness','great','自分の会社にも当てはまる',NULL,2),
  ('reaction-fastretailing-newbusiness','expect','これからのファーストリテイリングに期待したい',NULL,3),
  ('reaction-fastretailing-newbusiness','join','自分もこういう事業に関わってみたい',NULL,4),
  ('reaction-komatsu-newbusiness','hot','胸があつくなった',NULL,1),
  ('reaction-komatsu-newbusiness','great','自分の会社にも当てはまる',NULL,2),
  ('reaction-komatsu-newbusiness','expect','これからのコマツに期待したい',NULL,3),
  ('reaction-komatsu-newbusiness','join','自分もこういう事業に関わってみたい',NULL,4),
  ('reaction-lycorp-newbusiness','hot','胸があつくなった',NULL,1),
  ('reaction-lycorp-newbusiness','great','自分の会社にも当てはまる',NULL,2),
  ('reaction-lycorp-newbusiness','expect','これからのLINEヤフーに期待したい',NULL,3),
  ('reaction-lycorp-newbusiness','join','自分もこういう事業に関わってみたい',NULL,4),
  ('reaction-mercari-newbusiness','hot','胸があつくなった',NULL,1),
  ('reaction-mercari-newbusiness','great','自分の会社にも当てはまる',NULL,2),
  ('reaction-mercari-newbusiness','expect','これからのメルカリに期待したい',NULL,3),
  ('reaction-mercari-newbusiness','join','自分もこういう事業に関わってみたい',NULL,4),
  ('reaction-mhi-newbusiness','hot','胸があつくなった',NULL,1),
  ('reaction-mhi-newbusiness','great','自分の会社にも当てはまる',NULL,2),
  ('reaction-mhi-newbusiness','expect','これからの三菱重工業に期待したい',NULL,3),
  ('reaction-mhi-newbusiness','join','自分もこういう事業に関わってみたい',NULL,4),
  ('reaction-mitsui-newbusiness','hot','胸があつくなった',NULL,1),
  ('reaction-mitsui-newbusiness','great','自分の会社にも当てはまる',NULL,2),
  ('reaction-mitsui-newbusiness','expect','これからの三井物産に期待したい',NULL,3),
  ('reaction-mitsui-newbusiness','join','自分もこういう事業に関わってみたい',NULL,4),
  ('reaction-mufg-newbusiness','hot','胸があつくなった',NULL,1),
  ('reaction-mufg-newbusiness','great','自分の会社にも当てはまる',NULL,2),
  ('reaction-mufg-newbusiness','expect','これからの三菱UFJフィナンシャル・グループに期待したい',NULL,3),
  ('reaction-mufg-newbusiness','join','自分もこういう事業に関わってみたい',NULL,4),
  ('reaction-persol-newbusiness','hot','胸があつくなった',NULL,1),
  ('reaction-persol-newbusiness','great','自分の会社にも当てはまる',NULL,2),
  ('reaction-persol-newbusiness','expect','これからのパーソルホールディングスに期待したい',NULL,3),
  ('reaction-persol-newbusiness','join','自分もこういう事業に関わってみたい',NULL,4),
  ('reaction-rakuten-newbusiness','hot','胸があつくなった',NULL,1),
  ('reaction-rakuten-newbusiness','great','自分の会社にも当てはまる',NULL,2),
  ('reaction-rakuten-newbusiness','expect','これからの楽天グループに期待したい',NULL,3),
  ('reaction-rakuten-newbusiness','join','自分もこういう事業に関わってみたい',NULL,4),
  ('reaction-takeda-newbusiness','hot','胸があつくなった',NULL,1),
  ('reaction-takeda-newbusiness','great','自分の会社にも当てはまる',NULL,2),
  ('reaction-takeda-newbusiness','expect','これからの武田薬品工業に期待したい',NULL,3),
  ('reaction-takeda-newbusiness','join','自分もこういう事業に関わってみたい',NULL,4),
  ('reaction-newbusiness-money-ranking','hot','胸があつくなった',NULL,1),
  ('reaction-newbusiness-money-ranking','great','自分の会社にも当てはまる',NULL,2),
  ('reaction-newbusiness-money-ranking','expect','これからの新規事業の金額の使われ方に注目したい',NULL,3),
  ('reaction-newbusiness-money-ranking','join','自分もこういう事業に関わってみたい',NULL,4),
  ('reaction-newbusiness-partners','hot','胸があつくなった',NULL,1),
  ('reaction-newbusiness-partners','great','自分の会社にも当てはまる',NULL,2),
  ('reaction-newbusiness-partners','expect','これからの提携のかたちに注目したい',NULL,3),
  ('reaction-newbusiness-partners','join','自分もこういう事業に関わってみたい',NULL,4),
  ('reaction-newbusiness-words','hot','胸があつくなった',NULL,1),
  ('reaction-newbusiness-words','great','自分の会社にも当てはまる',NULL,2),
  ('reaction-newbusiness-words','expect','これからの新規事業の言葉に注目したい',NULL,3),
  ('reaction-newbusiness-words','join','自分もこういう事業に関わってみたい',NULL,4)
on conflict (poll_id, key) do nothing;
