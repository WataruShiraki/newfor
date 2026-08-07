-- ============================================================
-- NEWFOR 訂正・補足の受付窓口
--
-- Supabase の SQL Editor に貼って、1回だけ実行してください。
-- schema.sql と同じ考え方です。書けるけれど、読めません。
--
-- なぜ「読めない」ようにするのか
--   このテーブルには、記録された会社の方が送ってくださる内容が入ります。
--   公開前の情報や、担当者のお名前が入ることがあります。
--   anon（ブラウザから見える鍵）では1文字も読み出せない形にしておきます。
--   中身を見るときは Supabase の管理画面か、service_role の鍵を使ってください。
-- ============================================================

create table if not exists public.newfor_reports (
  id          bigserial primary key,

  -- どのページから送られたか
  page_url    text not null,
  page_kind   text not null default 'company',   -- company / news / article
  target      text,                              -- 企業slug、NEWSのslug など

  -- 中身
  kind        text not null default 'correction',-- correction 内容が違う /
                                                 -- missing    この事業が抜けている /
                                                 -- supplement その後を知っている
  body        text not null,
  source_url  text,                              -- 一次情報のURL。あると反映が早い
  contact     text,                              -- 任意。返信が要るときだけ

  -- 運用
  status      text not null default 'new',       -- new / reading / done / kept
  memo        text,                              -- こちらの覚え書き
  created_at  timestamptz not null default now(),

  -- 長さの上限。いたずらで巨大なデータを入れられないようにする
  constraint newfor_reports_body_len    check (char_length(body) between 5 and 4000),
  constraint newfor_reports_src_len     check (source_url is null or char_length(source_url) <= 600),
  constraint newfor_reports_contact_len check (contact is null or char_length(contact) <= 200),
  constraint newfor_reports_kind_ok     check (kind in ('correction','missing','supplement'))
);

create index if not exists newfor_reports_status_idx on public.newfor_reports (status, created_at desc);
create index if not exists newfor_reports_target_idx on public.newfor_reports (target);

-- ============================================================
-- Row Level Security：送れるけれど、読めない
-- ============================================================
alter table public.newfor_reports enable row level security;

drop policy if exists "anyone can report" on public.newfor_reports;

-- 誰でも送れる（INSERT）
create policy "anyone can report" on public.newfor_reports for insert with check (true);

-- SELECT のポリシーは作りません。作らない＝anon からは読めません。

-- ============================================================
-- 受け取る関数（idを返さない。送れたかどうかだけ返す）
-- ============================================================
create or replace function public.newfor_send_report(
  p_page_url   text,
  p_page_kind  text,
  p_target     text,
  p_kind       text,
  p_body       text,
  p_source_url text,
  p_contact    text
) returns boolean
language plpgsql
security definer
set search_path = public
as $$
begin
  if p_body is null or char_length(btrim(p_body)) < 5 then
    return false;
  end if;

  insert into public.newfor_reports
    (page_url, page_kind, target, kind, body, source_url, contact)
  values
    (left(coalesce(p_page_url,''), 500),
     case when p_page_kind in ('company','news','article') then p_page_kind else 'company' end,
     left(coalesce(p_target,''), 120),
     case when p_kind in ('correction','missing','supplement') then p_kind else 'correction' end,
     left(btrim(p_body), 4000),
     nullif(left(coalesce(p_source_url,''), 600), ''),
     nullif(left(coalesce(p_contact,''), 200), ''));

  return true;
end;
$$;

grant execute on function public.newfor_send_report(text,text,text,text,text,text,text) to anon, authenticated;

-- ============================================================
-- 届いたものを見るとき（Supabase の SQL Editor で実行）
-- ============================================================
-- select created_at, page_kind, target, kind, left(body,120) as body, source_url, contact
-- from public.newfor_reports
-- where status = 'new'
-- order by created_at desc;
--
-- 読み終えたら： update public.newfor_reports set status='done' where id = 123;
