-- ============================================================
-- NEWFOR ピックアップ（ヘッダー下を流れる、直近の投票）
--
-- Supabase の SQL Editor に貼って、1回だけ実行してください。
-- schema.sql を実行済みであることが前提です。
--
-- newfor_votes は「書き込みだけ許可・読み出し禁止」にしてあります。
-- 生ログをそのまま外に出さないため、ここでは
--   ・3日ぶんに絞る
--   ・1時間単位に丸める
--   ・同じ内容はまとめて件数だけ返す
-- という形のビューを作り、そのビューだけを anon に読ませます。
-- voter_hash は一切出しません。
-- ============================================================

create or replace view public.newfor_recent_votes
with (security_invoker = false) as
select
  date_trunc('hour', v.created_at)      as at,
  v.poll_id                             as poll_id,
  p.kind                                as kind,
  p.question                            as question,
  o.label                               as label,
  o.emoji                               as emoji,
  count(*)                              as votes
from public.newfor_votes v
join public.newfor_polls p        on p.id = v.poll_id
join public.newfor_poll_options o on o.poll_id = v.poll_id and o.key = v.option_key
where v.created_at > now() - interval '3 days'
group by 1, 2, 3, 4, 5, 6
order by 1 desc;

grant select on public.newfor_recent_votes to anon;
grant select on public.newfor_recent_votes to authenticated;
