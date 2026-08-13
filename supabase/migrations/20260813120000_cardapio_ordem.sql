-- Cardápio de Projetos — ordem e seção de cada card
--
-- Os cards em si moram no HTML da página (nome, descrição, link, cor).
-- Aqui fica só o arranjo: em que seção cada card está e em que posição.
--
-- Uma linha só, id = 'projetos'. O formato de `layout` é:
--   { "<slug-da-seção>": ["<id-do-card>", "<id-do-card>", ...] }
-- Card que não aparece no layout fica onde o HTML o colocou, no fim da seção.
-- Assim, quando um card novo nasce no HTML, ele aparece sem precisar mexer aqui.
--
-- Edição aberta, mesmo critério já adotado em hc_acoes (12/08/2026):
-- qualquer pessoa com o link lê e grava. Sem policy de DELETE.

create table if not exists public.hc_cardapio_ordem (
  id            text primary key,
  layout        jsonb       not null default '{}'::jsonb,
  atualizado_em timestamptz not null default now()
);

alter table public.hc_cardapio_ordem enable row level security;

drop policy if exists hc_cardapio_ordem_select on public.hc_cardapio_ordem;
create policy hc_cardapio_ordem_select on public.hc_cardapio_ordem
  for select using (true);

drop policy if exists hc_cardapio_ordem_insert on public.hc_cardapio_ordem;
create policy hc_cardapio_ordem_insert on public.hc_cardapio_ordem
  for insert with check (true);

drop policy if exists hc_cardapio_ordem_update on public.hc_cardapio_ordem;
create policy hc_cardapio_ordem_update on public.hc_cardapio_ordem
  for update using (true) with check (true);

-- carimba a hora a cada gravação
create or replace function public.hc_cardapio_ordem_touch()
returns trigger
language plpgsql
as $$
begin
  new.atualizado_em = now();
  return new;
end;
$$;

drop trigger if exists hc_cardapio_ordem_touch_trg on public.hc_cardapio_ordem;
create trigger hc_cardapio_ordem_touch_trg
  before insert or update on public.hc_cardapio_ordem
  for each row execute function public.hc_cardapio_ordem_touch();
