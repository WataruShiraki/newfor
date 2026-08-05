-- ============================================================
-- NEWFOR 投票テーブル
-- Supabase の SQL Editor に貼って、1回実行するだけです。
-- ============================================================

-- 投票の対象（今週の投票、歴史上いちばんの新規事業、など）
create table if not exists public.polls (
  id          text primary key,              -- 例: 'weekly-2026-08-05'
  question    text not null,
  kind        text not null default 'weekly', -- weekly / alltime / expectation
  opens_at    timestamptz not null default now(),
  closes_at   timestamptz,
  created_at  timestamptz not null default now()
);

-- 選択肢
create table if not exists public.poll_options (
  id          bigserial primary key,
  poll_id     text not null references public.polls(id) on delete cascade,
  key         text not null,                 -- 例: 'a' / 'b' / 'fujifilm'
  label       text not null,
  emoji       text,
  sort        int not null default 0,
  unique (poll_id, key)
);

-- 1票ずつの記録（誰が入れたかは持たない）
create table if not exists public.votes (
  id          bigserial primary key,
  poll_id     text not null references public.polls(id) on delete cascade,
  option_key  text not null,
  voter_hash  text not null,                 -- IPとUAのハッシュ。個人は特定しない
  created_at  timestamptz not null default now(),
  unique (poll_id, voter_hash)               -- 同じ端末からの二重投票を防ぐ
);

create index if not exists votes_poll_idx on public.votes (poll_id, option_key);

-- 集計だけを返すビュー（生データは外に出さない）
create or replace view public.poll_results as
select
  p.id            as poll_id,
  p.question,
  o.key           as option_key,
  o.label,
  o.emoji,
  o.sort,
  count(v.id)     as votes,
  round(100.0 * count(v.id) / nullif(sum(count(v.id)) over (partition by p.id), 0), 1) as pct
from public.polls p
join public.poll_options o on o.poll_id = p.id
left join public.votes v on v.poll_id = p.id and v.option_key = o.key
group by p.id, p.question, o.key, o.label, o.emoji, o.sort;

-- ============================================================
-- Row Level Security：読むのは誰でも、書くのは投票のみ
-- ============================================================
alter table public.polls        enable row level security;
alter table public.poll_options enable row level security;
alter table public.votes        enable row level security;

drop policy if exists "polls are readable"   on public.polls;
drop policy if exists "options are readable" on public.poll_options;
drop policy if exists "anyone can vote"      on public.votes;
drop policy if exists "votes are not readable" on public.votes;

create policy "polls are readable"   on public.polls        for select using (true);
create policy "options are readable" on public.poll_options for select using (true);

-- 投票（INSERT）は誰でもできる。ただし読み出しはできない＝生ログは守られる
create policy "anyone can vote" on public.votes for insert with check (true);

-- ============================================================
-- 投票を受け付ける関数（重複は静かに無視して、結果を返す）
-- ============================================================
create or replace function public.cast_vote(
  p_poll_id text,
  p_option_key text,
  p_voter_hash text
) returns table (option_key text, label text, emoji text, votes bigint, pct numeric)
language plpgsql
security definer
set search_path = public
as $$
begin
  -- 締切を過ぎた投票は受け付けない
  if exists (select 1 from polls where id = p_poll_id and closes_at is not null and closes_at < now()) then
    raise exception 'poll closed';
  end if;

  insert into votes (poll_id, option_key, voter_hash)
  values (p_poll_id, p_option_key, p_voter_hash)
  on conflict (poll_id, voter_hash) do nothing;

  return query
    select r.option_key, r.label, r.emoji, r.votes, r.pct
    from poll_results r
    where r.poll_id = p_poll_id
    order by r.sort;
end;
$$;

grant execute on function public.cast_vote(text, text, text) to anon;

-- ============================================================
-- 初期データの例（今週の投票）
-- ============================================================
insert into public.polls (id, question, kind, closes_at) values
  ('weekly-2026-08-05', 'ドコモが2026年夏に出すAIエージェント「SyncMe」。あなたの期待度は？', 'weekly', now() + interval '7 days')
on conflict (id) do nothing;

insert into public.poll_options (poll_id, key, label, emoji, sort) values
  ('weekly-2026-08-05', 'a', 'めちゃくちゃ期待！', '🚀', 1),
  ('weekly-2026-08-05', 'b', '今は様子見！',       '👀', 2)
on conflict (poll_id, key) do nothing;

-- 歴史上いちばんすごい新規事業（Wave 1 の企画）
insert into public.polls (id, question, kind) values
  ('alltime-greatest', '歴史上、いちばんすごいと思う新規事業は？', 'alltime')
on conflict (id) do nothing;

insert into public.poll_options (poll_id, key, label, emoji, sort) values
  ('alltime-greatest','fujifilm','富士フイルム ─ 写真フィルムから化粧品・医薬へ','🧴',1),
  ('alltime-greatest','toyota',  '豊田自動織機 ─ 織機から自動車へ','🚗',2),
  ('alltime-greatest','paypay',  'ソフトバンク ─ PayPayの100億円キャンペーン','💸',3),
  ('alltime-greatest','nintendo','任天堂 ─ 花札からゲーム機へ','🎮',4),
  ('alltime-greatest','sony',    'ソニー ─ ウォークマン','🎧',5),
  ('alltime-greatest','docomo',  'NTTドコモ ─ iモード','📱',6),
  ('alltime-greatest','seven',   'セブン-イレブン ─ おにぎりとATM','🍙',7),
  ('alltime-greatest','recruit', 'リクルート ─ Indeedの買収','🔍',8),
  ('alltime-greatest','yamato',  'ヤマト運輸 ─ 宅急便','📦',9),
  ('alltime-greatest','kddi',    'KDDI ─ auじぶん銀行','🏦',10)
on conflict (poll_id, key) do nothing;
