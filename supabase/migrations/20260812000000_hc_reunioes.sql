-- Painel de Reuniões Holy Cook — estado compartilhado das ações
--
-- A ata em si (texto, projetos, lista de ações) mora no HTML da página.
-- Aqui fica só o que muda com o uso: se a ação foi feita e qual o prazo.
-- A chave `id` é o id da ação no HTML (ex.: 'ag-listas', 'cv-fabrica').
--
-- Edição aberta por decisão explícita do Fred (12/08/2026): qualquer pessoa
-- com o link lê e grava. Sem policy de DELETE — ninguém apaga linha pela página.

create table if not exists public.hc_acoes (
  id             text primary key,
  feita          boolean not null default false,
  prazo          date,
  atualizado_por text,
  atualizado_em  timestamptz not null default now()
);
alter table public.hc_acoes enable row level security;
drop policy if exists hc_acoes_select on public.hc_acoes;
create policy hc_acoes_select on public.hc_acoes
  for select using (true);
drop policy if exists hc_acoes_insert on public.hc_acoes;
create policy hc_acoes_insert on public.hc_acoes
  for insert with check (true);
drop policy if exists hc_acoes_update on public.hc_acoes;
create policy hc_acoes_update on public.hc_acoes
  for update using (true) with check (true);
-- carimba a hora a cada gravação
create or replace function public.hc_acoes_touch()
returns trigger
language plpgsql
as $$
begin
  new.atualizado_em = now();
  return new;
end;
$$;
drop trigger if exists hc_acoes_touch_trg on public.hc_acoes;
create trigger hc_acoes_touch_trg
  before insert or update on public.hc_acoes
  for each row execute function public.hc_acoes_touch();
-- realtime: a página escuta postgres_changes nesta tabela
do $$
begin
  if not exists (
    select 1 from pg_publication_tables
    where pubname = 'supabase_realtime'
      and schemaname = 'public'
      and tablename = 'hc_acoes'
  ) then
    alter publication supabase_realtime add table public.hc_acoes;
  end if;
end;
$$;
