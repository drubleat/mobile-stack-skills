-- Apply as a migration owner. Only the trusted server may consume quota.
create table if not exists public.usage_counters (
  user_id uuid not null references auth.users(id) on delete cascade,
  day date not null,
  ai_calls integer not null default 0 check (ai_calls >= 0),
  primary key (user_id, day)
);
alter table public.usage_counters enable row level security;
revoke all on table public.usage_counters from anon, authenticated;

create or replace function public.increment_ai_usage(p_user_id uuid, p_limit integer)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare
  current_count integer;
  quota_day date := (now() at time zone 'UTC')::date;
begin
  if p_user_id is null or p_limit is null or p_limit < 1 then
    raise exception 'Invalid quota arguments' using errcode = '22023';
  end if;
  insert into public.usage_counters as counters (user_id, day, ai_calls)
  values (p_user_id, quota_day, 1)
  on conflict (user_id, day) do update
    set ai_calls = counters.ai_calls + 1
    where counters.ai_calls < p_limit
  returning ai_calls into current_count;
  return jsonb_build_object('over_limit', current_count is null, 'count', current_count);
end;
$$;
revoke all on function public.increment_ai_usage(uuid, integer) from public, anon, authenticated;
grant execute on function public.increment_ai_usage(uuid, integer) to service_role;
